<script setup lang="ts">
import { computed, inject, onMounted } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormField } from '@/components/mk-dynamics-form'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { copyText } from '@/utils/clipboard'
import type { KnowledgeFieldConfig } from './types'
import UserInputFieldTable from './component/UserInputFieldTable.vue'

defineOptions({ name: 'WorkflowKnowledgeBaseNode' })

const getModel = inject<() => WorkflowNodeModel>('getModel')!
const model = getModel()

/* 文档设置：保留 properties 顶层字段与标题协议。 */
if (!Array.isArray(model.properties.user_input_field_list)) model.properties.user_input_field_list = []
model.properties.user_input_config = { title: '文档设置', ...(model.properties.user_input_config as KnowledgeFieldConfig | undefined) }
const nodeConfig = model.properties.config ?? (model.properties.config = {})
const inputFields = computed({
  get: () => model.properties.user_input_field_list as FormField[],
  set: (fields: FormField[]) => {
    model.properties.user_input_field_list = cloneDeep(fields)
    refreshFields()
  },
})
const inputConfig = computed({
  get: () => model.properties.user_input_config as KnowledgeFieldConfig,
  set: (config: KnowledgeFieldConfig) => {
    model.properties.user_input_config = cloneDeep(config)
  },
})
const globalFields = computed(() => nodeConfig.globalFields ?? [])

// 字段增删、编辑和排序统一更新全局变量，固定保留知识库输出。
function refreshFields() {
  nodeConfig.globalFields = [
    ...inputFields.value.map((field) => ({
      label: typeof field.label === 'string' ? field.label : (field.label?.label ?? field.field),
      value: field.field,
    })),
    { label: '知识库', value: 'knowledge' },
  ]
  model.graphModel.eventCenter.emit('refreshFieldList', undefined)
  model.clearNextNodeField(true)
}

function formatFieldReference(field: string) {
  return `{${field}}`
}

function copyField(field: string) {
  void copyText(`{{global.${field}}}`)
}

onMounted(() => refreshFields())
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <UserInputFieldTable v-model="inputFields" v-model:config="inputConfig" />
    </div>
    <h6 class="mk-title-decoration mt-4 mb-2">输出参数</h6>
    <div class="mk-gray-card space-y-4">
      <div v-for="field in globalFields" :key="field.value" class="group flex-between">
        <span class="break-all">{{ field.label }} {{ formatFieldReference(field.value) }}</span>
        <!-- 复制全局变量引用 -->
        <el-button class="group-hover-visible" link @click="copyField(field.value)">
          <MkIcon name="icon_copy_outlined" />
        </el-button>
      </div>
    </div>
  </NodeContainer>
</template>
