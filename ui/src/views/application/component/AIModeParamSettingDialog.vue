<template>
  <el-dialog
    align-center
    :title="$t('common.paramSetting')"
    v-model="dialogVisible"
    style="width: 550px"
    append-to-body
    destroy-on-close
    :close-on-click-modal="false"
    :close-on-press-escape="false"
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
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">
          {{ $t('common.cancel') }}
        </el-button>
        <el-button
          type="primary"
          @click="submit"
          :loading="loading"
          v-if="permissionPrecise.paramSetting(modelID)"
        >
          {{ $t('common.confirm') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { FormField } from '@/components/dynamics-form/type'
import { useRoute } from 'vue-router'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import permissionMap from '@/permission'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

const route = useRoute()
const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const model_form_field = ref<Array<FormField>>([])
const emit = defineEmits(['refresh'])
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const form_data = ref<any>({})
const dialogVisible = ref(false)
const loading = ref(false)
const getApi = (model_id: string, application_id?: string) => {
  return loadSharedApi({ type: 'model', systemType: apiType.value }).getModelParamsForm(
    model_id,
    loading,
  )
}

const modelID = ref('')

const permissionPrecise = computed(() => {
  return permissionMap['model'][apiType.value]
})

const open = (model_id: string, application_id?: string, model_setting_data?: any) => {
  modelID.value = model_id
  form_data.value = {}
  const api = getApi(model_id, application_id)
  api.then((ok: any) => {
    model_form_field.value = ok.data
    // 渲染动态表单
    dynamicsFormRef.value?.render(model_form_field.value, model_setting_data)
  })
  dialogVisible.value = true
}

const reset_default = (model_id: string, application_id?: string) => {
  const api = getApi(model_id, application_id)
  api.then((ok: any) => {
    model_form_field.value = ok.data
    const model_setting_data = ok.data
      .map((item: any) => {
        if (item.show_default_value === false) {
          return { [item.field]: undefined }
        } else {
          return { [item.field]: item.default_value }
        }
      })
      .reduce((x: any, y: any) => ({ ...x, ...y }), {})

    emit('refresh', model_setting_data)
  })
}

const submit = async () => {
  dynamicsFormRef.value?.validate().then(() => {
    emit('refresh', form_data.value)
    dialogVisible.value = false
  })
}

defineExpose({ open, reset_default })
</script>

<style lang="scss" scoped></style>
