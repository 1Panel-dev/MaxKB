<script setup lang="ts">
import { computed, inject, onMounted, useTemplateRef } from 'vue'

import type { FormInstance } from 'element-plus'
import { handleNodeWheel } from '@/workflow-canvas/core/utils'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
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

// 节点初始化时补齐默认值和兼容旧数据，computed 只读取表单。
if (!model.properties.node_data) {
  model.properties.node_data = { content: '', fields: [], is_result: true, reply_type: 'content' }
}

const formData = computed<ReplyNodeForm>({
  get: () => model.properties.node_data as ReplyNodeForm,
  set: (value) => (model.properties.node_data = value),
})

function validate() {
  return Promise.all([
    formData.value.reply_type === 'referencing' ? nodeCascaderRef.value?.validate() : Promise.resolve(),
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
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" label-position="top" @submit.prevent>
        <el-form-item label="回复内容">
          <template #label>
            <div class="flex-between">
              <span>回复内容</span>
              <el-select v-model="formData.reply_type" :teleported="false" class="w-21!" size="small">
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

          <MdEditorMagnify v-else @wheel="handleNodeWheel" title="回复内容" v-model="formData.content" />
        </el-form-item>

        <div class="flex-between w-full">
          <span class="flex items-center gap-1">
            返回内容
            <el-tooltip content="关闭后该节点的内容则不输出给用户。如果你想让用户看到该节点的输出内容，请打开开关。" placement="right">
              <MkIcon name="icon_info_outlined" />
            </el-tooltip>
          </span>
          <span>
            <el-switch v-model="formData.is_result" size="small" />
          </span>
        </div>
      </el-form>
    </div>
  </NodeContainer>
</template>
