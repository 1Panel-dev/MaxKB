<script setup lang="ts">
import { computed, inject, onMounted, useTemplateRef, watch } from 'vue'
import { cloneDeep, set, throttle } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { BaseNodeModel } from '@logicflow/core'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import { loopBodyNode, loopStartNode } from '@/workflow-canvas/config/node-data'
import { WorkflowNodeType } from '@/workflow-canvas/types'

defineOptions({ name: 'WorkflowLoopNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel()

type CanvasLoopBodyModel = BaseNodeModel & { setLoopBody?: () => void }

interface LoopNodeData {
  loop_type: 'ARRAY' | 'NUMBER' | 'LOOP'
  array: string[]
  number: number
  loop?: { x: number; y: number }
  loop_body?: { nodes: unknown[]; edges: unknown[] }
}

const formRef = useTemplateRef<FormInstance>('formRef')

const DEFAULT_FORM: LoopNodeData = { loop_type: 'ARRAY', array: [], number: 1 }

const formData = computed<LoopNodeData>({
  get: () => {
    if (!model.properties.node_data) {
      set(model.properties, 'node_data', cloneDeep(DEFAULT_FORM))
    }
    const data = model.properties.node_data as LoopNodeData
    if (data.loop_type === undefined) set(data, 'loop_type', 'ARRAY')
    if (!Array.isArray(data.array)) set(data, 'array', [])
    if (data.number === undefined) set(data, 'number', 1)
    return data
  },
  set: (value) => (model.properties.node_data = value),
})

const showNode = computed({
  get: () => {
    if (model.properties.showNode !== undefined) return model.properties.showNode
    set(model.properties, 'showNode', true)
    return true
  },
  set: (v) => set(model.properties, 'showNode', v),
})

watch(showNode, (value) => {
  value ? throttle(mountLoopBodyNode, 1000)() : throttle(destroyLoopBodyNode, 1000)()
})

function destroyLoopBodyNode() {
  const outgoing = model.graphModel.getNodeOutgoingNode(model.id)
  const loopBody = outgoing.find((item) => String(item.type) === WorkflowNodeType.LoopBodyNode) as CanvasLoopBodyModel | undefined
  if (loopBody) {
    loopBody.setLoopBody?.()
    model.graphModel.deleteNode(loopBody.id)
  }
}

function mountLoopBodyNode() {
  const outgoing = model.graphModel.getNodeOutgoingNode(model.id)
  if (outgoing.some((item) => String(item.type) === WorkflowNodeType.LoopBodyNode)) return

  const nodeData = model.properties.node_data as LoopNodeData | undefined
  let workflow = (model.properties.workflow as { nodes: unknown[]; edges: unknown[] } | undefined) ?? {
    nodes: [loopStartNode],
    edges: [],
  }
  let x = model.x
  let y = model.y + 850
  if (nodeData?.loop_body) workflow = nodeData.loop_body
  if (nodeData?.loop) {
    x = nodeData.loop.x
    y = nodeData.loop.y
  }

  const bodyModel = model.graphModel.addNode({
    type: WorkflowNodeType.LoopBodyNode,
    properties: {
      ...cloneDeep(loopBodyNode.properties),
      height: loopBodyNode.height,
      workflow: cloneDeep(workflow),
      loop_node_id: model.id,
    },
    x,
    y,
  })
  model.graphModel.addEdge({
    type: 'loop-edge',
    sourceNodeId: model.id,
    sourceAnchorId: `${model.id}_children`,
    targetNodeId: bodyModel.id,
    targetAnchorId: `${bodyModel.id}_children`,
    virtual: true,
  } as unknown as Parameters<typeof model.graphModel.addEdge>[0])
}

function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  model.validate = validate
  if (showNode.value && !model.virtual) mountLoopBodyNode()
})
</script>

<template>
  <NodeContainer :node-model="model">
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <el-form-item label="循环类型" prop="loop_type" :rules="{ required: true, message: '请选择循环类型', trigger: 'change' }">
          <el-select v-model="formData.loop_type" :teleported="false" class="w-full">
            <el-option label="数组循环" value="ARRAY" />
            <el-option label="次数循环" value="NUMBER" />
            <el-option label="无限循环" value="LOOP" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="formData.loop_type === 'ARRAY'" label="循环数组" prop="array">
          <NodeCascader ref="nodeCascaderRef" v-model="formData.array" :node-model="model" placeholder="请选择变量" />
        </el-form-item>
        <el-form-item v-else-if="formData.loop_type === 'NUMBER'" label="循环次数" prop="number">
          <el-input-number v-model="formData.number" :min="1" :step="1" controls-position="right" align="left" />
        </el-form-item>
      </el-form>
    </div>
  </NodeContainer>
</template>
