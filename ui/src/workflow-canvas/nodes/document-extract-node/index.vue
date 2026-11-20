<script setup lang="ts">
import { computed, inject, onMounted, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { FormInstance } from 'element-plus'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import { FILE_REFERENCE_EXAMPLE } from '@/workflow-canvas/config/constants'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { WorkflowNodeType } from '@/workflow-canvas/types'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'WorkflowDocumentExtractNode' })
const getModel = inject('getModel') as () => WorkflowNodeModel
const model = getModel()
const formRef = useTemplateRef<FormInstance>('formRef')

interface DocumentExtractForm {
  document_list: string[]
}

const defaultForm: DocumentExtractForm = { document_list: [WorkflowNodeType.Start, 'document'] }
const savedForm = model.properties.node_data as Partial<DocumentExtractForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  document_list: Array.isArray(savedForm?.document_list) ? savedForm.document_list : defaultForm.document_list,
}
const formData = computed(() => model.properties.node_data as DocumentExtractForm)

async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}
onMounted(() => {
  model.validate = validate
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">{{ t('workflow.nodeSettings.title') }}</h6>
    <div class="mk-gray-card">
      <el-form
        ref="formRef"
        :model="formData"
        :validate-on-rule-change="false"
        label-position="top"
        require-asterisk-position="right"
        @submit.prevent
      >
        <el-form-item
          class="mk-hide-asterisk"
          prop="document_list"
          :rules="{ type: 'array', required: true, message: t('workflow.document.requiredMessage'), trigger: 'change' }"
        >
          <template #label>
            <span class="flex-align-center gap-1">
              <span class="mk-required">{{ t('workflow.document.label') }}</span>
              <MkTooltip placement="right">
                <template #content>
                  <div class="font-mono whitespace-pre-wrap">{{ `${t('common.labels.example')}：\n${FILE_REFERENCE_EXAMPLE}` }}</div>
                </template>
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </MkTooltip>
            </span>
          </template>
          <NodeCascader
            ref="documentCascaderRef"
            v-model="formData.document_list"
            :node-model="model"
            :placeholder="t('workflow.document.placeholder')"
          />
        </el-form-item>
      </el-form>
    </div>
  </NodeContainer>
</template>
