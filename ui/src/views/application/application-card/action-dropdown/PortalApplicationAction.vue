<script setup lang="ts">
import { computed } from 'vue'
import type { ApplicationDetail } from '@/api/types'
import type ApplicationApi from '@/api/admin/workspace/application/application'
import type SystemResourceApplicationApi from '@/api/admin/system/resource-management/application/application'
import perm from '@/permission'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'PortalApplicationAction' })

const props = defineProps<{ api: typeof ApplicationApi | typeof SystemResourceApplicationApi; application: ApplicationDetail }>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ change: [isPortal: boolean] }>()

/** 依据 api 是否含工作空间独有方法区分工作空间/系统资源管理场景，用于选择对应权限。 */
const isSystem = computed(() => !('putMoveApplication' in props.api))


/** 上下架权限：未授权时隐藏对应入口。 */
const canPortalUp = computed(() => (isSystem.value ? perm.application.system.portalUp() : perm.application.workspace.portalUp(props.application.id)))
const canPortalDown = computed(() => (isSystem.value ? perm.application.system.portalDown() : perm.application.workspace.portalDown(props.application.id)))

/** 上架到门户：仅已发布可上架。 */
const canUp = computed(() => canPortalUp.value && Boolean(props.application.is_publish))

function handlePortalUp() {
  if (loading.value || props.application.is_portal || !canUp.value) return
  loading.value = true
  return props.api
    .putApplicationPortalUp(props.application.id)
    .then((application) => {
      emit('change', application.is_portal)
      MsgSuccess('上架成功')
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

function handlePortalDown() {
  if (loading.value || !props.application.is_portal || !canPortalDown.value) return
  loading.value = true
  return props.api
    .putApplicationPortalDown(props.application.id)
    .then((application) => {
      emit('change', application.is_portal)
      MsgSuccess('下架成功')
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <!-- 上架到门户：仅已发布、未上架且有权限时展示 -->
  <MkDropdownItem v-if="!application.is_portal && canUp" :disabled="loading" @click="handlePortalUp">
    <template #icon>
      <MkIcon name="icon_launch_outlined1" />
    </template>
    <span>上架到门户</span>
  </MkDropdownItem>
  <!-- 从门户下架 -->
  <MkDropdownItem v-if="application.is_portal && canPortalDown" :disabled="loading" @click="handlePortalDown">
    <template #icon>
      <MkIcon name="icon_remove_outlined" />
    </template>
    <span>从门户下架</span>
  </MkDropdownItem>
</template>
