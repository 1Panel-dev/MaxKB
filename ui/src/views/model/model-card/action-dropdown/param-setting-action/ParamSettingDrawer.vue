<script setup lang="ts">
import { ref } from 'vue'
import type ModelApi from '@/api/admin/workspace/model/model'
import type { DynamicFormField, ModelItem } from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import AdvancedSettingsTable from '../../../advanced-settings-table/AdvancedSettingsTable.vue'

defineOptions({ name: 'ParamSettingDrawer' })

const props = defineProps<{ api: typeof ModelApi }>()

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
      MsgSuccess('保存成功')
      visible.value = false
    })
    .finally(() => {
      loading.value = false
    })
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" direction="btt" title="模型参数设置" @closed="handleClosed">
    <div v-loading="loading" class="mx-auto w-full max-w-200">
      <AdvancedSettingsTable v-model="modelParamsForm" />
    </div>

    <template #footer>
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
    </template>
  </MkDrawer>
</template>
