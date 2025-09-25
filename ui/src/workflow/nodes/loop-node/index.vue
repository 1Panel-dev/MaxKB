<template>
  <NodeContainer :nodeModel="nodeModel">
    <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
      <el-form
        @submit.prevent
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="replyNodeFormRef"
      >
        <el-form-item
          :label="$t('views.applicationWorkflow.nodes.loopNode.loopType.label')"
          @click.prevent
          prop="loop_type"
          :rules="{
            message: $t('views.applicationWorkflow.nodes.loopNode.loopType.requiredMessage'),
            trigger: 'change',
            required: true,
          }"
        >
          <el-select v-model="form_data.loop_type" type="small">
            <el-option
              :label="$t('views.applicationWorkflow.nodes.loopNode.loopType.arrayLoop')"
              value="ARRAY"
            />
            <el-option
              :label="$t('views.applicationWorkflow.nodes.loopNode.loopType.numberLoop')"
              value="NUMBER"
            />
            <el-option
              :label="$t('views.applicationWorkflow.nodes.loopNode.loopType.infiniteLoop')"
              value="LOOP"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          v-if="form_data.loop_type == 'ARRAY'"
          :label="$t('views.applicationWorkflow.nodes.loopNode.loopArray.label')"
          @click.prevent
          prop="array"
          :rules="{
            message: $t('views.applicationWorkflow.nodes.loopNode.loopArray.requiredMessage'),
            trigger: 'blur',
            required: true,
          }"
        >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="$t('views.applicationWorkflow.nodes.loopNode.loopArray.placeholder')"
            v-model="form_data.array"
          />
        </el-form-item>
        <el-form-item
          v-else-if="form_data.loop_type == 'NUMBER'"
          :label="$t('views.applicationWorkflow.nodes.loopNode.loopNumber.label')"
          @click.prevent
          prop="number"
          :rules="{
            message: $t('views.applicationWorkflow.nodes.loopNode.loopNumber.requiredMessage'),
            trigger: 'blur',
            required: true,
          }"
        >
          <el-input-number v-model="form_data.number" :min="1" />
        </el-form-item>
      </el-form>
    </el-card>
  </NodeContainer>
</template>
<script setup lang="ts">
import { set, throttle } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { ref, computed, onMounted, watch } from 'vue'
import { isLastNode } from '@/workflow/common/data'
import { loopBodyNode, loopStartNode } from '@/workflow/common/data'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
const props = defineProps<{ nodeModel: any }>()

const form = {
  loop_type: 'ARRAY',
  array: [],
  number: 1,
}

const form_data = computed({
  get: () => {
    if (props.nodeModel.properties.node_data) {
      return props.nodeModel.properties.node_data
    } else {
      set(props.nodeModel.properties, 'node_data', form)
    }
    return props.nodeModel.properties.node_data
  },
  set: (value) => {
    set(props.nodeModel.properties, 'node_data', value)
  },
})
const showNode = computed(() => {
  if (props.nodeModel.properties.showNode !== undefined) {
    return props.nodeModel.properties.showNode
  }
  set(props.nodeModel.properties, 'showNode', true)
  return true
})
watch(showNode, () => {
  if (showNode.value) {
    throttle(mountLoopBodyNode, 1000)()
  } else {
    throttle(destroyLoopBodyNode, 1000)()
  }
})
const replyNodeFormRef = ref()
const nodeCascaderRef = ref()
const validate = () => {
  return Promise.all([
    nodeCascaderRef.value ? nodeCascaderRef.value.validate() : Promise.resolve(''),
    replyNodeFormRef.value?.validate(),
  ]).catch((err: any) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}
const destroyLoopBodyNode = () => {
  const nodeOutgoingNode = props.nodeModel.graphModel.getNodeOutgoingNode(props.nodeModel.id)
  const loopBody = nodeOutgoingNode.find((item: any) => item.type == loopBodyNode.type)
  if (loopBody) {
    loopBody.set_loop_body()
    props.nodeModel.graphModel.deleteNode(loopBody.id)
  }
}
const mountLoopBodyNode = () => {
  const nodeOutgoingNode = props.nodeModel.graphModel.getNodeOutgoingNode(props.nodeModel.id)
  if (!nodeOutgoingNode.some((item: any) => item.type == loopBodyNode.type)) {
    let workflow = { nodes: [loopStartNode], edges: [] }
    let x = props.nodeModel.x
    let y = props.nodeModel.y + 350
    if (props.nodeModel.properties.node_data.loop_body) {
      workflow = props.nodeModel.properties.node_data.loop_body
    }
    if (props.nodeModel.properties.node_data.loop) {
      x = props.nodeModel.properties.node_data.loop.x
      y = props.nodeModel.properties.node_data.loop.y - 330
    }
    const nodeModel = props.nodeModel.graphModel.addNode({
      type: loopBodyNode.type,
      properties: {
        ...loopBodyNode.properties,
        workflow: workflow,
        loop_node_id: props.nodeModel.id,
      },
      x: x,
      y: y,
    })
    props.nodeModel.graphModel.addEdge({
      type: 'loop-edge',
      sourceNodeId: props.nodeModel.id,
      sourceAnchorId: props.nodeModel.id + '_children',
      targetNodeId: nodeModel.id,
      virtual: true,
    })
  }
}

onMounted(() => {
  if (typeof props.nodeModel.properties.node_data?.is_result === 'undefined') {
    if (isLastNode(props.nodeModel)) {
      set(props.nodeModel.properties.node_data, 'is_result', true)
    }
  }
  set(props.nodeModel, 'validate', validate)
  mountLoopBodyNode()
})
</script>
<style lang="scss" scoped></style>
