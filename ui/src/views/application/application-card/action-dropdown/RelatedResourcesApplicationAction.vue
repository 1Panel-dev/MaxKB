<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type RelatedResourcesApi from '@/api/admin/workspace/related-resources'
import type { ApplicationDetail } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import RelatedResourcesDrawer from '@/components/business/related-resources-drawer/index.vue'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'RelatedResourcesApplicationAction' })

const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{
  api: typeof RelatedResourcesApi
  application: ApplicationDetail
  label: string
}>()

/* 点击后挂载，关闭动画结束后释放抽屉。 */
const drawerMounted = ref(false)
const relatedResourcesDrawerRef = useTemplateRef<InstanceType<typeof RelatedResourcesDrawer>>('relatedResourcesDrawerRef')
function handleOpenRelatedResources() {
  const workspaceId = props.application.workspace_id
  if (!workspaceId) {
    MsgError(t('application.messages.missingWorkspace'))
    return
  }
  const application = { ...props.application, workspace_id: workspaceId }
  drawerMounted.value = true
  return nextTick(() => relatedResourcesDrawerRef.value?.open(RESOURCE_TYPE.APPLICATION, application))
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
