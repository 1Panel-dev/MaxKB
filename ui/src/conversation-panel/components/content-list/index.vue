<script setup lang="ts">
import { computed } from 'vue'
import Content from '@/conversation-panel/components/content/index.vue'

defineOptions({ name: 'ConversationContentList' })

interface ContentItem {
  type: string
  id?: string
  content?: unknown
  children?: ContentItem[]
  [key: string]: unknown
}

const props = defineProps<{ contentList: ContentItem[] }>()

// 隐藏审批和空正文；sort 为稳定排序，相同 id 的内容保留原始顺序。
const displayContents = computed(() => {
  const sortedContents = props.contentList
    .filter((content) => {
      if (content.type === 'APPROVAL') return false
      return !((content.type === 'TEXT' || content.type === 'HTML') && !content.content)
    })
    .sort((leftContent, rightContent) => (leftContent.id || '').localeCompare(rightContent.id || ''))

  return foldToolGroups(sortedContents)
})

// 排序后相邻的 TOOL（2 个起）折叠为 GROUP_TOOL；仅为展示结构，不写回数据。
// 分组 id 取首个工具 id，流式追加时保持不变，组件得以复用
function foldToolGroups(contentItems: ContentItem[]): ContentItem[] {
  const foldedContents: ContentItem[] = []

  for (const content of contentItems) {
    const lastContent = foldedContents[foldedContents.length - 1]

    if (content.type === 'TOOL' && lastContent?.type === 'GROUP_TOOL') {
      lastContent.children!.push(content)
    } else if (content.type === 'TOOL' && lastContent?.type === 'TOOL') {
      foldedContents[foldedContents.length - 1] = {
        type: 'GROUP_TOOL',
        id: `${lastContent.id}_group`,
        children: [lastContent, content],
      }
    } else {
      foldedContents.push(content)
    }
  }

  return foldedContents
}
</script>

<template>
  <div class="w-full space-y-3">
    <template v-for="(content, index) in displayContents" :key="`${content.type}:${content.id ?? index}`">
      <Content :content="content" />
    </template>
  </div>
</template>
