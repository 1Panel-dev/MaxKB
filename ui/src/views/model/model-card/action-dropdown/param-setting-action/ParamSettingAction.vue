<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ModelApi from '@/api/admin/workspace/model/model'
import type { ModelItem } from '@/api/types'
import ParamSettingDrawer from './ParamSettingDrawer.vue'

defineOptions({ name: 'ParamSettingAction' })

const props = defineProps<{ api: typeof ModelApi; label: string; model: ModelItem }>()

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
  <MkDropdownItem @click="handleOpenParamSetting">
    <template #icon><MkIcon name="icon_preferences_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>

  <ParamSettingDrawer v-if="drawerMounted" ref="paramSettingDrawerRef" :api="api" @closed="handleDrawerClosed" />
</template>
