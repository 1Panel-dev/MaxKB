<script setup lang="ts">
import { computed, ref } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { FormInstance, FormRules } from 'element-plus'
import { isLoopBuiltinField } from '../constant'

defineOptions({ name: 'LoopFieldDialog' })
const { t } = useI18n({ useScope: 'global' })

type LoopInputField = { field: string; label: string }
const emit = defineEmits<{ submit: [data: LoopInputField, index?: number] }>()

// 参数表单与校验。
const fieldFormRef = ref<FormInstance>()
const form = ref<LoopInputField>({ field: '', label: '' })
const rules = computed<FormRules<LoopInputField>>(() => ({
  field: [
    { whitespace: true, required: true, message: t('dynamicForm.fields.parameter.requiredMessage'), trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: t('workflow.loopStart.variables.invalidMessage'), trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        if (isLoopBuiltinField(value)) {
          callback(new Error(t('workflow.loopStart.variables.reservedMessage')))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  label: [{ whitespace: true, required: true, message: t('dynamicForm.fields.displayName.requiredMessage'), trigger: 'blur' }],
}))

// 打开时初始化，关闭动画结束后清理编辑状态。
const dialogVisible = ref(false)
const currentIndex = ref<number>()
const isEdit = computed(() => currentIndex.value !== undefined)

function open(row?: LoopInputField, index?: number) {
  form.value = row ? cloneDeep(row) : { field: '', label: '' }
  currentIndex.value = index
  dialogVisible.value = true
}

function close() {
  dialogVisible.value = false
}

function resetData() {
  currentIndex.value = undefined
  form.value = { field: '', label: '' }
  fieldFormRef.value?.clearValidate()
}

// 表格负责重名检查、写回和成功后的关闭。
async function submit() {
  const valid = await fieldFormRef.value?.validate().catch(() => false)
  if (!valid) return
  emit('submit', cloneDeep(form.value), currentIndex.value)
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog :title="isEdit ? t('common.parameters.edit') : t('common.parameters.add')" v-model="dialogVisible" @closed="resetData">
    <el-form
      label-position="top"
      ref="fieldFormRef"
      :rules="rules"
      :model="form"
      :validate-on-rule-change="false"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('dynamicForm.fields.parameter.label')" prop="field">
        <el-input v-model="form.field" :maxlength="64" :placeholder="t('dynamicForm.fields.parameter.placeholder')" show-word-limit />
      </el-form-item>
      <el-form-item :label="t('dynamicForm.fields.displayName.label')" prop="label">
        <el-input v-model="form.label" :maxlength="64" show-word-limit :placeholder="t('dynamicForm.fields.displayName.placeholder')" />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消编辑循环变量 -->
      <el-button plain @click="close">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存循环变量 -->
      <el-button type="primary" @click="submit">{{ isEdit ? t('common.actions.save') : t('common.actions.add') }}</el-button>
    </template>
  </MkDialog>
</template>
