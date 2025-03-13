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
          :label="$t('views.applicationWorkflow.nodes.loopNode.loopType.label', '循环类型')"
          @click.prevent
        >
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span
                  >{{ $t('views.applicationWorkflow.nodes.loopNode.loopType.label', '循环类型')
                  }}<span class="danger">*</span></span
                >
              </div>
            </div>
          </template>
          <el-select v-model="form_data.loop_type" type="small">
            <el-option
              :label="$t('views.applicationWorkflow.nodes.loopNode.array', '数组循环')"
              value="ARRAY"
            />
            <el-option
              :label="$t('views.applicationWorkflow.nodes.loopNode.number', '指定次数循环')"
              value="NUMBER"
            />
            <el-option
              :label="$t('views.applicationWorkflow.nodes.loopNode.loop', '无限循环')"
              value="LOOP"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          v-if="form_data.loop_type == 'ARRAY'"
          :label="$t('views.applicationWorkflow.nodes.loopNode.loopType.label', '循环数组')"
          @click.prevent
          prop="array"
          :rules="{
            message: $t(
              'views.applicationWorkflow.nodes.loopNode.array.requiredMessage',
              '循环数组必填'
            ),
            trigger: 'blur',
            required: true
          }"
        >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="
              $t('views.applicationWorkflow.nodes.loopNode.array.placeholder', '请选择循环数组')
            "
            v-model="form_data.array"
          />
        </el-form-item>
        <el-form-item
          v-else-if="form_data.loop_type == 'NUMBER'"
          :label="$t('views.applicationWorkflow.nodes.loopNode.loopType.label', '循环数组')"
          @click.prevent
          prop="number"
          :rules="{
            message: $t(
              'views.applicationWorkflow.nodes.loopNode.array.requiredMessage',
              '循环数组必填'
            ),
            trigger: 'blur',
            required: true
          }"
        >
          <el-input-number v-model="form_data.number" :min="1" />
        </el-form-item>
      </el-form>
    </el-card>
  </NodeContainer>
</template>
<script setup lang="ts">
import { set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { ref, computed, onMounted } from 'vue'
import { isLastNode } from '@/workflow/common/data'
import { loopBodyNode, loopStartNode } from '@/workflow/common/data'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
const props = defineProps<{ nodeModel: any }>()

const form = {
  loop_type: 'ARRAY',
  array: [],
  number: 1
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
  }
})

const replyNodeFormRef = ref()
const nodeCascaderRef = ref()
const validate = () => {
  return Promise.all([
    nodeCascaderRef.value ? nodeCascaderRef.value.validate() : Promise.resolve(''),
    replyNodeFormRef.value?.validate()
  ]).catch((err: any) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

onMounted(() => {
  if (typeof props.nodeModel.properties.node_data?.is_result === 'undefined') {
    if (isLastNode(props.nodeModel)) {
      set(props.nodeModel.properties.node_data, 'is_result', true)
    }
  }
  set(props.nodeModel, 'validate', validate)
  const nodeOutgoingNode = props.nodeModel.graphModel.getNodeOutgoingNode(props.nodeModel.id)
  if (!nodeOutgoingNode.some((item: any) => item.type == loopBodyNode.type)) {
    let workflow = { nodes: [loopStartNode], edges: [] }
    if (props.nodeModel.properties.node_data.loop_body) {
      workflow = props.nodeModel.properties.node_data.loop_body
    }
    const nodeModel = props.nodeModel.graphModel.addNode({
      type: loopBodyNode.type,
      properties: {
        ...loopBodyNode.properties,
        workflow: workflow,
        loop_node_id: props.nodeModel.id
      },
      x: props.nodeModel.x,
      y: props.nodeModel.y + loopBodyNode.height
    })
    props.nodeModel.graphModel.addEdge({
      type: 'loop-edge',
      sourceNodeId: props.nodeModel.id,
      sourceAnchorId: props.nodeModel.id + '_children',
      targetNodeId: nodeModel.id,
      virtual: true
    })
  }
})
</script>
<style lang="scss" scoped></style>
