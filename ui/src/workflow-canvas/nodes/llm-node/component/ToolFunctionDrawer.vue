<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { LlmTool, LlmToolFunction, LlmToolParameter } from '../types'
import type { FormInstance, FormItemRule } from 'element-plus'
import { normalizeTool, toolParameterTypes } from '../types'
import ToolParameterDialog from './ToolParameterDialog.vue'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'WorkflowLlmToolFunctionDrawer' })

const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ existingNames: string[] }>()
const emit = defineEmits<{ submit: [tool: LlmTool, index?: number] }>()

interface ToolFunctionForm {
  name: string
  description: string
  parameters: LlmToolParameter[]
}

const formRef = useTemplateRef<FormInstance>('formRef')
const parameterDialogRef = useTemplateRef<InstanceType<typeof ToolParameterDialog>>('parameterDialogRef')
const visible = ref(false)
const editingName = ref('')
const currentIndex = ref<number>()
const functionForm = ref<ToolFunctionForm>({ name: '', description: '', parameters: [] })
const parseJson = ref('')
const parseError = ref('')

const nameRules = computed<FormItemRule[]>(() => [
  { whitespace: true, required: true, message: t('workflow.llm.toolName.requiredMessage'), trigger: 'blur' },
  {
    validator: (_rule, value: string, callback) => {
      const name = value.trim()
      const duplicated = props.existingNames.includes(name) && !(currentIndex.value !== undefined && name === editingName.value)
      callback(duplicated ? new Error(t('workflow.llm.toolName.duplicateMessage')) : undefined)
    },
    trigger: 'blur',
  },
])

function toParameters(parameters?: LlmToolFunction['parameters']): LlmToolParameter[] {
  const required = parameters?.required ?? []
  return Object.entries(parameters?.properties ?? {}).map(([name, property]) => ({
    name,
    type: property.type || 'string',
    description: property.description || '',
    required: required.includes(name),
  }))
}

function toFunctionParameters(parameters: LlmToolParameter[]): LlmToolFunction['parameters'] {
  const properties: LlmToolFunction['parameters']['properties'] = {}
  const required: string[] = []
  parameters.forEach((parameter) => {
    properties[parameter.name] = { type: parameter.type, description: parameter.description }
    if (parameter.required) required.push(parameter.name)
  })
  return { type: 'object', properties, ...(required.length ? { required } : {}) }
}

// 抽屉仅维护工具草稿，节点接收提交后关闭。
function open(tool?: LlmTool, index?: number) {
  if (tool) {
    editingName.value = tool.function.name
    currentIndex.value = index
    functionForm.value = {
      name: tool.function.name,
      description: tool.function.description,
      parameters: toParameters(tool.function.parameters),
    }
    parseJson.value = JSON.stringify(tool, null, 2)
  }
  visible.value = true
}

function close() {
  visible.value = false
}

function getParameterError(parameters: LlmToolParameter[]): string {
  const names = new Set<string>()
  for (const parameter of parameters) {
    const name = parameter.name.trim()
    if (!name) return t('workflow.llm.toolParameters.nameRequiredMessage')
    if (name.length > 64) return `${t('workflow.llm.toolParameters.nameLengthMessage', { max: 64 })}：${name}`
    if (names.has(name)) return `${t('workflow.parameters.duplicateMessage')}：${name}`
    if (!toolParameterTypes.includes(parameter.type)) return t('workflow.llm.toolParameters.typeMessage', { name })
    if (typeof parameter.description !== 'string' || parameter.description.length > 256)
      return t('workflow.llm.toolParameters.descriptionMessage', { name, max: 256 })
    names.add(name)
  }
  return ''
}

function parseFromJson() {
  parseError.value = ''
  try {
    const tool = normalizeTool(JSON.parse(parseJson.value))
    if (!tool) {
      parseError.value = t('workflow.llm.toolName.missingMessage')
      return
    }
    const parameters = toParameters(tool.function.parameters)
    parseError.value = getParameterError(parameters)
    if (parseError.value) return
    functionForm.value = {
      name: tool.function.name,
      description: tool.function.description,
      parameters,
    }
    formRef.value?.clearValidate()
  } catch {
    parseError.value = t('workflow.llm.jsonParse.invalidMessage')
  }
}

function handleOpenParameter(parameter?: LlmToolParameter, index?: number) {
  parameterDialogRef.value?.open(parameter, index)
}

function saveParameter(parameter: LlmToolParameter, index?: number) {
  if (functionForm.value.parameters.some((field, fieldIndex) => fieldIndex !== index && field.name === parameter.name)) {
    MsgError(`${t('workflow.parameters.duplicateMessage')}：${parameter.name}`)
    return
  }
  const parameters = functionForm.value.parameters
  if (index === undefined) parameters.push(cloneDeep(parameter))
  else parameters.splice(index, 1, cloneDeep(parameter))
  parameterDialogRef.value?.close()
}

function removeParameter(index: number) {
  functionForm.value.parameters.splice(index, 1)
}

function handleSubmit() {
  formRef.value
    ?.validate()
    .then(() => {
      const parameterError = getParameterError(functionForm.value.parameters)
      if (parameterError) {
        MsgError(parameterError)
        return
      }
      const tool: LlmTool = {
        type: 'function',
        function: {
          name: functionForm.value.name.trim(),
          description: functionForm.value.description.trim(),
          parameters: toFunctionParameters(functionForm.value.parameters),
        },
      }
      emit('submit', tool, currentIndex.value)
    })
    .catch(() => {})
}

function resetData() {
  editingName.value = ''
  currentIndex.value = undefined
  functionForm.value = { name: '', description: '', parameters: [] }
  parseJson.value = ''
  parseError.value = ''
  formRef.value?.clearValidate()
}

defineExpose({ open, close })
</script>

<template>
  <MkDrawer
    v-model="visible"
    :title="currentIndex !== undefined ? t('workflow.llm.tools.editTitle') : t('workflow.llm.tools.addTitle')"
    @closed="resetData"
  >
    <el-form
      ref="formRef"
      :model="functionForm"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
      @paste.stop
    >
      <el-form-item :label="t('workflow.llm.jsonParse.label')" :error="parseError">
        <el-input v-model="parseJson" type="textarea" :rows="8" :placeholder="t('workflow.llm.jsonParse.placeholder')" />
      </el-form-item>
      <!-- 从 JSON 回填工具 -->
      <el-button class="mb-4" type="primary" @click="parseFromJson">{{ t('workflow.llm.jsonParse.action') }}</el-button>
      <el-form-item :label="t('workflow.llm.toolName.label')" prop="name" :rules="nameRules">
        <el-input
          v-model="functionForm.name"
          maxlength="64"
          show-word-limit
          :placeholder="t('workflow.llm.toolName.placeholder')"
          @blur="functionForm.name = functionForm.name.trim()"
        />
      </el-form-item>
      <el-form-item
        :label="t('workflow.llm.toolDescription.label')"
        prop="description"
        :rules="{ whitespace: true, required: true, message: t('workflow.llm.toolDescription.requiredMessage'), trigger: 'blur' }"
      >
        <el-input
          v-model="functionForm.description"
          type="textarea"
          :rows="3"
          maxlength="256"
          show-word-limit
          :placeholder="t('workflow.llm.toolDescription.placeholder')"
        />
      </el-form-item>

      <div class="flex-between mb-2">
        <span>{{ t('workflow.llm.toolParameters.label') }}</span>
        <!-- 添加参数 -->
        <el-button text type="primary" @click="handleOpenParameter()">
          <MkIcon name="icon_add_outlined" />
        </el-button>
      </div>
      <MkTable
        :data="functionForm.parameters"
        size="small"
        row-key="name"
        :max-height="undefined"
        :empty-text="t('workflow.llm.toolParameters.empty')"
      >
        <el-table-column :label="t('dynamicForm.fields.parameter.label')">
          <template #default="{ row }">
            <span class="block truncate" :title="row.name">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('workflow.llm.dataType.label')" width="90">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.description.label')">
          <template #default="{ row }">
            <span class="block truncate" :title="row.description || '-'">{{ row.description || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('dynamicForm.fields.required.columnLabel')" width="55">
          <template #default="{ row }">{{ row.required ? t('common.options.yes') : t('common.options.no') }}</template>
        </el-table-column>
        <el-table-column :label="t('common.labels.operation')" width="80">
          <template #default="{ row, $index }">
            <!-- 编辑参数 -->
            <el-button text type="primary" @click="handleOpenParameter(row, $index)"><MkIcon name="icon_edit_outlined" /></el-button>
            <!-- 删除参数 -->
            <el-button text type="primary" @click="removeParameter($index)"><MkIcon name="icon_delete-trash_outlined" /></el-button>
          </template>
        </el-table-column>
      </MkTable>
    </el-form>

    <ToolParameterDialog ref="parameterDialogRef" @submit="saveParameter" />

    <template #footer>
      <!-- 取消工具编辑 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 提交工具 -->
      <el-button type="primary" @click="handleSubmit">
        {{ currentIndex !== undefined ? t('common.actions.save') : t('common.actions.add') }}
      </el-button>
    </template>
  </MkDrawer>
</template>
