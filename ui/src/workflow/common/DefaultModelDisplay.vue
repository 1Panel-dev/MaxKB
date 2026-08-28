<template>
  <el-select
    class="default-model-display"
    :model-value="displayModelId"
    disabled
    :teleported="false"
    style="width: 100%"
  >
    <el-option
      v-for="opt in displayOptions"
      :key="opt.value"
      :value="opt.value"
      :label="opt.label"
    />
    <template #label="{ label }">
      <el-space :size="8">
        <span
          v-if="currentModelIcon"
          class="select-model-icon"
          :innerHTML="currentModelIcon"
        ></span>
        <span>{{ label }}</span>
      </el-space>
    </template>
  </el-select>
</template>
<script setup lang="ts">
import { computed, inject, onMounted, ref } from 'vue'
import { flatMap } from 'lodash'
import { t } from '@/locales'
import useStore from '@/stores'
import { relatedObject } from '@/utils/array'

defineOptions({ name: 'DefaultModelDisplay' })

const props = defineProps<{
  type: string
  options: any
}>()

const getResourceDetail = inject('getResourceDetail') as any
const { model } = useStore()
const providerOptions = ref<any[]>([])

// 无可用模型时的兜底占位 id,保证 disabled el-select 一定能解析出选中项
const PLACEHOLDER_ID = '__default_model__'

const defaultModelId = computed(() => {
  return getResourceDetail?.()?.value?.default_model_setting?.[props.type]?.model_id || ''
})

const currentModel = computed(() => {
  if (!props.options || !defaultModelId.value) return null
  return (flatMap(props.options) as any[]).find((item: any) => item.id === defaultModelId.value) || null
})

const displayModelId = computed(() => (currentModel.value ? currentModel.value.id : PLACEHOLDER_ID))

const displayOptions = computed(() => {
  if (currentModel.value) {
    return [{ value: currentModel.value.id, label: currentModel.value.name }]
  }
  // 已配置默认模型但该模型在当前可选列表中无法解析(停用/下架/可见性过滤)时,
  // 与「未配置」区分开,避免误导用户以为缺省配置不存在。
  if (defaultModelId.value) {
    return [{ value: PLACEHOLDER_ID, label: t('workflow.setting.defaultModelUnavailable') }]
  }
  return [{ value: PLACEHOLDER_ID, label: t('workflow.setting.defaultModelNotConfigured') }]
})

const currentModelIcon = computed(() => {
  if (!currentModel.value) return ''
  return relatedObject(providerOptions.value, currentModel.value.provider, 'provider')?.icon || ''
})

onMounted(() => {
  model.asyncGetProvider().then((res: any) => {
    providerOptions.value = res?.data || []
  })
})
</script>
