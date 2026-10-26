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
const id = computed(() => props.application.id)

/** 上下架权限：未授权时隐藏对应入口。 */
const canPortalUp = computed(() => (isSystem.value ? perm.application.system.portalUp() : perm.application.workspace.portalUp(id.value)))
const canPortalDown = computed(() => (isSystem.value ? perm.application.system.portalDown() : perm.application.workspace.portalDown(id.value)))

/** 上架到门户：仅已发布可上架。 */
const canUp = computed(() => canPortalUp.value && Boolean(props.application.is_publish))

function handlePortalUp() {
  if (loading.value) return
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
  if (loading.value) return
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
  <!-- 上架到门户：仅已发布且有权限时可用 -->
  <MkDropdownItem
    v-if="!application.is_portal && canPortalUp"
    :disabled="loading || !canUp"
    :title="!canUp ? '请先发布后再上架' : ''"
    @click="handlePortalUp"
  >
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
