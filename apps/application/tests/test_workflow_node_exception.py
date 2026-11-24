import threading
import time
from unittest.mock import patch

from django.test import SimpleTestCase

import application.workflow.nodes as workflow_nodes
from application.workflow.common import WorkflowType, new_instance
from application.workflow.i_node import INode
from application.workflow.status import Status
from application.workflow.workflow_manage import CallBack, WorkflowManage
from knowledge.models.knowledge_action import State
from trigger.handler.impl.task.application_task import get_workflow_state


class _OkNode(INode):
    type = "test-ok-node"

    def execute(self):
        pass


class _SlowNode(INode):
    type = "test-slow-node"

    def execute(self):
        time.sleep(0.3)


class _FailingNode(INode):
    type = "test-failing-node"

    def execute(self):
        raise ValueError("boom")


_TEST_NODES = {cls.type: cls for cls in (_OkNode, _SlowNode, _FailingNode)}
_real_get_node_class = workflow_nodes.get_node_class


def _get_node_class(node_type, workflow_type):
    return _TEST_NODES.get(node_type) or _real_get_node_class(node_type, workflow_type)


def _node(node_id, node_type, node_data=None, **properties):
    return {
        "id": node_id,
        "type": node_type,
        "x": 0,
        "y": 0,
        "properties": {"stepName": node_id, "node_data": node_data or {}, **properties},
    }


def _edge(source, target, anchor="right"):
    return {
        "id": f"{source}-{target}",
        "type": "app-edge",
        "sourceNodeId": source,
        "targetNodeId": target,
        "sourceAnchorId": f"{source}_{anchor}",
        "targetAnchorId": f"{target}_left",
    }


def _exception_edge(source, target):
    return _edge(source, target, "exception_right")


def _run(nodes, edges, start_node_id):
    workflow = new_instance({"nodes": nodes, "edges": edges})
    finished = threading.Event()
    errors = []

    def on_complete(_manage, error):
        errors.append(error)
        finished.set()

    def get_start_node(wf, manage):
        node = wf.get_node(start_node_id)
        return _get_node_class(node.type, WorkflowType.APPLICATION)(
            node, manage, lambda n: n.properties.get("node_data", {})
        )

    with patch.object(workflow_nodes, "get_node_class", _get_node_class):
        manage = WorkflowManage(
            workflow, {}, WorkflowType.APPLICATION, CallBack(lambda *_: None, on_complete), get_start_node
        )
        manage.run()
        assert finished.wait(10), "workflow did not finish"
    return manage, [str(e) if e else e for e in errors]


class NodeExceptionBranchTests(SimpleTestCase):
    def test_exception_branch_receives_exception_message_and_run_is_not_a_failure(self):
        assign = _node(
            "assign",
            "variable-assign-node",
            {
                "variable_list": [
                    {
                        "name": "global.err",
                        "fields": ["global", "err"],
                        "source": "custom",
                        "type": "string",
                        "value": "{{fail.exception_message}}",
                    }
                ]
            },
        )
        nodes = [_node("fail", _FailingNode.type, enableException=True), assign]

        manage, errors = _run(nodes, [_exception_edge("fail", "assign")], "fail")

        self.assertEqual(errors, [None])
        self.assertEqual(manage.get_context("fail", "exception_message"), "boom")
        self.assertEqual(manage.context["global"], {"err": "boom"})
        details = manage.get_details()
        fail_detail = next(d for d in details if d["node_id"] == "fail")
        self.assertEqual(fail_detail["status"], Status.FAIL.value)
        self.assertTrue(fail_detail["enableException"])
        self.assertEqual(fail_detail["err_message"], "boom")
        self.assertEqual(get_workflow_state(details), State.SUCCESS)

    def test_failure_without_exception_handling_still_fails_the_run(self):
        manage, errors = _run([_node("fail", _FailingNode.type)], [], "fail")

        self.assertEqual(errors, ["boom"])
        details = manage.get_details()
        self.assertEqual(details[0]["err_message"], "boom")
        self.assertEqual(get_workflow_state(details), State.FAILURE)

    def test_successful_node_has_no_error_in_details(self):
        manage, errors = _run([_node("ok", _OkNode.type)], [], "ok")

        self.assertEqual(errors, [None])
        self.assertIsNone(manage.get_details()[0]["err_message"])

    def test_caught_failure_is_not_raised_when_the_failed_node_finishes_last(self):
        # 场景 A:开启异常处理但异常锚点未连线
        _, errors = _run([_node("fail", _FailingNode.type, enableException=True)], [], "fail")
        self.assertEqual(errors, [None])

        # 场景 C:异常分支指向禁用节点,失败节点在并行分支之后结束
        nodes = [
            _node("start", _OkNode.type),
            _node("fail", _FailingNode.type, enableException=True),
            _node("other", _OkNode.type),
            _node("disabled", _OkNode.type, disabled=True),
        ]
        edges = [_edge("start", "fail"), _edge("start", "other"), _exception_edge("fail", "disabled")]
        _, errors = _run(nodes, edges, "start")
        self.assertEqual(errors, [None])

    def test_uncaught_failure_is_kept_while_a_parallel_branch_is_still_running(self):
        # 场景 B:失败节点不是最后结束的节点
        nodes = [_node("start", _OkNode.type), _node("fail", _FailingNode.type), _node("slow", _SlowNode.type)]

        _, errors = _run(nodes, [_edge("start", "fail"), _edge("start", "slow")], "start")

        self.assertEqual(errors, ["boom"])
