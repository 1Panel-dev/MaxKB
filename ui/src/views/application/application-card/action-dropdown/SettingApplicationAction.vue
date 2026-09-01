<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import type { ApplicationDetail } from '@/api/types'
import { isWorkFlow } from '@/utils/application'

defineOptions({ name: 'SettingApplicationAction' })

const props = defineProps<{ application: ApplicationDetail; label: string }>()

const router = useRouter()
const route = useRoute()

function handleSettingApplication(event: MouseEvent) {
  event.stopPropagation()
  if (isWorkFlow(props.application.type)) {
    const workflowRoute = {
      name: 'workflow-application',
      params: { workspaceId: route.params.workspaceId, applicationId: props.application.id },
    } as const

    if (event.ctrlKey || event.metaKey) {
      window.open(router.resolve(workflowRoute).href)
      return
    }
    router.push(workflowRoute)
  } else {
    void router.push({
      name: 'workspace-application-simple-setting',
      params: {
        applicationId: props.application.id,
        type: props.application.type,
        workspaceId: route.params.workspaceId,
      },
    })
  }
}
</script>

<template>
  <MkDropdownItem @click="handleSettingApplication">
    <template #icon><MkIcon name="icon-setting" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
</template>
