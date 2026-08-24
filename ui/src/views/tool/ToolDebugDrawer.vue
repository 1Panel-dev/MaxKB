<script setup lang="ts">
import { computed, nextTick, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { Back } from '@element-plus/icons-vue'
import type { ToolDebugPayload, ToolInitField, ToolPayload } from '@/api/types'
import ToolApi from '@/api/admin/workspace/tool/tool'

defineOptions({ name: 'ToolDebugDrawer' })

const formRef = ref<FormInstance>()
const visible = ref(false)
const loading = ref(false)
const showResult = ref(false)
const debugSucceeded = ref(false)
const debugResult = ref<unknown>()

const debugForm = reactive<ToolDebugPayload>({
  code: '',
  debug_field_list: [],
  init_field_list: [],
  init_params: {},
  input_field_list: [],
})

const formRules = computed<FormRules>(() => {
  const rules: FormRules = {}

  debugForm.init_field_list.forEach((field) => {
    if (field.required) {
      rules[`init_params.${field.field}`] = [
        { required: true, message: `请输入${field.label}`, trigger: 'blur' },
      ]
    }
  })
  debugForm.debug_field_list.forEach((field, index) => {
    if (field.is_required) {
      rules[`debug_field_list.${index}.value`] = [
        { required: true, message: `请输入${field.name}`, trigger: 'blur' },
      ]
    }
  })
  return rules
})

const formattedResult = computed(() => {
  if (debugResult.value === undefined || debugResult.value === null || debugResult.value === '') {
    return '-'
  }
  if (typeof debugResult.value === 'string') return debugResult.value

  try {
    return JSON.stringify(debugResult.value, null, 2)
  } catch {
    return String(debugResult.value)
  }
})

function resetData() {
  debugForm.code = ''
  debugForm.debug_field_list = []
  debugForm.init_field_list = []
  debugForm.init_params = {}
  debugForm.input_field_list = []
  loading.value = false
  showResult.value = false
  debugSucceeded.value = false
  debugResult.value = undefined
  formRef.value?.clearValidate()
}

function open(tool: ToolPayload) {
  resetData()
  debugForm.code = tool.code ?? ''
  debugForm.input_field_list = structuredClone(tool.input_field_list ?? [])
  debugForm.init_field_list = structuredClone(tool.init_field_list ?? [])
  const savedInitParams =
    typeof tool.init_params === 'object' && tool.init_params ? tool.init_params : {}
  debugForm.init_params = {
    ...Object.fromEntries(
      debugForm.init_field_list.map((field) => [field.field, field.default_value ?? '']),
    ),
    ...savedInitParams,
  }
  debugForm.debug_field_list = debugForm.input_field_list.map((field) => ({
    ...field,
    value: '',
  }))
  visible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

function getInitFieldType(field: ToolInitField) {
  if (field.input_type === 'PasswordInput') return 'password'
  if (field.input_type === 'JsonInput') return 'textarea'
  return 'text'
}

function getErrorMessage(error: unknown) {
  if (typeof error === 'object' && error && 'message' in error) {
    return String(error.message)
  }
  return '工具运行失败'
}

function handleRun() {
  formRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    showResult.value = false
    ToolApi.postToolDebug(structuredClone(debugForm))
      .then((result) => {
        debugSucceeded.value = true
        debugResult.value = result
        showResult.value = true
      })
      .catch((error: unknown) => {
        debugSucceeded.value = false
        debugResult.value = getErrorMessage(error)
        showResult.value = true
      })
      .finally(() => {
        loading.value = false
      })
  })
}

defineExpose({ open })
</script>

<template>
  <MkDrawer
    v-model="visible"
    append-to-body
    class="tool-debug-drawer"
    :modal="false"
    :show-close="false"
    size="60%"
    @closed="resetData"
  >
    <template #header>
      <div class="flex items-center gap-1">
        <el-button link @click="visible = false">
          <MkIcon :icon="Back" :size="20" />
        </el-button>
        <h4>调试</h4>
      </div>
    </template>

    <el-form
      ref="formRef"
      :model="debugForm"
      :rules="formRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <section v-if="debugForm.init_field_list.length" class="mb-6">
        <h4 class="mb-4">启动参数</h4>
        <div class="rounded-md border border-N900/10 p-4">
          <el-form-item
            v-for="field in debugForm.init_field_list"
            :key="field.field"
            :label="field.label"
            :prop="`init_params.${field.field}`"
          >
            <el-switch
              v-if="field.input_type === 'SwitchInput'"
              v-model="debugForm.init_params[field.field] as boolean"
            />
            <el-input
              v-else
              v-model="debugForm.init_params[field.field] as string"
              :placeholder="`请输入${field.label}`"
              :show-password="field.input_type === 'PasswordInput'"
              :type="getInitFieldType(field)"
            />
          </el-form-item>
        </div>
      </section>

      <section v-if="debugForm.debug_field_list.length" class="mb-6">
        <h4 class="mb-4">输入参数</h4>
        <div class="rounded-md border border-N900/10 p-4">
          <el-form-item
            v-for="(field, index) in debugForm.debug_field_list"
            :key="`${field.name}-${index}`"
            :prop="`debug_field_list.${index}.value`"
          >
            <template #label>
              <span class="inline-flex items-center gap-2">
                {{ field.name }}
                <el-tag size="small" type="info">{{ field.type }}</el-tag>
              </span>
            </template>
            <el-input v-model="field.value" :placeholder="`请输入${field.name}`" />
          </el-form-item>
        </div>
      </section>
    </el-form>

    <section v-if="showResult">
      <h4 class="mb-4">运行结果</h4>
      <el-alert
        :closable="false"
        :title="debugSucceeded ? '运行成功' : '运行失败'"
        :type="debugSucceeded ? 'success' : 'error'"
        class="mb-4"
        show-icon
      />
      <p class="mb-2 text-N600">输出</p>
      <pre
        class="max-h-80 overflow-auto whitespace-pre-wrap rounded-md border border-N900/10 p-4"
        :class="{ 'text-danger': !debugSucceeded }"
        >{{ formattedResult }}</pre
      >
    </section>

    <template #footer>
      <el-button @click="visible = false">返回</el-button>
      <el-button type="primary" :loading="loading" @click="handleRun">运行</el-button>
    </template>
  </MkDrawer>
</template>

<style scoped lang="scss">
:deep(.tool-debug-drawer .el-drawer__footer),
:deep(.tool-debug-drawer .el-drawer__header) {
  border-color: var(--el-border-color-lighter);
  border-style: solid;
  margin-bottom: 0;
  padding: calc(var(--spacing) * 4) calc(var(--spacing) * 6);
}

:deep(.tool-debug-drawer .el-drawer__footer) {
  border-top-width: 1px;
}

:deep(.tool-debug-drawer .el-drawer__header) {
  border-bottom-width: 1px;
}
</style>
