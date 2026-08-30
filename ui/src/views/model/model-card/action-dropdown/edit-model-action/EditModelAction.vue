<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ModelApi from '@/api/admin/workspace/model/model'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import EditModelDrawer from './EditModelDrawer.vue'

defineOptions({ name: 'EditModelAction' })

const props = defineProps<{ api: typeof ModelApi; label: string; model: ModelItem; provider: ModelProviderItem }>()

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
  <MkDropdownItem @click="handleOpenEditModel">
    <template #icon><MkIcon name="icon_edit_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>

  <EditModelDrawer v-if="drawerMounted" ref="editModelDrawerRef" :api="api" @closed="handleDrawerClosed" @refresh="emit('refresh')" />
</template>
