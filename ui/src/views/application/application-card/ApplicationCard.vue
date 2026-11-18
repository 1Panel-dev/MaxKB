<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ApplicationDetail } from '@/api/types'
import type { ApiInputField } from '@/workflow-canvas/nodes/base-node/types'
import applicationAPI from '@/api/admin/workspace/application/application'
import { CHAT_API_BASE_PATH } from '@/api/constants'
import { isWorkFlow } from '@/utils/common'
import { dateFormat } from '@/utils/time'
import { hasRenderableSlotContent } from '@/utils/vnode'

defineOptions({ name: 'ApplicationCard' })

const { t } = useI18n({ useScope: 'global' })

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
      <el-tag v-if="isWorkFlow(application.type)" type="warning" size="small">{{ t('application.advanced.shortLabel') }}</el-tag>
      <el-tag v-else type="primary" class="default" size="small">{{ t('application.simple.shortLabel') }}</el-tag>
    </template>

    <p class="line-clamp-2" :title="application.desc ?? undefined">
      {{ application.desc }}
    </p>

    <template #footer="{ Action, ActionDropdown }">
      <MkStatusLabel v-if="application.is_portal" type="custom" :label="t('application.status.onPortal')" icon="icon_launch" class="text-N600!" />
      <MkStatusLabel
        v-else
        :active="application.is_publish"
        :active-text="t('application.status.published')"
        :inactive-text="t('application.status.unpublished')"
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
        <MkTooltip :content="t('application.actions.chat')" placement="top">
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
