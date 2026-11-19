<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import type ModelApi from '@/api/admin/workspace/model'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import { MODEL_STATUS } from '@/api/enums'
import ModelDownloadStatus from './ModelDownloadStatus.vue'
import { MODEL_TYPE_LABELS } from '@/constants/model'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'ModelCard' })

const props = defineProps<{
  api: typeof ModelApi | typeof SystemSharedModelApi
  disabled?: boolean
  model: ModelItem
  provider: ModelProviderItem
  refresh: () => Promise<void>
  shared: boolean
}>()

const emit = defineEmits<{ click: [event: MouseEvent] }>()

defineSlots<{ 'action-dropdown'?: () => unknown }>()

const modelTypeLabel = computed(() => {
  return MODEL_TYPE_LABELS[props.model.model_type] ?? props.model.model_type
})

const errMessage = computed(() => {
  if (props.model.meta?.message) {
    if (props.model.meta.message === 'pull model manifest: file does not exist') {
      return t('model.messages.missingOllama', { name: props.model.model_name })
    }
    return props.model.meta.message
  }
  return ''
})

function handleClick(event: MouseEvent) {
  if (props.disabled) return
  emit('click', event)
}
</script>

<template>
  <MkResourceCard
    class="relative overflow-hidden"
    :disabled="disabled"
    :title="model.name"
    :nick_name="model.nick_name || '-'"
    :create_time="model.create_time"
    @click="handleClick"
  >
    <template #icon>
      <span class="block h-6 w-6" :innerHTML="provider.icon" />
    </template>
    <template #title="{ title }">
      <h6 class="min-w-0 truncate" :title="title">{{ title }}</h6>

      <MkTooltip :content="errMessage" v-if="model.status === MODEL_STATUS.ERROR">
        <MkIcon name="icon_warning_filled" class="text-danger!" />
      </MkTooltip>
      <MkTooltip v-if="model.status === MODEL_STATUS.PAUSE_DOWNLOAD" :content="t('model.messages.downloadFailed', { name: model.model_name })">
        <MkIcon name="icon_warning_filled" type="danger" />
      </MkTooltip>
    </template>
    <template #tag>
      <el-tag v-if="props.shared" size="small" type="info">{{ t('resource.shared') }}</el-tag>
    </template>

    <ul class="space-y-2">
      <li class="flex gap-4">
        <span class="shrink-0">{{ t('model.fields.type.label') }}</span>
        <span class="min-w-0 flex-1 truncate text-N900" :title="modelTypeLabel">
          {{ modelTypeLabel }}
        </span>
      </li>
      <li class="flex gap-4">
        <span class="shrink-0">{{ t('model.fields.baseModel.label') }}</span>
        <span class="min-w-0 flex-1 truncate text-N900" :title="model.model_name">
          {{ model.model_name }}
        </span>
      </li>
    </ul>
    <!-- 下载状态 -->
    <ModelDownloadStatus v-if="model.status === MODEL_STATUS.DOWNLOAD" :api="api" :model="model" :refresh="refresh" />

    <template #footer="{ Action, ActionDropdown }">
      <component :is="Action" v-if="!disabled">
        <component :is="ActionDropdown">
          <slot name="action-dropdown" />
        </component>
      </component>
    </template>
  </MkResourceCard>
</template>
