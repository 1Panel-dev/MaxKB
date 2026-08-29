<script setup lang="ts">
import { useTemplateRef } from 'vue'
import type { ModelProviderItem } from '@/api/types'
import CreateModelDrawer from './CreateModelDrawer.vue'
import SelectProviderDrawer from './SelectProviderDrawer.vue'

defineOptions({ name: 'ModelCreate' })

const props = defineProps<{
  currentProvider: ModelProviderItem
  providers: ModelProviderItem[]
}>()

const emit = defineEmits<{
  refresh: []
}>()

/* 创建模型 */
const selectProviderDrawerRef =
  useTemplateRef<InstanceType<typeof SelectProviderDrawer>>('selectProviderDrawerRef')
const createModelDrawerRef =
  useTemplateRef<InstanceType<typeof CreateModelDrawer>>('createModelDrawerRef')

function handleOpenCreateModel() {
  if (props.currentProvider.provider !== 'all') {
    createModelDrawerRef.value?.open(props.currentProvider)
    return
  }
  selectProviderDrawerRef.value?.open()
}

function handleCreateProviderSelect(provider: ModelProviderItem) {
  createModelDrawerRef.value?.open(provider)
}

function handleBackToProviderSelect() {
  selectProviderDrawerRef.value?.open()
}
</script>

<template>
  <el-button type="primary" class="ml-3" @click="handleOpenCreateModel">
    <MkIcon name="icon_add_outlined" />
    <span>添加模型</span>
  </el-button>
  <SelectProviderDrawer ref="selectProviderDrawerRef" @select="handleCreateProviderSelect" />
  <CreateModelDrawer
    ref="createModelDrawerRef"
    :providers="providers"
    @back="handleBackToProviderSelect"
    @refresh="emit('refresh')"
  />
</template>
