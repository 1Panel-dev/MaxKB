<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormItemRule } from 'element-plus'
import { MsgError } from '@/utils/message'
import ToolParameterDialog from './ToolParameterDialog.vue'
import { normalizeTool, toolParameterTypes, type LlmTool, type LlmToolFunction, type LlmToolParameter } from '../types'

defineOptions({ name: 'WorkflowLlmToolFunctionDrawer' })

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

const nameRules: FormItemRule[] = [
  { whitespace: true, required: true, message: '请输入工具名称', trigger: 'blur' },
  {
    validator: (_rule, value: string, callback) => {
      const name = value.trim()
      const duplicated = props.existingNames.includes(name) && !(currentIndex.value !== undefined && name === editingName.value)
      callback(duplicated ? new Error('工具名称已存在') : undefined)
    },
    trigger: 'blur',
  },
]

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
    if (!name) return '请输入参数名称'
    if (name.length > 64) return `参数名称不能超过 64 字：${name}`
    if (names.has(name)) return `参数已存在：${name}`
    if (!toolParameterTypes.includes(parameter.type)) return `参数 ${name} 的数据类型不支持`
    if (typeof parameter.description !== 'string' || parameter.description.length > 256) return `参数 ${name} 的描述应为不超过 256 字的文本`
    names.add(name)
  }
  return ''
}

function parseFromJson() {
  parseError.value = ''
  try {
    const tool = normalizeTool(JSON.parse(parseJson.value))
    if (!tool) {
      parseError.value = '未找到工具名称'
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
    parseError.value = 'JSON 解析失败，请检查格式'
  }
}

function handleOpenParameter(parameter?: LlmToolParameter, index?: number) {
  parameterDialogRef.value?.open(parameter, index)
}

function saveParameter(parameter: LlmToolParameter, index?: number) {
  if (functionForm.value.parameters.some((field, fieldIndex) => fieldIndex !== index && field.name === parameter.name)) {
    MsgError(`参数已存在：${parameter.name}`)
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
  <MkDrawer v-model="visible" :title="currentIndex !== undefined ? '编辑工具' : '添加工具'" @closed="resetData">
    <el-form ref="formRef" :model="functionForm" label-position="top" require-asterisk-position="right" @submit.prevent @paste.stop>
      <el-form-item label="JSON 解析" :error="parseError">
        <el-input v-model="parseJson" type="textarea" :rows="8" placeholder="请输入 JSON 格式文本进行解析" />
        <!-- 从 JSON 回填工具 -->
      </el-form-item>
      <el-button class="mb-4" type="primary" @click="parseFromJson">解析</el-button>
      <el-form-item label="工具名称" prop="name" :rules="nameRules">
        <el-input
          v-model="functionForm.name"
          maxlength="64"
          show-word-limit
          placeholder="请输入工具名称"
          @blur="functionForm.name = functionForm.name.trim()"
        />
      </el-form-item>
      <el-form-item label="工具描述" prop="description" :rules="{ whitespace: true, required: true, message: '请输入工具描述', trigger: 'blur' }">
        <el-input v-model="functionForm.description" type="textarea" :rows="3" maxlength="256" show-word-limit placeholder="请输入工具描述" />
      </el-form-item>

      <div class="flex-between mb-2">
        <span>工具参数</span>
        <!-- 添加参数 -->
        <el-button text type="primary" @click="handleOpenParameter()">
          <MkIcon name="icon_add_outlined" />
        </el-button>
      </div>
      <MkTable :data="functionForm.parameters" size="small" row-key="name" :max-height="undefined" empty-text="暂无参数">
        <el-table-column label="参数">
          <template #default="{ row }">
            <span class="block truncate" :title="row.name">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="数据类型" width="90">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="描述">
          <template #default="{ row }">
            <span class="block truncate" :title="row.description || '-'">{{ row.description || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="必填" width="55">
          <template #default="{ row }">{{ row.required ? '是' : '否' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80">
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
      <el-button plain @click="visible = false">取消</el-button>
      <!-- 提交工具 -->
      <el-button type="primary" @click="handleSubmit">{{ currentIndex !== undefined ? '保存' : '添加' }}</el-button>
    </template>
  </MkDrawer>
</template>
