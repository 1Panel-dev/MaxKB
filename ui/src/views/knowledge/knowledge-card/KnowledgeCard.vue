<script setup lang="ts">
import type { KnowledgeItem } from '@/api/types'
import MkSourceCard from '@/components/mk-source-card/index.vue'
import { numberFormat } from '@/utils/number'

defineOptions({ name: 'KnowledgeCard' })

defineProps<{ knowledge: KnowledgeItem; shared?: boolean; selectable?: boolean; selected?: boolean }>()

const emit = defineEmits<{ selected: [selected: boolean] }>()
defineSlots<{ 'action-dropdown'?: () => unknown }>()
</script>

<template>
  <MkSourceCard
    :create_time="knowledge.create_time"
    :nick_name="knowledge.nick_name || '-'"
    :title="knowledge.name"
    :selectable="selectable"
    :selected="selected"
    @selected="emit('selected', $event)"
  >
    <template #icon>
      <KnowledgeIcon :type="knowledge.type" />
    </template>

    <template #tag>
      <el-tag v-if="shared" size="small" type="info">共享</el-tag>
    </template>

    <p class="line-clamp-2" :title="knowledge.desc ?? undefined">
      {{ knowledge.desc }}
    </p>

    <template #footer="{ Action, ActionDropdown }">
      <span>
        <span class="mr-1 font-semibold">{{ knowledge.document_count ?? 0 }}</span>
        <span class="text-N600">文档</span>
      </span>
      <el-divider direction="vertical" />
      <span>
        <strong class="mr-1 font-semibold">{{ numberFormat(knowledge.char_length) }}</strong>
        <span class="text-N600">字符</span>
      </span>

      <component :is="Action" v-if="!shared">
        <component :is="ActionDropdown">
          <slot name="action-dropdown" />
        </component>
      </component>
    </template>
  </MkSourceCard>
</template>
