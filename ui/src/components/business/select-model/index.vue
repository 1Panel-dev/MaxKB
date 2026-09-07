<script setup lang="ts" generic="Multiple extends boolean = false">
import { computed, ref, useTemplateRef } from 'vue'
import type { SelectInstance } from 'element-plus'
import { MODEL_STATUS } from '@/api/enums'
import type { ModelProviderItem, ModelItem } from '@/api/types'
import { groupBy } from 'lodash'
import ModelParamsDialog from './ModelParamsDialog.vue'
import ModelCreateButton from '@/views/model/create-model/ModelCreateButton.vue'
import ModelApi from '@/api/admin/workspace/model/model'
import SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import { isWorkspaceResource, isSystemSharedResource } from '@/utils/resource-context'
defineOptions({ name: 'SelectModel', inheritAttrs: false })

interface ModelOptionGroup {
  icon: string
  models: ModelItem[]
  name: string
  provider: string
}

type SelectModelValue = Multiple extends true ? string[] : string

const props = withDefaults(
  defineProps<{
    modelValue: SelectModelValue
    options: ModelItem[]
    providerOptions: ModelProviderItem[]
    canEditParams?: boolean
    canAdd?: boolean
    modelParams?: Record<string, unknown>
    disabled?: boolean
    multiple?: Multiple
  }>(),
  {
    options: () => [],
    providerOptions: () => [],
    canEditParams: false,
    canAdd: false,
    modelParams: () => ({}),
    disabled: false,
  },
)

const emit = defineEmits<{
  change: [modelValue: SelectModelValue]
  refresh: []
  'update:modelValue': [modelValue: SelectModelValue]
  'update:modelParams': [settings: Record<string, unknown>]
}>()

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

const _options = computed(() => {
  return groupBy(props.options, 'provider')
})

const loading = ref(false)
const canEditModelParams = computed(() => props.canEditParams && !props.multiple)

const selectedModelValue = computed<SelectModelValue>({
  get: () => props.modelValue,
  set: (modelValue) => {
    emit('update:modelValue', modelValue)
    emit('change', modelValue)
    if (typeof modelValue === 'string') resetModelParams(modelValue)
  },
})

function getProviderIcon(modelId: unknown) {
  return modelOptionGroups.value.find(({ models }) => models.some(({ id }) => id === modelId))?.icon ?? ''
}

// 创建模型：根据当前资源范围传入完整 API，创建后由调用方刷新选项。
const selectRef = useTemplateRef<SelectInstance>('selectRef')
const allModelProvider: ModelProviderItem = { icon: '', name: '全部模型', provider: 'all' }
const createModelApi = computed(() => {
  if (isWorkspaceResource()) return ModelApi
  if (isSystemSharedResource()) return SystemSharedModelApi
  return undefined
})

function handleOpenCreateModel(open: () => void) {
  if (props.disabled || !props.canAdd || !createModelApi.value) return
  selectRef.value?.blur()
  open()
}

// 模型参数：切换模型加载默认值，确认弹窗后回写配置。
const modelParamsDialogRef = useTemplateRef<InstanceType<typeof ModelParamsDialog>>('modelParamsDialogRef')

function resetModelParams(modelId: string) {
  if (!canEditModelParams.value) return
  emit('update:modelParams', {})
  if (!modelId) return
  modelParamsDialogRef.value?.resetDefault(modelId).then((settings) => {
    if (props.modelValue !== modelId || !canEditModelParams.value) return
    emit('update:modelParams', settings)
  })
}

function openModelParams() {
  if (typeof props.modelValue !== 'string' || !props.modelValue || props.disabled) return
  modelParamsDialogRef.value?.open(props.modelValue, props.modelParams)
}
</script>

<template>
  <div class="relative w-full" :class="{ 'select-model--with-params': canEditModelParams }">
    <el-select
      ref="selectRef"
      v-model="selectedModelValue"
      placeholder="请选择模型"
      v-bind="$attrs"
      class="w-full"
      :disabled="disabled"
      clearable
      filterable
      :loading="loading"
      :multiple="multiple"
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
          </div>
        </el-option>
      </el-option-group>

      <template #label="{ label, value }">
        <div class="flex items-center" :class="multiple ? 'gap-1' : 'gap-2'">
          <span v-if="getProviderIcon(value)" class="shrink-0" :class="multiple ? 'h-4 w-4' : 'h-5 w-5'" v-html="getProviderIcon(value)" />
          <span class="truncate" :title="label">{{ label }}</span>
        </div>
      </template>

      <template v-if="canAdd && createModelApi" #footer>
        <slot name="footer">
          <ModelCreateButton :api="createModelApi" :current-provider="allModelProvider" :providers="providerOptions" @refresh="emit('refresh')">
            <template #default="{ open }">
              <el-button type="primary" link :disabled="disabled" @click.stop="handleOpenCreateModel(open)">
                <MkIcon name="icon_add_outlined" />
                <span>添加模型</span>
              </el-button>
            </template>
          </ModelCreateButton>
        </slot>
      </template>
    </el-select>
    <div v-if="canEditModelParams" class="absolute inset-y-px right-3 flex items-center gap-2">
      <el-divider direction="vertical" />
      <el-tooltip content="模型参数设置" placement="top" :disabled="disabled || !modelValue">
        <el-button text class="-mr-1" :disabled="disabled || !modelValue" @click.stop="openModelParams">
          <MkIcon name="icon_preferences_outlined" />
        </el-button>
      </el-tooltip>
    </div>
  </div>
  <ModelParamsDialog v-if="canEditModelParams" ref="modelParamsDialogRef" @submit="emit('update:modelParams', $event)" />
</template>

<style scoped lang="scss">
/* 参数入口与选择器共用外边框，为原生下拉箭头和清空按钮预留空间。 */
.select-model--with-params {
  :deep(.el-select__wrapper) {
    padding-right: calc(var(--spacing) * 13);
  }
}
</style>
