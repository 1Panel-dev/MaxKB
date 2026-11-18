<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { KnowledgeItem } from '@/api/types'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import { numberFormat } from '@/utils/number'

defineOptions({ name: 'KnowledgeCard' })

const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{
  disabled?: boolean
  knowledge: KnowledgeItem
  shared?: boolean
  selectable?: boolean
  selected?: boolean
}>()

const emit = defineEmits<{ click: []; selected: [selected: boolean] }>()
defineSlots<{ 'action-dropdown'?: () => unknown }>()

const documentCount = computed(() => (props.knowledge.document_count ?? 0) + (props.knowledge.image_count ?? 0))

function handleOpen() {
  if (!props.selectable) emit('click')
}
</script>

<template>
  <MkResourceCard
    :create_time="knowledge.create_time"
    :nick_name="knowledge.nick_name || '-'"
    :title="knowledge.name"
    :selectable="selectable"
    :selected="selected"
    :class="{ 'cursor-pointer': !selectable }"
    @click="handleOpen"
    @selected="emit('selected', $event)"
  >
    <template #icon>
      <KnowledgeIcon :type="knowledge.type" />
    </template>

    <template #tag>
      <el-tag v-if="shared" size="small" type="info">{{ t('resource.shared') }}</el-tag>
    </template>

    <p class="line-clamp-2" :title="knowledge.desc ?? undefined">
      {{ knowledge.desc }}
    </p>

    <template #footer="{ Action, ActionDropdown }">
      <span class="text-N600">
        <span class="font-semibold text-N900">{{ documentCount }}</span>
        {{ t('knowledge.stats.documents', documentCount) }}
      </span>
      <el-divider direction="vertical" />
      <span class="text-N600">
        <span class="font-semibold text-N900">{{ numberFormat(knowledge.char_length) }}</span>
        {{ t('knowledge.stats.characters', knowledge.char_length ?? 0) }}
      </span>
      <template v-if="knowledge.type === KNOWLEDGE_TYPE.BASE || knowledge.type === KNOWLEDGE_TYPE.WORKFLOW">
        <el-divider direction="vertical" />
        <span class="text-N600">
          <span class="font-semibold text-N900">{{ numberFormat(knowledge.image_count ?? 0) }}</span>
          {{ t('knowledge.stats.images', knowledge.image_count ?? 0) }}
        </span>
      </template>
      <component :is="Action" v-if="!disabled">
        <component :is="ActionDropdown">
          <slot name="action-dropdown" />
        </component>
      </component>
    </template>
  </MkResourceCard>
</template>
