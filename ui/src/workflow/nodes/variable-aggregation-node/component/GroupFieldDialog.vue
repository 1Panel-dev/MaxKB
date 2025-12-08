<template>
  <el-dialog
    :title="isEdit ? $t('views.applicationWorkflow.nodes.variableAggregationNode.editGroup') : $t('views.applicationWorkflow.nodes.variableAggregationNode.addGroup')"
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
    >
      <el-form-item
        :label="$t('common.variable')"
        prop="field"
      >
        <el-input
          v-model="form.field"
          :maxlength="64"
          :placeholder="$t('views.applicationWorkflow.variable.inputPlaceholder')"
          show-word-limit
        />
      </el-form-item>
      <el-form-item
        :label="$t('dynamicsForm.paramForm.name.label')"
        prop="label"
      >
        <el-input
          v-model="form.label"
          :maxlength="64"
          show-word-limit
          :placeholder="$t('dynamicsForm.paramForm.name.placeholder')"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="close"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(fieldFormRef)" :loading="loading">
          {{ isEdit ? $t('common.save') : $t('common.add') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import { cloneDeep } from 'lodash'
import { t } from '@/locales'
const emit = defineEmits(['refresh'])

const fieldFormRef = ref()
const loading = ref<boolean>(false)
const isEdit = ref(false)
const currentIndex = ref(null)
const form = ref<any>({
  field: '',
  label: '',
})

const rules = reactive({
  label: [
    { required: true, message: t('dynamicsForm.paramForm.name.placeholder'), trigger: 'blur' },
  ],
  field: [
    { required: true, message: t('views.applicationWorkflow.variable.inputPlaceholder'), trigger: 'blur' },
    {
      pattern: /^[a-zA-Z0-9_]+$/,
      message: t('dynamicsForm.paramForm.field.requiredMessage2'),
      trigger: 'blur',
    },
  ],
})

const dialogVisible = ref<boolean>(false)

const open = (data: any, index?: any) => {
  if (data) {
    form.value = cloneDeep(data)
    isEdit.value = true
    currentIndex.value = index
  }

  dialogVisible.value = true
}

const close = () => {
  dialogVisible.value = false
  isEdit.value = false
  currentIndex.value = null
  form.value = {
    field: '',
    label: '',
  }
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      emit('refresh', form.value, currentIndex.value)
    }
  })
}

defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
