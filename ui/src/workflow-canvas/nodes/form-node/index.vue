<script setup lang="ts">
import { computed, inject, onMounted, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { FormField, VisibilityFieldOption } from '@/components/mk-dynamics-form'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { handleNodeWheel } from '@/workflow-canvas/core/utils'
import FormSettingTable from './component/form-setting/FormSettingTable.vue'

defineOptions({ name: 'WorkflowFormNode' })

const getModel = inject<() => WorkflowNodeModel>('getModel')!
const model = getModel()

interface FormNodeForm {
  is_result: boolean
  form_field_list: FormField[]
  form_content_format: string
}

const formNodeFormRef = useTemplateRef<FormInstance>('formNodeFormRef')

// 初始化时一次性补齐旧节点缺失的表单配置。
const defaultForm: FormNodeForm = { is_result: true, form_content_format: '', form_field_list: [] }
const savedForm = model.properties.node_data as Partial<FormNodeForm> | undefined
// 当前表单引用统一使用真实节点 ID，兼容旧占位标识与 v2 未保存 self 的条件。
const savedFields = cloneDeep(Array.isArray(savedForm?.form_field_list) ? savedForm.form_field_list : defaultForm.form_field_list)
for (const field of savedFields) {
  for (const condition of field.visibility_rules?.conditions ?? []) {
    if (condition.field?.length === 2 && (condition.self || condition.field[0] === 'self-form' || condition.field[0] === model.id)) {
      condition.field[0] = model.id
      condition.self = true
    }
  }
}
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  is_result: savedForm?.is_result ?? defaultForm.is_result,
  form_content_format: savedForm?.form_content_format ?? defaultForm.form_content_format,
  form_field_list: savedFields,
}

const formData = computed<FormNodeForm>({
  get: () => model.properties.node_data as FormNodeForm,
  set: (value) => (model.properties.node_data = value),
})

// 字段表格只编辑列表，节点统一写回并同步下游引用。
const formFields = computed({
  get: () => formData.value.form_field_list,
  set: (fields: FormField[]) => {
    formData.value.form_field_list = cloneDeep(fields)
    model.properties.config ??= {}
    model.properties.config.fields = [
      { label: '表单全部内容', value: 'form_data' },
      ...formFields.value.map((field) => ({
        label: typeof field.label === 'string' ? field.label : (field.label?.label ?? ''),
        value: field.field,
      })),
    ]
    model.clearNextNodeField(true)
  },
})

const upstreamFieldOptions = computed<VisibilityFieldOption[]>(() =>
  model.getUpNodeFieldList(false, true).filter((field) => Boolean(field.children?.length)),
)

// 节点校验保留表单内容与显隐条件中的失效引用检查。
function validate() {
  const validationResults: Array<Promise<unknown>> = []
  const formResult = formNodeFormRef.value?.validate()
  if (formResult) validationResults.push(formResult)

  const upstreamNodeFields = model.getUpNodeFieldList(true, true)
  for (const field of formData.value.form_field_list) {
    for (const condition of field.visibility_rules?.conditions || []) {
      if (!condition.field || condition.field.length < 2 || !condition.field[0] || !condition.field[1]) continue
      if (condition.self) {
        if (!formData.value.form_field_list.some((formField) => formField.field === condition.field[1])) {
          validationResults.push(Promise.reject('引用变量不存在'))
        }
      } else {
        const nodeEntry = upstreamNodeFields.find((node) => node.value === condition.field[0])
        if (!nodeEntry || !nodeEntry.children?.some((nodeField) => nodeField.value === condition.field[1])) {
          validationResults.push(Promise.reject('引用变量不存在'))
        }
      }
    }
  }
  return Promise.all(validationResults).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  model.validate = validate
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formNodeFormRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <el-form-item prop="form_content_format" class="mk-hide-asterisk" :rules="{ required: true, message: '请填写表单输出内容', trigger: 'blur' }">
          <template #label>
            <div class="flex items-center gap-1">
              <span class="mk-required">表单输出内容</span>
              <el-tooltip placement="right" content="设置执行该节点输出的内容，{ form } 为表单的占位符">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </el-tooltip>
            </div>
          </template>
          <MdEditorMagnify v-model="formData.form_content_format" title="表单输出内容" @wheel="handleNodeWheel" />
        </el-form-item>
        <!-- 表单配置 -->
        <el-form-item>
          <FormSettingTable
            v-model="formFields"
            :upstream-field-options="upstreamFieldOptions"
            :node-id="model.id"
            :node-name="String(model.properties.stepName || '表单收集')"
          />
        </el-form-item>
      </el-form>
    </div>
  </NodeContainer>
</template>
