<template>
  <div class="content-list">
    <div v-for="(content, index) in contents" :key="`${content.type}:${content.id ?? index}`" class="content-item">
      <Content :type="content.type" :content="content" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Content from '@/conversation-panel/components/content/index.vue'

const props = defineProps<{ contentList: Array<any> }>()

const contents = computed(() => {
  const sortedContents = props.contentList
    .filter((item) => item.type !== 'APPROVAL')
    .map((item, index) => ({ item, index }))
    .sort((a, b) => {
      const idA = a.item.id || ''
      const idB = b.item.id || ''
      if (idA !== idB) {
        return idA.localeCompare(idB)
      }
      return a.index - b.index
    })
    .map(({ item }) => item)
    .filter((item) => !((item.type === 'TEXT' || item.type === 'HTML') && !item.content))
  return foldToolGroups(sortedContents)
})

// 排序后相邻的 TOOL（2 个起）折叠为 GROUP_TOOL；仅为展示结构，不写回数据。
// 分组 id 取首个工具 id，流式追加时保持不变，组件得以复用
function foldToolGroups(contentItems: any[]) {
  const foldedContents: any[] = []
  for (const item of contentItems) {
    const last = foldedContents[foldedContents.length - 1]
    if (item.type === 'TOOL' && last?.type === 'GROUP_TOOL') {
      last.children.push(item)
    } else if (item.type === 'TOOL' && last?.type === 'TOOL') {
      foldedContents[foldedContents.length - 1] = { type: 'GROUP_TOOL', id: `${last.id}_group`, children: [last, item] }
    } else {
      foldedContents.push(item)
    }
  }
  return foldedContents
}
</script>

<style scoped lang="scss">
.content-list {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.content-item {
  width: 100%;
}
</style>
