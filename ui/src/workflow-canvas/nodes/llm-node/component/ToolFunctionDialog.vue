<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormItemRule } from 'element-plus'
import { normalizeTool, toolParameterTypes, type LlmTool, type LlmToolFunction, type LlmToolParameter } from '../types'

defineOptions({ name: 'WorkflowLlmToolFunctionDialog' })

const props = defineProps<{ existingNames: string[] }>()
const emit = defineEmits<{ submit: [tool: LlmTool, index?: number] }>()

interface ToolFunctionForm {
  name: string
  description: string
  parameters: LlmToolParameter[]
}

const formRef = useTemplateRef<FormInstance>('formRef')
const visible = ref(false)
const editing = ref(false)
const editingName = ref('')
const currentIndex = ref<number>()
const functionForm = ref<ToolFunctionForm>({ name: '', description: '', parameters: [] })
const showParse = ref(false)
const parseJson = ref('')
const parseError = ref('')

const nameRules: FormItemRule[] = [
  { whitespace: true, required: true, message: '请输入函数名称', trigger: 'blur' },
  {
    validator: (_rule, value: string, callback) => {
      const duplicated = props.existingNames.includes(value) && !(editing.value && value === editingName.value)
      callback(duplicated ? new Error('函数名称已存在') : undefined)
    },
    trigger: 'blur',
  },
]

function parameterNameRules(index: number): FormItemRule[] {
  return [
    { whitespace: true, required: true, message: '请输入参数名', trigger: 'blur' },
    {
      validator: (_rule, value: string, callback) => {
        const duplicated = functionForm.value.parameters.some((parameter, i) => i !== index && parameter.name === value)
        callback(duplicated ? new Error('参数名重复') : undefined)
      },
      trigger: 'blur',
    },
  ]
}

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

// 弹窗仅维护函数草稿，节点接收提交后关闭。
function open(tool?: LlmTool, index?: number) {
  if (tool) {
    editing.value = true
    editingName.value = tool.function.name
    currentIndex.value = index
    functionForm.value = {
      name: tool.function.name,
      description: tool.function.description,
      parameters: toParameters(cloneDeep(tool.function.parameters)),
    }
  }
  visible.value = true
}

function close() {
  visible.value = false
}

function parseFromJson() {
  parseError.value = ''
  try {
    const tool = normalizeTool(JSON.parse(parseJson.value))
    if (!tool) {
      parseError.value = '未找到函数名称'
      return
    }
    functionForm.value = {
      name: tool.function.name,
      description: tool.function.description,
      parameters: toParameters(tool.function.parameters),
    }
    showParse.value = false
    formRef.value?.clearValidate()
  } catch {
    parseError.value = 'JSON 解析失败，请检查格式'
  }
}

function addParameter() {
  functionForm.value.parameters.push({ name: '', type: 'string', description: '', required: false })
}

function removeParameter(index: number) {
  functionForm.value.parameters.splice(index, 1)
}

function handleSubmit() {
  formRef.value
    ?.validate()
    .then(() => {
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
  editing.value = false
  editingName.value = ''
  currentIndex.value = undefined
  functionForm.value = { name: '', description: '', parameters: [] }
  showParse.value = false
  parseJson.value = ''
  parseError.value = ''
  formRef.value?.clearValidate()
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="visible" :title="editing ? '编辑函数' : '添加函数'" @closed="resetData">
    <div class="mb-2 flex justify-end">
      <!-- 切换 JSON 解析区 -->
      <el-button text type="primary" @click="showParse = !showParse">解析 JSON</el-button>
    </div>
    <div v-if="showParse" class="mb-4">
      <el-input
        v-model="parseJson"
        type="textarea"
        :rows="6"
        placeholder='粘贴函数定义 JSON，例如：{"name": "get_weather", "description": "获取天气", "parameters": {...}}'
      />
      <div class="flex-align-center mt-2 gap-2">
        <!-- 从 JSON 回填函数 -->
        <el-button type="primary" size="small" @click="parseFromJson">解析</el-button>
        <span v-if="parseError" class="text-sm text-[var(--el-color-danger)]">{{ parseError }}</span>
      </div>
    </div>

    <el-form ref="formRef" :model="functionForm" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="函数名称" prop="name" :rules="nameRules">
        <el-input v-model="functionForm.name" maxlength="64" placeholder="例如：get_weather" @blur="functionForm.name = functionForm.name.trim()" />
      </el-form-item>
      <el-form-item label="函数描述" prop="description" :rules="{ whitespace: true, required: true, message: '请输入函数描述', trigger: 'blur' }">
        <el-input v-model="functionForm.description" type="textarea" :rows="2" placeholder="描述函数的功能" />
      </el-form-item>

      <div class="flex-between mb-2">
        <span>参数列表</span>
        <!-- 添加参数 -->
        <el-button text type="primary" @click="addParameter">
          <MkIcon name="icon_add_outlined" />
        </el-button>
      </div>
      <div v-for="(parameter, index) in functionForm.parameters" :key="index" class="flex items-start gap-2">
        <el-form-item class="w-1/4" :prop="`parameters.${index}.name`" :rules="parameterNameRules(index)">
          <el-input v-model="parameter.name" placeholder="参数名" @blur="parameter.name = parameter.name.trim()" />
        </el-form-item>
        <el-form-item class="w-1/5">
          <el-select v-model="parameter.type">
            <el-option v-for="parameterType in toolParameterTypes" :key="parameterType" :label="parameterType" :value="parameterType" />
          </el-select>
        </el-form-item>
        <el-form-item class="min-w-0 flex-1">
          <el-input v-model="parameter.description" placeholder="描述" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="parameter.required">必填</el-checkbox>
        </el-form-item>
        <!-- 删除参数 -->
        <el-button text type="primary" class="mt-1" @click="removeParameter(index)">
          <MkIcon name="icon_delete-trash_outlined" />
        </el-button>
      </div>
      <div v-if="!functionForm.parameters.length" class="text-N600 text-sm">暂无参数</div>
    </el-form>

    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">{{ editing ? '保存' : '添加' }}</el-button>
    </template>
  </MkDialog>
</template>
