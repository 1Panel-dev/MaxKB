<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type RelatedResourcesApi from '@/api/admin/workspace/related-resources'
import type { ModelItem } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import { MsgError } from '@/utils/message'
import RelatedResourcesDrawer from '@/components/business/related-resources-drawer/index.vue'

defineOptions({ name: 'RelatedResourcesModelAction' })
const props = defineProps<{
  api: typeof RelatedResourcesApi
  model: ModelItem
  label: string
}>()

/* 点击后挂载，关闭动画结束后释放抽屉。 */
const drawerMounted = ref(false)
const relatedResourcesDrawerRef = useTemplateRef<InstanceType<typeof RelatedResourcesDrawer>>('relatedResourcesDrawerRef')
function handleOpenRelatedResources() {
  const workspaceId = props.model.workspace_id
  if (!workspaceId) {
    MsgError('模型缺少所属工作空间信息')
    return
  }
  const model = { ...props.model, workspace_id: workspaceId }
  drawerMounted.value = true
  return nextTick(() => relatedResourcesDrawerRef.value?.open(RESOURCE_TYPE.MODEL, model))
}
function handleDrawerClosed() {
  drawerMounted.value = false
}
</script>

<template>
  <!-- 查看关联资源 -->
  <MkDropdownItem @click="handleOpenRelatedResources">
    <template #icon><MkIcon name="icon_mindnote_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
  <RelatedResourcesDrawer v-if="drawerMounted" ref="relatedResourcesDrawerRef" :api="api" @closed="handleDrawerClosed" />
</template>
