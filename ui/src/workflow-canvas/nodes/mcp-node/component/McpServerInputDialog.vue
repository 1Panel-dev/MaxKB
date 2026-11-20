<script setup lang="ts">
import { reactive, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { FormInstance } from 'element-plus'

defineOptions({ name: 'McpServerInputDialog' })
const { t } = useI18n({ useScope: 'global' })

const emit = defineEmits<{ refresh: [value: Record<string, string>] }>()

const dialogVisible = ref(false)
const loading = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const form = reactive<Record<string, string>>({})

const inputFieldList = ref<string[]>([])

function open(vars: string[]) {
  inputFieldList.value = vars
  dialogVisible.value = true
}

function resetData() {
  Object.keys(form).forEach((key) => delete form[key])
  inputFieldList.value = []
  formRef.value?.clearValidate()
}

const submit = async (formEl: FormInstance | null) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      emit('refresh', { ...form })
      dialogVisible.value = false
    }
  })
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" :title="t('workflow.mcp.variables.title')" @closed="resetData">
    <el-form ref="formRef" label-position="top" :model="form" :validate-on-rule-change="false" require-asterisk-position="right" @submit.prevent>
      <el-form-item
        v-for="item in inputFieldList"
        :key="item"
        :label="item"
        :prop="item"
        :rules="{ required: true, message: t('common.validation.inputRequired'), trigger: 'blur' }"
      >
        <el-input v-model="form[item]" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <!-- 取消变量设置 -->
        <el-button plain @click.prevent="dialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
        <!-- 保存变量设置 -->
        <el-button type="primary" :loading="loading" @click="submit(formRef)">{{ t('common.actions.save') }}</el-button>
      </span>
    </template>
  </MkDialog>
</template>
<style lang="scss" scoped></style>
