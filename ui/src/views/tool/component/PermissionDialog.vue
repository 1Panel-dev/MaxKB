<template>
  <el-dialog
    :title="$t('views.functionLib.functionForm.form.permission_type.label')"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    append-to-body
    width="450"
  >
    <el-form
      label-position="top"
      ref="fieldFormRef"
      :rules="rules"
      :model="form"
      require-asterisk-position="right"
    >
      <el-radio-group v-model="form.permission_type" class="radio-block">
        <el-radio value="PRIVATE" size="large">
          {{ $t('common.private') }}
          <el-text type="info">{{
            $t('views.template.templateForm.form.permissionType.privateDesc')
          }}</el-text>
        </el-radio>
        <el-radio value="PUBLIC" size="large">
          {{ $t('common.public') }}
          <el-text type="info">{{
            $t('views.template.templateForm.form.permissionType.publicDesc')
          }}</el-text>
        </el-radio>
      </el-radio-group>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(fieldFormRef)" :loading="loading">
          {{ isEdit ? $t('common.save') : $t('common.add') }}
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
import functionLibApi from '@/api/function-lib'
import { MsgSuccess } from '@/utils/message'

const emit = defineEmits(['refresh'])

const fieldFormRef = ref()
const loading = ref<boolean>(false)
const isEdit = ref(false)

const form = ref<any>({
  permission_type: 'PRIVATE'
})

const rules = reactive({
  permission_type: [
    {
      required: true,
      message: t('views.functionLib.functionForm.form.paramName.placeholder'),
      trigger: 'blur'
    }
  ]
})

const dialogVisible = ref<boolean>(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      permission_type: 'PRIVATE'
    }
    isEdit.value = false
  }
})

const open = (row: any) => {
  if (row) {
    form.value = cloneDeep(row)
    isEdit.value = true
  }

  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      functionLibApi.putFunctionLib(form.value?.id as string, form.value, loading).then((res) => {
        MsgSuccess(t('common.editSuccess'))
        emit('refresh')
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
