<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type { ToolItem } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import ResourceAuthorizationDrawer from '@/components/business/resource-authorization-drawer/index.vue'

defineOptions({ name: 'AuthorizeToolAction' })
const props = defineProps<{ tool: ToolItem; label: string }>()

const drawerMounted = ref(false)
const authorizationDrawerRef = useTemplateRef<InstanceType<typeof ResourceAuthorizationDrawer>>('authorizationDrawerRef')

function handleOpenAuthorization() {
  drawerMounted.value = true
  return nextTick(() => authorizationDrawerRef.value?.open(props.tool.id))
}

function handleDrawerClosed() {
  drawerMounted.value = false
}
</script>

<template>
  <!-- 资源授权 -->
  <MkDropdownItem @click="handleOpenAuthorization">
    <template #icon><MkIcon name="icon_passkeys_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
  <ResourceAuthorizationDrawer
    v-if="drawerMounted"
    ref="authorizationDrawerRef"
    :type="RESOURCE_TYPE.TOOL"
    :workspace-id="tool.workspace_id"
    @closed="handleDrawerClosed"
  />
</template>
