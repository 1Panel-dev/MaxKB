<script setup lang="ts">
import { ref } from 'vue'
import type { ModelProviderItem } from '@/api/types'
import ProviderApi from '@/api/admin/workspace/model/provider'
import { MODEL_TYPE_LABELS } from '@/constants'

defineOptions({ name: 'SelectProviderDrawer' })

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
  loadModelProviders()
  visible.value = true
}

/* 供应商 */
function loadModelProviders() {
  return ProviderApi.getProviderList().then((providers) => {
    providerOptions.value = [...providers].sort((left, right) =>
      left.name.localeCompare(right.name),
    )
  })
}

function handleProviderSelect(provider: ModelProviderItem) {
  visible.value = false
  emit('select', provider)
}

function handleModelTypeChange() {
  // if (value === 'all') {
  //   providerOptions.value = props.providers
  //   return
  // }
  // loading.value = true
  // ProviderApi.getProviderListByModelType(value)
  //   .then((providers) => {
  //     providerOptions.value = providers
  //   })
  //   .finally(() => {
  //     loading.value = false
  //   })
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" direction="btt" title="添加模型" @closed="resetData">
    <template #header>
      <div class="flex w-full">
        <h4>添加模型</h4>
        <el-steps :active="0" class="absolute-center w-75!">
          <el-step title="选择供应商" />
          <el-step title="添加模型" />
        </el-steps>
      </div>
    </template>

    <div class="max-w-200 mx-auto">
      <div class="mb-5 flex-between">
        <h4>选择供应商</h4>
        <el-select v-model="modelType" class="w-45!" @change="handleModelTypeChange">
          <el-option label="全部模型" value="all" />
          <el-option
            v-for="(label, value) in MODEL_TYPE_LABELS"
            :key="value"
            :label="label"
            :value="value"
          />
        </el-select>
      </div>

      <div v-loading="loading" class="grid grid-cols-2 gap-4">
        <template v-for="provider in providerOptions" :key="provider.provider">
          <el-card shadow="hover" @click="handleProviderSelect(provider)">
            <div class="flex">
              <span class="h-6 w-6 shrink-0" :innerHTML="provider.icon" />
              <span class="ml-3 font-medium">{{ provider.name }}</span>
            </div>
          </el-card>
        </template>
      </div>

      <MkEmpty v-if="!providerOptions.length" class="mt-24" />
    </div>
  </MkDrawer>
</template>

<style scoped lang="scss"></style>
