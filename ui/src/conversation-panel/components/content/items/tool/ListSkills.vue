<script setup lang="ts">
import { computed } from 'vue'
import type { ChatContent } from '@/api/types'

defineOptions({ name: 'ConversationListSkillsContent' })

const props = defineProps<{ content: ChatContent; loading: boolean }>()
const expanded = defineModel<boolean>('expanded', { required: true })

const summary = computed(() => props.content.summary || '')
</script>

<template>
  <!-- 展开或收起技能列表 -->
  <MkCollapse class="w-full" v-model:expanded="expanded" indicator-position="after" trigger-class="group text-N500! mb-2 w-fit hover:text-N900!">
    <template #indicator="{ expanded }">
      <MkIcon
        name="icon_right_outlined"
        :size="12"
        class="transition-transform text-N500! group-hover:text-N900!"
        :class="{ 'rotate-90': expanded }"
      />
    </template>
    <template #label>
      <span v-if="loading" class="mk-conversation-loading" />
      <svg class="shrink-0" viewBox="0 0 16 16" width="16" height="16" fill="none">
        <path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" />
      </svg>
      <span class="min-w-0 max-w-[300px] truncate" :title="'list_skills'">list_skills</span>
      <span class="shrink-0 font-mono text-xs text-N500" v-if="summary">{{ summary }}</span>
    </template>
    <div v-if="content.content" class="py-1">
      <div class="rf-block">
        <pre class="rf-content">{{ content.content }}</pre>
      </div>
    </div>
  </MkCollapse>
</template>

<style scoped>
.rf-block {
  background: var(--mk-N100);
  border: 1px solid var(--mk-N300);
  border-radius: 6px;
  overflow: hidden;
  max-height: 360px;
  overflow-y: auto;
}

.rf-content {
  margin: 0;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 12px;
  line-height: 1.5;
  color: var(--mk-N900);
  white-space: pre-wrap;
  word-break: break-all;
  padding: 8px 12px;
}
</style>
