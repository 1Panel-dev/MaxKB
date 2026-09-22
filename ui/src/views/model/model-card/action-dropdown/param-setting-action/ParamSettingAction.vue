<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ModelApi from '@/api/admin/workspace/model'
import type SystemResourceModelApi from '@/api/admin/system/resource-management/model'
import type SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import type { ModelItem } from '@/api/types'
import ParamSettingDrawer from './ParamSettingDrawer.vue'

defineOptions({ name: 'ParamSettingAction' })

const props = defineProps<{ api: typeof ModelApi | typeof SystemSharedModelApi | typeof SystemResourceModelApi; label: string; model: ModelItem }>()

const drawerMounted = ref(false)
const paramSettingDrawerRef = useTemplateRef<InstanceType<typeof ParamSettingDrawer>>('paramSettingDrawerRef')

function handleOpenParamSetting() {
  drawerMounted.value = true
  void nextTick(() => paramSettingDrawerRef.value?.open(props.model))
}

function handleDrawerClosed() {
  drawerMounted.value = false
}
</script>

<template>
  <!-- 模型参数设置 -->
  <MkAction :label="label" icon="icon_preferences_outlined" @click="handleOpenParamSetting" />

  <ParamSettingDrawer v-if="drawerMounted" ref="paramSettingDrawerRef" :api="api" @closed="handleDrawerClosed" />
</template>
