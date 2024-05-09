<template>
  <el-tabs v-model="activeName" class="paragraph-tabs">
    <template v-for="(item, index) in data" :key="index">
      <el-tab-pane :label="item.name" :name="index">
        <template #label>
          <div class="flex-center">
            <img :src="getImgUrl(item && item?.name)" alt="" height="16" />
            <span class="ml-4">{{ item?.name }}</span>
          </div>
        </template>
        <div class="mb-16">
          <el-text type="info">{{ item.content.length }} 段落</el-text>
        </div>
        <div class="paragraph-list" v-if="activeName == index">
          <el-scrollbar>
            <ParagraphList v-model="item.content" :isConnect="isConnect"> </ParagraphList>
          </el-scrollbar>
        </div>
      </el-tab-pane>
    </template>
  </el-tabs>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { getImgUrl } from '@/utils/utils'
import ParagraphList from './ParagraphList.vue'

defineProps({
  data: {
    type: Array<any>,
    default: () => []
  },
  isConnect: Boolean
})

const activeName = ref(0)
</script>
<style scoped lang="scss">
.paragraph-tabs {
  :deep(.el-tabs__item) {
    background: var(--app-text-color-light-1);
    margin: 4px;
    border-radius: 4px;
    padding: 5px 10px 5px 8px !important;
    height: auto;
    &:nth-child(2) {
      margin-left: 0;
    }
    &:last-child {
      margin-right: 0;
    }
    &.is-active {
      border: 1px solid var(--el-color-primary);
      background: var(--el-color-primary-light-9);
      color: var(--el-text-color-primary);
    }
  }
  :deep(.el-tabs__nav-wrap::after) {
    display: none;
  }
  :deep(.el-tabs__active-bar) {
    display: none;
  }
}
.paragraph-list {
  height: calc(var(--create-dataset-height) - 101px);
}
</style>
