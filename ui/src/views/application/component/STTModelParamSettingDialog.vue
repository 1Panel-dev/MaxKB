<template>
    <el-dialog
      align-center
      :title="$t('common.paramSetting')"
      v-model="dialogVisible"
      style="width: 550px"
      append-to-body
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
      <div class="flex-between">
        <span class="dialog-footer">
          <el-button @click.prevent="dialogVisible = false">
            {{ $t('common.cancel') }}
          </el-button>
          <el-button type="primary" @click="submit" :loading="loading">
            {{ $t('common.confirm') }}
          </el-button>
        </span>
      </div>
    </template>
    </el-dialog>
</template>



<script setup lang="ts">
import type { FormField } from '@/components/dynamics-form/type'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'


const route = useRoute()

const {
  params: { id }
} = route as any
const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const dialogVisible = ref<boolean>(false)
const form_data = ref<any>({})
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const stt_model_id = ref<string>('')
const loading = ref<boolean>(false)
const model_form_field = ref<Array<FormField>>([])
const emit = defineEmits(['refresh'])

const open = (model_id: string, application_id?: string, model_setting_data?: any) => {
  form_data.value = {}
  stt_model_id.value = model_id
  loadSharedApi({ type: 'model', systemType: apiType.value })
    .getModelParamsForm(model_id, loading)  
    .then(( ok: any ) => {
      model_form_field.value = ok.data
      const resp = ok.data
        .map((item: any) => ({
          [item.field]: item.show_default_value !== false ? item.default_value : undefined,
        }))
        .reduce((x: any, y: any) => ({ ...x, ...y }), {})

      if (model_setting_data) {
        Object.keys(model_setting_data).forEach((key) => {
          if (!(key in resp)) {
            delete model_setting_data[key]
          }
        })
      }
      model_setting_data = { ...resp, ...model_setting_data }
      // 渲染动态表单
      dynamicsFormRef.value?.render(model_form_field.value, model_setting_data)
    })
  dialogVisible.value = true
}

const submit = async () => {
  dynamicsFormRef.value?.validate().then(() => {
      emit('refresh', form_data.value)
      dialogVisible.value = false
  })
}

const reset_default = (model_id: string, application_id?: string) => {
  loadSharedApi({ type: 'model', systemType: apiType.value })
    .getModelParamsForm(model_id, loading)
    .then((ok: any) => {
      model_form_field.value = ok.data
      const model_setting_data = ok.data
        .map((item: any) => ({
          [item.field]: item.show_default_value !== false ? item.default_value : undefined,
        }))
        .reduce((x: any, y: any) => (({ ...x, ...y })), {})

        emit('refresh', model_setting_data)
    })
}



defineExpose({ open, reset_default })

</script>

<style lang="scss" scoped></style>