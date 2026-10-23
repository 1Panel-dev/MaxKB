<script setup lang="ts">
import type { ApplicationDetail } from '@/api/types'
import type ApplicationApi from '@/api/admin/workspace/application/application'
import type SystemResourceApplicationApi from '@/api/admin/system/resource-management/application/application'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'PortalApplicationAction' })

const props = defineProps<{ api: typeof ApplicationApi | typeof SystemResourceApplicationApi; application: ApplicationDetail }>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ change: [isPortal: boolean] }>()

function handlePortalApplication() {
  if (loading.value) return
  const isPortal = !props.application.is_portal
  loading.value = true
  return props.api
    .putApplicationPortal(props.application.id, isPortal)
    .then((application) => {
      emit('change', application.is_portal)
      MsgSuccess(isPortal ? '上架成功' : '下架成功')
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <!-- 切换智能体门户上架状态 -->
  <MkDropdownItem divided :disabled="loading" @click="handlePortalApplication">
    <template #icon>
      <MkIcon :name="application.is_portal ? 'icon_remove_outlined' : 'icon_launch_outlined1'" />
    </template>
    <span>{{ application.is_portal ? '从门户下架' : '上架到门户' }}</span>
  </MkDropdownItem>
</template>
