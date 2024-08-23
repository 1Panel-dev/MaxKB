<template>
  <el-dialog
    align-center
    :title="$t('views.application.applicationForm.dialogues.paramSettings')"
    class="aiMode-param-dialog"
    v-model="dialogVisible"
    style="width: 550px"
    append-to-body
  >
    <DynamicsForm
      v-model="form_data"
      :model="form_data"
      label-position="top"
      require-asterisk-position="right"
      :render_data="model_form_field"
      ref="dynamicsFormRef"
    >
    </DynamicsForm>

    <template #footer>
      <span class="dialog-footer p-16">
        <el-button @click.prevent="dialogVisible = false">
          {{ $t('views.application.applicationForm.buttons.cancel') }}
        </el-button>
        <el-button type="primary" @click="submit" :loading="loading">
          {{ $t('views.application.applicationForm.buttons.confirm') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import type { FormInstance } from 'element-plus'
import type { FormField } from '@/components/dynamics-form/type'
import modelAPi from '@/api/model'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import { keys } from 'lodash'
const model_form_field = ref<Array<FormField>>([])
const emit = defineEmits(['refresh'])
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const form_data = ref<any>({})
const dialogVisible = ref(false)
const loading = ref(false)

const open = (model_id: string, model_setting_data?: any) => {
  modelAPi.getModelParamsForm(model_id, loading).then((ok) => {
    model_form_field.value = ok.data
    model_setting_data =
      model_setting_data && keys(model_setting_data).length > 0
        ? model_setting_data
        : ok.data
            .map((item) => ({ [item.field]: item.default_value }))
            .reduce((x, y) => ({ ...x, ...y }), {})
    // 渲染动态表单
    dynamicsFormRef.value?.render(model_form_field.value, model_setting_data)
  })
  dialogVisible.value = true
}

const submit = async () => {
  emit('refresh', form_data.value)
  dialogVisible.value = false
}

defineExpose({ open })
</script>

<style lang="scss" scoped>
.aiMode-param-dialog {
  padding: 8px 8px 24px 8px;

  .el-dialog__header {
    padding: 16px 16px 0 16px;
  }

  .el-dialog__body {
    padding: 16px !important;
  }

  .dialog-max-height {
    height: 550px;
  }

  .custom-slider {
    .el-input-number.is-without-controls .el-input__wrapper {
      padding: 0 !important;
    }
  }
}
</style>
