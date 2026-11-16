<script setup lang="ts">
import { computed } from 'vue'
import type { ApplicationDetail } from '@/api/types'
import type { ApiInputField } from '@/workflow-canvas/nodes/base-node/types'
import applicationAPI from '@/api/admin/workspace/application/application'
import { CHAT_API_BASE_PATH } from '@/api/constants'
import { isWorkFlow } from '@/utils/common'
import { dateFormat } from '@/utils/time'
import { hasRenderableSlotContent } from '@/utils/vnode'

defineOptions({ name: 'ApplicationCard' })

const props = defineProps<{ application: ApplicationDetail; selectable?: boolean; selected?: boolean }>()

const emit = defineEmits<{ click: []; selected: [selected: boolean] }>()

const slots = defineSlots<{ 'action-dropdown'?: () => unknown }>()
const hasActionDropdown = computed(() => hasRenderableSlotContent(slots['action-dropdown']?.()))
const apiQuery = computed(() => {
  const query = props.application?.work_flow?.nodes
    ?.find((n) => n.id === 'base-node')
    ?.properties?.api_input_field_list.map((field: ApiInputField) => {
      return `${field.variable}=${field.default_value}`
    })
    .join('&')
  if (query) {
    return '?' + query
  }
  return ''
})

const chatBasePath = CHAT_API_BASE_PATH.replace(/\/api$/, '')

function handleOpen() {
  if (!props.selectable) emit('click')
}
function toChat() {
  applicationAPI.getAccessToken(props.application.id).then((ok) => {
    const accessUrl = ok.access_token ? `${window.location.origin}${chatBasePath}/${ok.access_token}/${apiQuery.value}` : ''
    window.open(accessUrl, '_blank')
  })
}
</script>

<template>
  <MkResourceCard
    :create_time="application.create_time"
    :nick_name="application.nick_name || '-'"
    :selectable="selectable"
    :selected="selected"
    :title="application.name"
    :class="{ 'cursor-pointer': !selectable }"
    @click="handleOpen"
    @selected="emit('selected', $event)"
  >
    <template #icon>
      <ApplicationIcon :icon="application.icon" />
    </template>

    <template #tag>
      <el-tag v-if="isWorkFlow(application.type)" type="warning" size="small">高级</el-tag>
      <el-tag v-else type="primary" class="default" size="small">简易</el-tag>
    </template>

    <p class="line-clamp-2" :title="application.desc ?? undefined">
      {{ application.desc }}
    </p>

    <template #footer="{ Action, ActionDropdown }">
      <MkStatusLabel v-if="application.is_portal" type="custom" label="已上架" icon="icon_launch" class="text-N600!" />
      <MkStatusLabel
        v-else
        :active="application.is_publish"
        active-text="已发布"
        inactive-text="未发布"
        :icon="application.is_publish ? undefined : 'icon_time_filled'"
        class="text-N600!"
      />
      <template v-if="application.is_publish">
        <el-divider direction="vertical" />
        <span class="flex-align-center gap-2">
          <MkIcon name="icon_time_outlined" class="text-N500!" />
          <span class="text-N600">{{ dateFormat(application.update_time) }}</span>
        </span>
      </template>

      <component :is="Action">
        <!-- 去对话 -->
        <MkTooltip content="去对话" placement="top">
          <el-button text @click="toChat">
            <MkIcon name="icon_new-chat_outlined" />
          </el-button>
        </MkTooltip>
        <template v-if="hasActionDropdown">
          <el-divider direction="vertical" />
          <component :is="ActionDropdown">
            <slot name="action-dropdown" />
          </component>
        </template>
      </component>
    </template>
  </MkResourceCard>
</template>
