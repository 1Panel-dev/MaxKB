<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { FormInstance, FormRules } from 'element-plus'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { createAnchorGuard } from '@/workflow-canvas/core/utils'

defineOptions({ name: 'WorkflowDataSourceLocalNode' })
const { t } = useI18n({ useScope: 'global' })

interface DataSourceLocalForm {
  file_type_list: string[]
  file_size_limit: number
  file_count_limit: number
}

const getModel = inject<() => WorkflowNodeModel>('getModel')!
const model = getModel()
const formRef = useTemplateRef<FormInstance>('formRef')
const anchorGuard = createAnchorGuard(model)
const fileTypeOptions = ['TXT', 'DOCX', 'PDF', 'HTML', 'XLS', 'XLSX', 'ZIP', 'CSV', 'MD']

/* 本地文件限制：初始化补齐旧数据，保留自定义格式和已有配置。 */
const savedForm = model.properties.node_data as Partial<DataSourceLocalForm> | undefined
model.properties.node_data = {
  file_size_limit: 100,
  file_count_limit: 50,
  ...savedForm,
  file_type_list: Array.isArray(savedForm?.file_type_list) ? savedForm.file_type_list : [...fileTypeOptions],
}
const formData = computed(() => model.properties.node_data as DataSourceLocalForm)
const rules = computed<FormRules<DataSourceLocalForm>>(() => ({
  file_type_list: [{ type: 'array', required: true, message: t('workflow.localFile.format.requiredMessage'), trigger: 'change' }],
  file_count_limit: [
    { required: true, message: t('common.validation.inputRequired'), trigger: 'change' },
    {
      type: 'integer',
      min: 1,
      max: 1000,
      message: t('workflow.localFile.fileCount.rangeMessage', { min: 1, max: 1000 }),
      trigger: 'change',
    },
  ],
  file_size_limit: [
    { required: true, message: t('common.validation.inputRequired'), trigger: 'change' },
    {
      type: 'integer',
      min: 1,
      max: 1000,
      message: t('workflow.localFile.fileSize.rangeMessage', { min: 1, max: 1000 }),
      trigger: 'change',
    },
  ],
}))

function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error })) ?? Promise.resolve()
}

onMounted(() => {
  model.validate = validate
})
onBeforeUnmount(() => anchorGuard.reset())
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">{{ t('workflow.node.setting') }}</h6>
    <div class="mk-gray-card">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        :validate-on-rule-change="false"
        label-position="top"
        require-asterisk-position="right"
        @submit.prevent
      >
        <!-- 设置允许上传的文件格式 -->
        <el-form-item :label="t('workflow.localFile.format.label')" prop="file_type_list">
          <el-select
            v-model="formData.file_type_list"
            :placeholder="t('workflow.localFile.format.placeholder')"
            class="w-full!"
            clearable
            multiple
            allow-create
            filterable
            default-first-option
            :teleported="false"
            @visible-change="anchorGuard.setOverlayVisible('file_type_list', $event)"
          >
            <el-option v-for="fileType in fileTypeOptions" :key="fileType" :label="fileType" :value="fileType" />
          </el-select>
        </el-form-item>
        <!-- 设置上传文件数量上限 -->
        <el-form-item :label="t('workflow.localFile.fileCount.label')" prop="file_count_limit">
          <el-input-number
            v-model="formData.file_count_limit"
            :min="1"
            :max="1000"
            :value-on-clear="0"
            controls-position="right"
            align="left"
            class="w-full!"
            :step="1"
            step-strictly
          />
        </el-form-item>
        <!-- 设置单个文件大小上限 -->
        <el-form-item :label="`${t('workflow.localFile.fileSize.label')}（MB）`" prop="file_size_limit">
          <el-input-number
            v-model="formData.file_size_limit"
            :min="1"
            :max="1000"
            :value-on-clear="0"
            controls-position="right"
            align="left"
            class="w-full!"
            :step="1"
            step-strictly
          />
        </el-form-item>
      </el-form>
    </div>
  </NodeContainer>
</template>
