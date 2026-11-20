<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type WorkflowApi from '@/api/admin/workspace/tool/workflow'
import type { ToolInputField } from '@/workflow-canvas/nodes/tool-base-node/types'
import type LogicFlow from '@logicflow/core'
import type { FormInstance, FormItemRule } from 'element-plus'
import type { ComponentPublicInstance } from 'vue'
import JsonInput from '@/components/codemirror-editor/Json.vue'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import ResultDrawer from './ResultDrawer.vue'

defineOptions({ name: 'ToolWorkflowDebugDrawer' })
const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ toolId: string; api?: typeof WorkflowApi }>()
const visible = ref(false)
const inputFields = ref<ToolInputField[]>([])
const inputValues = ref<Record<string, unknown>>({})
const formRef = useTemplateRef<FormInstance>('formRef')
const resultDrawerRef = useTemplateRef<InstanceType<typeof ResultDrawer>>('resultDrawerRef')
const running = ref(false)
const jsonInputRefs = new Map<string, InstanceType<typeof JsonInput>>()

function setJsonInputRef(field: string, instance: Element | ComponentPublicInstance | null) {
  if (instance) jsonInputRefs.set(field, instance as InstanceType<typeof JsonInput>)
  else jsonInputRefs.delete(field)
}

/* 参数取自调试前已保存的画布快照，不再重复查询工具详情。 */
function open(graph: LogicFlow.GraphData) {
  if (running.value) return
  const baseNode = graph.nodes.find((node) => node.id === WorkflowNodeType.ToolBaseNode)
  inputFields.value = cloneDeep((baseNode?.properties?.user_input_field_list as ToolInputField[] | undefined) ?? [])
  inputValues.value = Object.fromEntries(
    inputFields.value.map((field) => [
      field.field,
      field.type === 'boolean' ? false : field.type === 'array' ? [] : field.type === 'dict' ? {} : undefined,
    ]),
  )
  visible.value = true
}

function fieldRules(field: ToolInputField): FormItemRule[] {
  return [
    // 必填规则覆盖 change、blur 和提交校验，避免 FormItem 自动补充无文案的 required 规则。
    { required: field.is_required, message: t('common.validation.inputRequired') },
    {
      validator: (_rule, value, callback) => {
        if (field.type === 'array' || field.type === 'dict') {
          jsonInputRefs.get(field.field)?.validateRules(_rule, value, (error) => {
            if (error) {
              callback(error)
              return
            }
            const valid = field.type === 'array' ? Array.isArray(value) : value !== null && typeof value === 'object' && !Array.isArray(value)
            callback(
              valid
                ? undefined
                : new Error(field.type === 'array' ? t('common.validation.jsonArrayRequired') : t('common.validation.jsonObjectRequired')),
            )
          })
          return
        }
        if (value === undefined || value === '') {
          callback(field.is_required ? new Error(t('common.validation.inputRequired')) : undefined)
          return
        }
        callback()
      },
      trigger: 'blur',
    },
  ]
}

async function handleRun() {
  if (running.value) return
  if (formRef.value && !(await formRef.value.validate().catch(() => false))) return
  const parameters: Record<string, unknown> = {}
  for (const field of inputFields.value) {
    const value = inputValues.value[field.field]
    if (value === undefined || value === '') continue
    parameters[field.field] = cloneDeep(value)
  }
  resultDrawerRef.value?.open(parameters)
}

function close() {
  resultDrawerRef.value?.close()
  visible.value = false
}

function reset() {
  inputFields.value = []
  inputValues.value = {}
}

defineExpose({ open, close })
</script>

<template>
  <MkDrawer v-model="visible" :title="t('common.actions.debug')" @closed="reset">
    <h4 v-if="inputFields.length" class="mk-title-decoration mb-4">{{ t('execution.details.inputParams') }}</h4>
    <el-form
      ref="formRef"
      :model="inputValues"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <template v-for="field in inputFields" :key="field.field">
        <el-form-item class="mk-hide-asterisk" :prop="field.field" :rules="fieldRules(field)" :required="field.is_required">
          <template #label>
            <span :class="field.is_required ? 'mk-required' : ''">{{ field.label || field.field }}</span>
            <el-tag type="info" size="small" class="ml-2">{{ field.type }}</el-tag>
          </template>
          <JsonInput
            v-if="['array', 'dict'].includes(field.type)"
            :ref="(instance) => setJsonInputRef(field.field, instance)"
            v-model="inputValues[field.field]"
          />
          <el-input-number
            v-else-if="['int', 'float'].includes(field.type)"
            v-model="inputValues[field.field]"
            :precision="field.type === 'int' ? 0 : undefined"
          />
          <el-switch v-else-if="field.type === 'boolean'" v-model="inputValues[field.field]" />
          <el-input v-else v-model="inputValues[field.field]" :placeholder="t('dynamicForm.fields.parameter.placeholder')" />
        </el-form-item>
      </template>
    </el-form>
    <template #footer>
      <!-- 关闭调试 -->
      <el-button plain @click="close">{{ t('common.actions.cancel') }}</el-button>
      <!-- 运行工具工作流 -->
      <el-button type="primary" :loading="running" @click="handleRun">{{ t('tool.debug.run') }}</el-button>
    </template>
  </MkDrawer>
  <ResultDrawer :api="api" ref="resultDrawerRef" :tool-id="props.toolId" v-model:running="running" />
</template>
