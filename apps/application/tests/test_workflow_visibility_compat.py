from django.test import SimpleTestCase

from application.workflow.visibility_compat import normalize_workflow_visibility


def field_with(*conditions):
    return {
        "field": "target",
        "input_type": "TextInput",
        "visibility_rules": {"action": "show", "condition": "and", "conditions": list(conditions)},
    }


def condition(scope, name="is", **extra):
    return {"id": "c1", "field": [scope, name], "compare": "contain", "value": "ussop", **extra}


def base_node(*fields):
    return {"id": "base-node", "type": "base-node", "properties": {"user_input_field_list": list(fields)}}


def form_node(node_id, *fields):
    return {"id": node_id, "type": "form-node", "properties": {"node_data": {"form_field_list": list(fields)}}}


def conditions_of(node):
    properties = node["properties"]
    fields = properties.get("user_input_field_list") or properties["node_data"]["form_field_list"]
    return fields[0]["visibility_rules"]["conditions"]


class WorkflowVisibilityCompatTests(SimpleTestCase):
    def test_base_node_global_scope_becomes_self(self):
        node = base_node(field_with(condition("global")))
        self.assertTrue(normalize_workflow_visibility({"nodes": [node]}))
        self.assertEqual(conditions_of(node), [condition("base-node", self=True)])

    def test_form_node_self_references_become_self(self):
        node = form_node("form-1", field_with(condition("form-1"), condition("self-form", "b")))
        self.assertTrue(normalize_workflow_visibility({"nodes": [node]}))
        self.assertEqual(
            conditions_of(node),
            [condition("form-1", self=True), condition("form-1", "b", self=True)],
        )

    def test_form_node_inside_loop_is_normalized(self):
        inner = form_node("form-2", field_with(condition("form-2")))
        loop = {
            "id": "loop",
            "type": "loop-node",
            "properties": {"node_data": {"loop_body": {"nodes": [inner]}}},
        }
        self.assertTrue(normalize_workflow_visibility({"nodes": [loop]}))
        self.assertIs(conditions_of(inner)[0]["self"], True)

    def test_cross_node_and_global_references_in_form_node_are_kept(self):
        node = form_node("form-1", field_with(condition("global", "time"), condition("llm-1", "answer")))
        self.assertFalse(normalize_workflow_visibility({"nodes": [node]}))
        self.assertEqual(conditions_of(node), [condition("global", "time"), condition("llm-1", "answer")])

    def test_v3_data_and_empty_rules_are_unchanged(self):
        v3_base = base_node(field_with(condition("base-node", self=True)), field_with())
        empty_rules = {"field": "x", "visibility_rules": None}
        work_flow = {"nodes": [v3_base, form_node("form-1", empty_rules), {"id": "start-node"}]}
        self.assertFalse(normalize_workflow_visibility(work_flow))
        self.assertFalse(normalize_workflow_visibility({}))
        self.assertFalse(normalize_workflow_visibility(None))
