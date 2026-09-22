<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type LogicFlow from '@logicflow/core'
import type SharedModelApi from '@/api/admin/system/shared-resources/model'
import type SystemModelApi from '@/api/admin/system/resource-management/model'
import type ModelApi from '@/api/admin/workspace/model'
import type { DefaultModelSettingPayload } from '@/api/types'
import DefaultModelSettingDrawer from './DefaultModelSettingDrawer.vue'

defineOptions({ name: 'ButtonDefaultModelSetting' })

const props = withDefaults(
  defineProps<{
    modelValue?: DefaultModelSettingPayload
    modelApi: typeof ModelApi | typeof SystemModelApi | typeof SharedModelApi
    getGraphData: () => LogicFlow.GraphData | undefined
    disabled?: boolean
  }>(),
  { modelValue: () => ({}), disabled: false },
)
const emit = defineEmits<{
  open: []
  save: [settings: DefaultModelSettingPayload]
  applyToAll: [graphData: LogicFlow.GraphData]
}>()

const drawerMounted = ref(false)
const drawerRef = useTemplateRef<InstanceType<typeof DefaultModelSettingDrawer>>('drawerRef')

function handleOpen() {
  if (props.disabled || drawerMounted.value) return
  emit('open')
  drawerMounted.value = true
  void nextTick(() => drawerRef.value?.open(props.modelValue))
}

function handleDrawerClosed() {
  drawerMounted.value = false
}
</script>

<template>
  <el-button plain :disabled="disabled" @click="handleOpen">
    <MkIcon name="icon_admin_outlined" />
    <span> 默认模型设置 </span>
  </el-button>

  <DefaultModelSettingDrawer
    v-if="drawerMounted"
    ref="drawerRef"
    :model-value="modelValue"
    :model-api="modelApi"
    :get-graph-data="getGraphData"
    :disabled="disabled"
    @save="emit('save', $event)"
    @apply-to-all="emit('applyToAll', $event)"
    @closed="handleDrawerClosed"
  />
</template>
