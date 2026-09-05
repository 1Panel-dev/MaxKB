<template>
  <div class="content-list">
    <div v-for="(content, index) in contents" :key="index" class="content-item">
      <Content :type="content.type" :content="content" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Content from '@/components/conversation/content/index.vue'

const props = defineProps<{ contentList: Array<any> }>()

const contents = computed(() => {
  return props.contentList
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
    .filter((item) => !(item.type === 'TEXT' && !item.content))
})
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
