<script setup lang="ts">
import { computed, inject, onMounted, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { isLastNode } from '@/workflow-canvas/core/utils'

defineOptions({ name: 'WorkflowKnowledgeWriteNode' })

interface KnowledgeWriteForm {
  document_list: string[]
  is_result?: boolean
}

const getModel = inject<() => WorkflowNodeModel>('getModel')!
const model = getModel()
const formRef = useTemplateRef<FormInstance>('formRef')
const documentCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('documentCascaderRef')

/* 写入内容：初始化时补齐引用数组，保留已有配置。 */
const savedForm = model.properties.node_data as Partial<KnowledgeWriteForm> | undefined
model.properties.node_data = {
  ...savedForm,
  document_list: Array.isArray(savedForm?.document_list) ? savedForm.document_list : [],
}
const formData = computed(() => model.properties.node_data as KnowledgeWriteForm)
const rules: FormRules<KnowledgeWriteForm> = {
  document_list: [
    { type: 'array', required: true, message: '请选择输入内容', trigger: 'change' },
    { asyncValidator: () => documentCascaderRef.value?.validate() ?? Promise.resolve(), trigger: 'change' },
  ],
}

/* 节点校验及旧版末端输出默认值。 */
function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error })) ?? Promise.resolve()
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
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" :rules="rules" label-position="top" require-asterisk-position="right" @submit.prevent>
        <!-- 选择写入知识库的内容 -->
        <el-form-item label="输入内容" prop="document_list">
          <NodeCascader ref="documentCascaderRef" v-model="formData.document_list" :node-model="model" class="w-full!" placeholder="请选择输入内容" />
        </el-form-item>
      </el-form>
    </div>
  </NodeContainer>
</template>
