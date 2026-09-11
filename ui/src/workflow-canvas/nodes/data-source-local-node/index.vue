<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { createAnchorGuard } from '@/workflow-canvas/core/utils'

defineOptions({ name: 'WorkflowDataSourceLocalNode' })

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
const rules: FormRules<DataSourceLocalForm> = {
  file_type_list: [{ type: 'array', required: true, message: '请选择文件格式', trigger: 'change' }],
  file_count_limit: [{ type: 'integer', required: true, min: 1, max: 1000, message: '请输入 1–1000 的文件数量', trigger: 'change' }],
  file_size_limit: [{ type: 'integer', required: true, min: 1, max: 1000, message: '请输入 1–1000 MB 的文件大小', trigger: 'change' }],
}

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
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" :rules="rules" label-position="top" require-asterisk-position="right" @submit.prevent>
        <!-- 设置允许上传的文件格式 -->
        <el-form-item label="文件格式" prop="file_type_list">
          <el-select
            v-model="formData.file_type_list"
            placeholder="请选择文件格式"
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
        <el-form-item label="最多上传文件数" prop="file_count_limit">
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
        <el-form-item label="单个文件大小上限（MB）" prop="file_size_limit">
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
