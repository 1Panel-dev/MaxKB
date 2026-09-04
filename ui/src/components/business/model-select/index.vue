<script setup lang="ts">
import { computed, onBeforeUnmount, ref, useTemplateRef } from 'vue'
import { Check, Operation } from '@element-plus/icons-vue'
import { MODEL_STATUS } from '@/api/enums'
import type { ModelProviderItem, ModelItem } from '@/api/types'
import { groupBy } from 'lodash'
import ModelParamsDialog from './ModelParamsDialog.vue'
defineOptions({ name: 'ModelSelect', inheritAttrs: false })

interface ModelOptionGroup {
  icon: string
  models: ModelItem[]
  name: string
  provider: string
}

const props = withDefaults(
  defineProps<{
    modelValue: string
    options: ModelItem[]
    providerOptions: ModelProviderItem[]
    showModelParams?: boolean
    modelParams?: Record<string, unknown>
    disabled?: boolean
  }>(),
  {
    modelValue: '',
    options: () => [],
    providerOptions: () => [],
    showModelParams: false,
    modelParams: () => ({}),
    disabled: false,
  },
)
const _options = computed(() => {
  return groupBy(props.options, 'provider')
})
const emit = defineEmits<{
  change: [modelId: string]
  'update:modelValue': [modelId: string]
  'update:modelParams': [settings: Record<string, unknown>]
}>()

const loading = ref(false)

const selectedModelId = computed({
  get: () => props.modelValue,
  set: (modelId) => {
    emit('update:modelValue', modelId)
    emit('change', modelId)
    resetModelParams(modelId)
  },
})

// 模型参数：切换模型加载默认值，确认弹窗后回写配置。
const modelParamsDialogRef = useTemplateRef<InstanceType<typeof ModelParamsDialog>>('modelParamsDialogRef')
let modelParamsRequestId = 0

function resetModelParams(modelId: string) {
  const requestId = ++modelParamsRequestId
  if (!props.showModelParams) return
  emit('update:modelParams', {})
  if (!modelId) return
  modelParamsDialogRef.value?.resetDefault(modelId).then((settings) => {
    if (requestId !== modelParamsRequestId || props.modelValue !== modelId || !props.showModelParams) return
    emit('update:modelParams', settings)
  })
}

function openModelParams() {
  if (!props.modelValue || props.disabled) return
  modelParamsDialogRef.value?.open(props.modelValue, props.modelParams)
}

onBeforeUnmount(() => {
  modelParamsRequestId += 1
})

const modelOptionGroups = computed<ModelOptionGroup[]>(() => {
  const providerMap = new Map(props.providerOptions.map((provider) => [provider.provider, provider]))

  return Object.entries(_options.value ?? {}).map(([provider, models]) => {
    const providerOption = providerMap.get(provider)
    return {
      icon: providerOption?.icon ?? '',
      models: [...models].sort((left, right) => Number(right.status === MODEL_STATUS.SUCCESS) - Number(left.status === MODEL_STATUS.SUCCESS)),
      name: providerOption?.name ?? provider,
      provider,
    }
  })
})

const selectedProviderIcon = computed(
  () => modelOptionGroups.value.find(({ models }) => models.some(({ id }) => id === selectedModelId.value))?.icon ?? '',
)
</script>

<template>
  <div class="flex w-full items-center gap-2">
    <el-select
      v-model="selectedModelId"
      v-bind="$attrs"
      class="min-w-0 flex-1"
      :disabled="disabled"
      clearable
      filterable
      :loading="loading"
      :teleported="false"
    >
      <el-option-group v-for="group in modelOptionGroups" :key="group.provider" :label="group.name">
        <el-option
          v-for="model in group.models"
          :key="model.id"
          :disabled="model.status !== MODEL_STATUS.SUCCESS"
          :label="model.name"
          :value="model.id"
        >
          <div class="flex h-full items-center gap-2">
            <span class="h-5 w-5 shrink-0" v-html="group.icon" />
            <span class="min-w-0 flex-1 truncate" :title="model.name">{{ model.name }}</span>
            <el-tag v-if="model.source === 'shared'" size="small" type="info">共享</el-tag>
            <span v-if="model.status !== MODEL_STATUS.SUCCESS" class="text-danger">不可用</span>
            <Check v-if="model.id === selectedModelId" class="h-4 w-4 shrink-0 text-primary" />
          </div>
        </el-option>
      </el-option-group>

      <template #label="{ label }">
        <div class="flex items-center gap-2">
          <span class="h-5 w-5 shrink-0" v-html="selectedProviderIcon" />
          <span class="truncate" :title="label">{{ label }}</span>
        </div>
      </template>

      <template #empty>
        <MkEmpty description="暂无可用模型" />
      </template>
    </el-select>
    <el-button v-if="showModelParams" :disabled="disabled || !modelValue" title="模型参数设置" aria-label="模型参数设置" @click="openModelParams">
      <MkIcon :icon="Operation" />
    </el-button>
  </div>
  <ModelParamsDialog v-if="showModelParams" ref="modelParamsDialogRef" @submit="emit('update:modelParams', $event)" />
</template>
