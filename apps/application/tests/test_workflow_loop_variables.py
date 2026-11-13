import threading

from django.test import SimpleTestCase

from application.workflow.common import WorkflowType, new_instance
from application.workflow.nodes import get_node_class
from application.workflow.nodes.loop_node.loop_node import LoopNodeSerializer
from application.workflow.workflow_manage import CallBack, WorkflowManage
from common.exception.app_exception import AppApiException


def _node(node_id, node_type, node_data=None, **properties):
    return {
        "id": node_id,
        "type": node_type,
        "x": 0,
        "y": 0,
        "properties": {"stepName": node_id, "node_data": node_data or {}, **properties},
    }


def _edge(source, target):
    return {
        "id": f"{source}-{target}",
        "type": "app-edge",
        "sourceNodeId": source,
        "targetNodeId": target,
        "sourceAnchorId": f"{source}_right",
        "targetAnchorId": f"{target}_left",
    }


def _loop_start(*variables):
    return _node(
        "loop-start-node",
        "loop-start-node",
        stepName="循环开始",
        config={"fields": [{"label": "下标", "value": "index"}, {"label": "循环元素", "value": "item"}]},
        loop_input_field_list=[{"field": field, "label": field} for field in variables],
    )


def _assign(node_id, *variables):
    return _node(
        node_id,
        "variable-assign-node",
        {
            "variable_list": [
                {"name": ".".join(fields), "fields": fields, "source": "custom", "type": "string", "value": value}
                for fields, value in variables
            ]
        },
    )


def _loop(node_id, number, body_nodes, body_edges):
    return _node(
        node_id,
        "loop-node",
        {"loop_type": "NUMBER", "number": number, "loop_body": {"nodes": body_nodes, "edges": body_edges}},
    )


def _run(loop_node):
    """以循环节点作为起始节点跑完一个根工作流,返回根 WorkflowManage"""
    workflow = new_instance({"nodes": [loop_node], "edges": []})
    finished = threading.Event()
    errors = []

    def on_complete(_manage, error):
        errors.append(error)
        finished.set()

    def get_start_node(wf, manage):
        node = wf.get_node(loop_node["id"])
        node_class = get_node_class(node.type, WorkflowType.APPLICATION)
        return node_class(node, manage, lambda n: n.properties.get("node_data", {}))

    def on_next(wf_manage, _content):
        # 知识库工作流每收到一块输出就取一次详情,第一轮循环尚未结束时也必须可用
        wf_manage.get_details()

    manage = WorkflowManage(workflow, {}, WorkflowType.APPLICATION, CallBack(on_next, on_complete), get_start_node)
    manage.run()
    assert finished.wait(10), "workflow did not finish"
    assert errors == [None], errors
    return manage


class LoopVariableTests(SimpleTestCase):
    def test_loop_variable_is_shared_across_iterations_and_readable_after_the_loop(self):
        loop = _loop(
            "loop1",
            3,
            [
                _loop_start("total"),
                _assign(
                    "assign",
                    (["loop", "total"], "{{loop.total}}{{循环开始.index}}"),
                    (["global", "last"], "{{循环变量.total}}"),
                ),
            ],
            [_edge("loop-start-node", "assign")],
        )

        manage = _run(loop)

        # 循环变量存放在循环节点的上下文里,下游用 [循环节点ID, 变量名] 引用
        self.assertEqual(manage.get_reference_field("loop1", ["total"]), "012")
        # 循环体内给全局变量赋值,写到根工作流
        self.assertEqual(manage.get_reference_field("global", ["last"]), "012")
        self.assertNotIn("loop", manage.context["loop1"]["last_context"])
        self.assertNotIn("global", manage.context["loop1"]["last_context"])

    def test_nested_loop_writes_reach_the_owning_loop_and_the_root_workflow(self):
        inner = _loop(
            "inner",
            2,
            [
                _loop_start("cnt"),
                _assign(
                    "assign",
                    (["loop", "acc"], "{{loop.acc}}x"),
                    (["loop", "cnt"], "{{loop.cnt}}y"),
                    (["global", "g"], "{{loop.acc}}|{{loop.cnt}}"),
                ),
            ],
            [_edge("loop-start-node", "assign")],
        )
        outer = _loop("outer", 2, [_loop_start("acc"), inner], [_edge("loop-start-node", "inner")])

        manage = _run(outer)

        # 内层循环修改外层循环声明的变量
        self.assertEqual(manage.get_reference_field("outer", ["acc"]), "xxxx")
        # 内层循环自己的变量存放在外层循环体的上下文里,且每次进入内层循环都从空开始
        self.assertEqual(manage.context["outer"]["last_context"]["inner"]["cnt"], "yy")
        # 两层嵌套里给全局变量赋值,依然写到根工作流
        self.assertEqual(manage.context["global"], {"g": "xxxx|yy"})
        self.assertNotIn("global", manage.context["outer"]["last_context"])

    def test_loop_variable_cannot_use_a_name_reserved_by_the_loop_node(self):
        data = {"loop_type": "NUMBER", "number": 1, "loop_body": {"nodes": [_loop_start("last_context")], "edges": []}}

        with self.assertRaises(AppApiException):
            LoopNodeSerializer(data=data).is_valid(raise_exception=True)
