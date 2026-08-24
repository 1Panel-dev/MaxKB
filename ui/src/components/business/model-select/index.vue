<script setup lang="ts">
import { computed, ref } from 'vue'
import { Check } from '@element-plus/icons-vue'
import { MODEL_STATUS } from '@/api/enums'
import type { ModelProviderItem, ModelItem } from '@/api/types'
import { groupBy } from 'lodash'
defineOptions({
  name: 'ModelSelect',
  inheritAttrs: false,
})

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
  }>(),
  {
    modelValue: '',
    options: () => [],
    providerOptions: () => [],
  },
)
const _options = computed(() => {
  return groupBy(props.options, 'provider')
})
const emit = defineEmits<{
  change: [modelId: string]
  'update:modelValue': [modelId: string]
}>()

const loading = ref(false)

const selectedModelId = computed({
  get: () => props.modelValue,
  set: (modelId) => {
    emit('update:modelValue', modelId)
    emit('change', modelId)
  },
})

const modelOptionGroups = computed<ModelOptionGroup[]>(() => {
  const providerMap = new Map(
    props.providerOptions.map((provider) => [provider.provider, provider]),
  )

  return Object.entries(_options.value ?? {}).map(([provider, models]) => {
    const providerOption = providerMap.get(provider)
    return {
      icon: providerOption?.icon ?? '',
      models: [...models].sort(
        (left, right) =>
          Number(right.status === MODEL_STATUS.SUCCESS) -
          Number(left.status === MODEL_STATUS.SUCCESS),
      ),
      name: providerOption?.name ?? provider,
      provider,
    }
  })
})

const selectedProviderIcon = computed(
  () =>
    modelOptionGroups.value.find(({ models }) =>
      models.some(({ id }) => id === selectedModelId.value),
    )?.icon ?? '',
)
</script>

<template>
  <el-select
    v-model="selectedModelId"
    v-bind="$attrs"
    class="w-full"
    clearable
    filterable
    :loading="loading"
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
</template>
