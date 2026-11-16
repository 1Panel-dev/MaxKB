<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ref } from 'vue'
import type ModelApi from '@/api/admin/workspace/model'
import type SystemResourceModelApi from '@/api/admin/system/resource-management/model'
import type SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import type { DynamicFormField, ModelItem } from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import AdvancedSettingsTable from '@/views/model/advanced-settings-table/AdvancedSettingsTable.vue'

defineOptions({ name: 'ParamSettingDrawer' })

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ api: typeof ModelApi | typeof SystemSharedModelApi | typeof SystemResourceModelApi }>()

const emit = defineEmits<{ closed: [] }>()

const visible = ref(false)
const loading = ref(false)
const currentModel = ref<ModelItem>()
const modelParamsForm = ref<DynamicFormField[]>([])

function resetData() {
  currentModel.value = undefined
  modelParamsForm.value = []
  loading.value = false
}

function handleClosed() {
  resetData()
  emit('closed')
}

function open(model: ModelItem) {
  currentModel.value = model
  visible.value = true
  loading.value = true
  props.api
    .getModelParamsForm(model.id)
    .then((paramsForm) => {
      modelParamsForm.value = paramsForm
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSubmit() {
  if (!currentModel.value) return

  loading.value = true
  props.api
    .putModelParamsForm(currentModel.value.id, modelParamsForm.value)
    .then(() => {
      MsgSuccess(t('common.messages.saved'))
      visible.value = false
    })
    .finally(() => {
      loading.value = false
    })
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" direction="btt" :title="t('model.actions.parameterSettings')" @closed="handleClosed">
    <div v-loading="loading" class="mx-auto w-full max-w-200">
      <AdvancedSettingsTable v-model="modelParamsForm" />
    </div>

    <template #footer>
      <el-button plain :disabled="loading" @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">{{ t('common.actions.save') }}</el-button>
    </template>
  </MkDrawer>
</template>
