<script setup lang="ts">
import { set } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/NodeContainer.vue'
import { isLastNode } from '@/workflow-canvas/core/utils'
import type { BaseNodeModel } from '@logicflow/core'

defineOptions({ name: 'WorkflowReplyNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel()
interface ReplyNodeForm {
  content: string
  fields: string[]
  is_result: boolean
  reply_type: 'content' | 'referencing'
}

const formRef = useTemplateRef<FormInstance>('formRef')
const nodeCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('nodeCascaderRef')

const formData = computed<ReplyNodeForm>({
  get: () => {
    if (!model.properties.node_data) {
      model.properties.node_data = {
        content: '',
        fields: [],
        is_result: true,
        reply_type: 'content',
      }
    }
    return model.properties.node_data as ReplyNodeForm
  },
  set: (value) => (model.properties.node_data = value),
})

function validate() {
  return Promise.all([
    formData.value.reply_type === 'referencing'
      ? nodeCascaderRef.value?.validate()
      : Promise.resolve(),
    formRef.value?.validate(),
  ]).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  if (formData.value.is_result === undefined && isLastNode(model)) {
    formData.value.is_result = true
  }
  model.validate = validate
})
</script>

<template>
  <NodeContainer :node-model="model">
    <el-form ref="formRef" :model="formData" label-position="top" @submit.prevent>
      <el-form-item label="回复内容">
        <template #label>
          <div class="flex w-full items-center justify-between gap-3">
            <span>回复内容</span>
            <el-select v-model="formData.reply_type" :teleported="false" class="w-24" size="small">
              <el-option label="引用变量" value="referencing" />
              <el-option label="自定义" value="content" />
            </el-select>
          </div>
        </template>

        <NodeCascader
          v-if="formData.reply_type === 'referencing'"
          ref="nodeCascaderRef"
          v-model="formData.fields"
          :node-model="model"
          class="w-full"
          placeholder="请选择变量"
        />
        <el-input v-else v-model="formData.content" :rows="5" type="textarea" />
      </el-form-item>

      <el-form-item label="返回内容">
        <el-switch v-model="formData.is_result" />
      </el-form-item>
    </el-form>
  </NodeContainer>
</template>
