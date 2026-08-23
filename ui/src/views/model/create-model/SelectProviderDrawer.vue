<script setup lang="ts">
import { ref } from 'vue'
import type { ModelProviderItem } from '@/api/types'
import ProviderApi from '@/api/admin/workspace/model/provider'
import { MODEL_TYPE_LABELS } from '@/constants'

defineOptions({ name: 'SelectProviderDrawer' })

const props = defineProps<{
  providers: ModelProviderItem[]
}>()
const emit = defineEmits<{
  select: [provider: ModelProviderItem]
}>()

const visible = ref(false)
const modelType = ref('all')
const loading = ref(false)
const providerOptions = ref<ModelProviderItem[]>([])

function resetData() {
  modelType.value = 'all'
  loading.value = false
  providerOptions.value = []
}

function open() {
  resetData()
  providerOptions.value = props.providers
  visible.value = true
}

function close() {
  visible.value = false
  resetData()
}

function handleProviderSelect(provider: ModelProviderItem) {
  close()
  emit('select', provider)
}

function handleModelTypeChange(value: string) {
  if (value === 'all') {
    providerOptions.value = props.providers
    return
  }

  loading.value = true
  ProviderApi.getProviderListByModelType(value)
    .then((providers) => {
      providerOptions.value = providers
    })
    .finally(() => {
      loading.value = false
    })
}

defineExpose({ open, close })
</script>

<template>
  <MkDrawer
    v-model="visible"
    class="create-model-step-drawer"
    direction="btt"
    size="calc(100% - 68px)"
    title="添加模型"
    @closed="resetData"
  >
    <template #header>
      <div class="grid w-full grid-cols-[1fr_460px_1fr] items-center pr-8">
        <h4>添加模型</h4>
        <el-steps :active="0" align-center>
          <el-step title="选择供应商" />
          <el-step title="添加模型" />
        </el-steps>
      </div>
    </template>

    <div class="mx-auto w-full max-w-[1110px] px-6 py-8">
      <div class="mb-5 flex items-center justify-between">
        <h4>选择供应商</h4>
        <el-select v-model="modelType" class="w-52" @change="handleModelTypeChange">
          <el-option label="全部模型" value="all" />
          <el-option
            v-for="(label, value) in MODEL_TYPE_LABELS"
            :key="value"
            :label="label"
            :value="value"
          />
        </el-select>
      </div>

      <div v-loading="loading" class="grid min-h-24 grid-cols-2 gap-5">
        <button
          v-for="provider in providerOptions"
          :key="provider.provider"
          type="button"
          class="flex h-[78px] cursor-pointer items-center rounded-lg border border-N900/20 px-6 text-left transition-colors hover:border-primary hover:text-primary"
          @click="handleProviderSelect(provider)"
        >
          <span class="h-7 w-7 shrink-0" :innerHTML="provider.icon" />
          <span class="ml-4 text-lg font-medium">{{ provider.name }}</span>
        </button>
      </div>

      <MkEmpty v-if="!providerOptions.length" class="mt-24" />
    </div>
  </MkDrawer>
</template>

<style scoped lang="scss">
:deep(.create-model-step-drawer .el-drawer__body .p-6) {
  min-height: 100%;
  padding: 0;
}

:deep(.create-model-step-drawer .el-drawer__header) {
  border-bottom: 1px solid var(--el-border-color-lighter);
  margin-bottom: 0;
  padding: calc(var(--spacing) * 4) calc(var(--spacing) * 6);
}
</style>
