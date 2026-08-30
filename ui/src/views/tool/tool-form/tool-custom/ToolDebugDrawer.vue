<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import type { ToolDebugPayload, ToolPayload } from '@/api/types'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import { MkDynamicsForm } from '@/components/mk-dynamics-form'

defineOptions({ name: 'ToolDebugDrawer' })

const props = defineProps<{ api: typeof ToolApi }>()

const formRef = ref<FormInstance>()
const dynamicsFormRef = ref<InstanceType<typeof MkDynamicsForm>>()
const visible = ref(false)
const loading = ref(false)
const showResult = ref(false)
const debugSucceeded = ref(false)
const debugResult = ref<unknown>()

const debugForm = reactive<ToolDebugPayload>({ code: '', debug_field_list: [], init_field_list: [], init_params: {}, input_field_list: [] })

const formRules = computed<FormRules>(() => {
  const rules: FormRules = {}

  debugForm.debug_field_list.forEach((field, index) => {
    if (field.is_required) {
      rules[`debug_field_list.${index}.value`] = [{ required: true, message: `请输入${field.name}`, trigger: 'blur' }]
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

function open(tool: ToolPayload) {
  resetData()
  debugForm.code = tool.code ?? ''
  debugForm.input_field_list = cloneDeep(tool.input_field_list ?? [])
  debugForm.init_field_list = cloneDeep(tool.init_field_list ?? [])
  const savedInitParams = typeof tool.init_params === 'object' && tool.init_params ? tool.init_params : {}
  debugForm.init_params = cloneDeep(savedInitParams)
  debugForm.debug_field_list = debugForm.input_field_list.map((field) => ({ ...field, value: '' }))
  visible.value = true
}

function getErrorMessage(error: unknown) {
  if (typeof error === 'object' && error && 'message' in error) {
    return String(error.message)
  }
  return '工具运行失败'
}

function handleRun() {
  Promise.all([dynamicsFormRef.value?.validate() ?? Promise.resolve(), formRef.value?.validate() ?? Promise.resolve(true)])
    .then(() => {
      loading.value = true
      showResult.value = false

      return props.api
        .postToolDebug(cloneDeep(debugForm))
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
    .catch(() => {})
}

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

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" append-to-body class="tool-debug-drawer" :modal="false" :show-close="false" size="60%" @closed="resetData">
    <template #header>
      <div class="-ml-2 flex items-center">
        <el-button class="mr-1" text @click="visible = false">
          <MkIcon name="icon_arrow-left_outlined" :size="20" />
        </el-button>
        <h4>调试</h4>
      </div>
    </template>

    <section v-if="debugForm.init_field_list.length" class="mb-6">
      <h4 class="mk-title-decoration mb-4">启动参数</h4>

      <MkDynamicsForm ref="dynamicsFormRef" v-model="debugForm.init_params" :render-data="debugForm.init_field_list" />
    </section>

    <section v-if="debugForm.debug_field_list.length" class="mb-6">
      <h4 class="mk-title-decoration mb-4">输入参数</h4>

      <el-form
        ref="formRef"
        v-loading="loading"
        :model="debugForm"
        :rules="formRules"
        hide-required-asterisk
        label-position="top"
        require-asterisk-position="right"
        @submit.prevent
      >
        <el-form-item v-for="(field, index) in debugForm.debug_field_list" :key="`${field.name}-${index}`" :prop="`debug_field_list.${index}.value`">
          <template #label>
            <span class="inline-flex items-center gap-2">
              <span :class="field.is_required ? 'mk-required' : ''">
                {{ field.name }}
              </span>
              <el-tag size="small" type="info">{{ field.type }}</el-tag>
            </span>
          </template>
          <el-input v-model="field.value" :placeholder="`请输入 ${field.name}`" />
        </el-form-item>
      </el-form>
    </section>

    <el-button type="primary" :loading="loading" @click="handleRun">运行</el-button>

    <section v-if="showResult" class="mt-4">
      <h4 class="mk-title-decoration mb-4">运行结果</h4>
      <el-alert :closable="false" :title="debugSucceeded ? '运行成功' : '运行失败'" :type="debugSucceeded ? 'success' : 'error'" class="mb-4" show-icon />
      <p class="mb-2">输出</p>
      <pre class="whitespace-pre-wrap rounded-md border p-2" :class="{ 'border-danger': !debugSucceeded }">{{ formattedResult }}</pre>
    </section>
  </MkDrawer>
</template>
