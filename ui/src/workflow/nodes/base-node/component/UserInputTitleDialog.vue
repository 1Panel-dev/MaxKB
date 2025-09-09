<template>
  <el-dialog
    :title="$t('common.setting')"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
    append-to-body
  >
    <el-form
      label-position="top"
      ref="fieldFormRef"
      :rules="rules"
      :model="form"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="$t('common.title')" prop="title">
        <el-input
          v-model="form.title"
          maxlength="64"
          show-word-limit
          @blur="form.title = form.title.trim()"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(fieldFormRef)" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import { cloneDeep } from 'lodash'
import { t } from '@/locales'
const emit = defineEmits(['refresh'])

const fieldFormRef = ref()
const loading = ref<boolean>(false)

const form = ref<any>({
  title: t('chat.userInput'),
})

const rules = reactive({
  title: [
    { required: true, message: t('dynamicsForm.paramForm.name.requiredMessage'), trigger: 'blur' },
  ],
})

const dialogVisible = ref<boolean>(false)

const open = (row: any) => {
  if (row) {
    form.value = cloneDeep(row)
  }

  dialogVisible.value = true
}

const close = () => {
  dialogVisible.value = false
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      emit('refresh', form.value)
    }
  })
}

defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
