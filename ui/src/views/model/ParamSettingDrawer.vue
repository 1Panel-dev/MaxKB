<script setup lang="ts">
import { ref } from 'vue'
import type { DynamicFormField, ModelItem } from '@/api/types'
import ModelApi from '@/api/admin/workspace/model/model'
import { MsgSuccess } from '@/utils/message'
import AdvancedSettingsTable from './components/advanced-settings/AdvancedSettingsTable.vue'

defineOptions({ name: 'ParamSettingDrawer' })

const visible = ref(false)
const loading = ref(false)
const currentModel = ref<ModelItem>()
const modelParamsForm = ref<DynamicFormField[]>([])

function resetData() {
  currentModel.value = undefined
  modelParamsForm.value = []
  loading.value = false
}

function open(model: ModelItem) {
  resetData()
  currentModel.value = model
  visible.value = true
  loading.value = true
  ModelApi.getModelParamsForm(model.id)
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
  ModelApi.putModelParamsForm(currentModel.value.id, modelParamsForm.value)
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
  <MkDrawer v-model="visible" direction="btt" title="模型参数设置" @closed="resetData">
    <div v-loading="loading" class="mx-auto w-full max-w-200">
      <AdvancedSettingsTable v-model="modelParamsForm" />
    </div>

    <template #footer>
      <el-button :disabled="loading" @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
    </template>
  </MkDrawer>
</template>
