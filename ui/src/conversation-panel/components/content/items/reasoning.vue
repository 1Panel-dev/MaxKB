<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { useBottomFollow } from '@/conversation-panel/core/bottom-follow'

defineOptions({ name: 'ConversationReasoningContent' })

defineProps<{ content: { content?: string | null; status?: string } }>()
// 默认收起，思考中也只显示状态文案，手动展开后查看内容
const isExpanded = ref(false)

// 思考内容限高滚动，高度与新建文件的差异区一致；流式输出时跟随到底部
useBottomFollow(useTemplateRef<HTMLElement>('reasoningScrollRef'))
</script>

<template>
  <!-- 展开或收起思考内容 -->
  <MkCollapse v-model:expanded="isExpanded" indicator-position="after" trigger-class="group text-N500! mb-2 w-fit hover:text-N900!">
    <template #indicator="{ expanded }">
      <MkIcon
        name="icon_right_outlined"
        :size="12"
        class="transition-transform text-N500! group-hover:text-N900!"
        :class="{ 'rotate-90': expanded }"
      />
    </template>
    <template #label>
      <MkIcon name="icon_two-ellipses_outlined" />
      <span class="-mx-1" :class="{ 'mk-dotting': content.status === 'RUNNING' }">
        {{ content.status === 'RUNNING' ? '思考中' : '思考完成' }}
      </span>
    </template>
    <div ref="reasoningScrollRef" class="max-h-[400px] overflow-y-auto text-N500! whitespace-pre-wrap break-words">
      {{ content.content }}
    </div>
  </MkCollapse>
</template>

<style scoped lang="scss"></style>
