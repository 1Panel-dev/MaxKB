<script setup lang="ts">
import { computed } from 'vue'
import { I18nT, useI18n } from 'vue-i18n'
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
      <I18nT keypath="knowledge.stats.documents" tag="span" scope="global" :plural="documentCount" class="text-N600">
        <template #count>
          <span class="font-semibold text-N900">{{ documentCount }}</span>
        </template>
      </I18nT>
      <el-divider direction="vertical" />
      <I18nT keypath="knowledge.stats.characters" tag="span" scope="global" :plural="knowledge.char_length ?? 0" class="text-N600">
        <template #count>
          <span class="font-semibold text-N900">{{ numberFormat(knowledge.char_length) }}</span>
        </template>
      </I18nT>
      <template v-if="knowledge.type === KNOWLEDGE_TYPE.BASE || knowledge.type === KNOWLEDGE_TYPE.WORKFLOW">
        <el-divider direction="vertical" />
        <I18nT keypath="knowledge.stats.images" tag="span" scope="global" :plural="knowledge.image_count ?? 0" class="text-N600">
          <template #count>
            <span class="font-semibold text-N900">{{ numberFormat(knowledge.image_count ?? 0) }}</span>
          </template>
        </I18nT>
      </template>
      <component :is="Action" v-if="!disabled">
        <component :is="ActionDropdown">
          <slot name="action-dropdown" />
        </component>
      </component>
    </template>
  </MkResourceCard>
</template>
