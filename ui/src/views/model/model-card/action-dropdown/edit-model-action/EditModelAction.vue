<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ModelApi from '@/api/admin/workspace/model'
import type SystemResourceModelApi from '@/api/admin/system/resource-management/model'
import type SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import EditModelDrawer from './EditModelDrawer.vue'

defineOptions({ name: 'EditModelAction' })

const props = defineProps<{
  api: typeof ModelApi | typeof SystemSharedModelApi | typeof SystemResourceModelApi
  disabled?: boolean
  label: string
  model: ModelItem
  provider: ModelProviderItem
}>()

const emit = defineEmits<{ refresh: [] }>()

const drawerMounted = ref(false)
const editModelDrawerRef = useTemplateRef<InstanceType<typeof EditModelDrawer>>('editModelDrawerRef')

function handleOpenEditModel() {
  drawerMounted.value = true
  void nextTick(() => editModelDrawerRef.value?.open(props.provider, props.model))
}

function handleDrawerClosed() {
  drawerMounted.value = false
}
</script>

<template>
  <!-- 编辑模型 -->
  <MkAction :label="label" icon="icon_edit_outlined" :disabled="disabled" @click="handleOpenEditModel" />

  <EditModelDrawer v-if="drawerMounted" ref="editModelDrawerRef" :api="api" @closed="handleDrawerClosed" @refresh="emit('refresh')" />
</template>
