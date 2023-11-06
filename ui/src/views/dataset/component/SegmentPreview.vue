<template>
  <el-tabs v-model="activeName" class="segment-tabs" @tab-click="handleClick">
    <template v-for="(item, index) in data" :key="index">
      <el-tab-pane :label="item.name" :name="index">
        <template #label>
          <div class="flex">
            <img :src="getImgUrl(item && item?.name)" alt="" height="22" />
            <span class="ml-4">{{ item?.name }}</span>
          </div>
        </template>
        <el-scrollbar>
          <div class="segment-list">
            <el-card
              v-for="(child, i) in item.content"
              :key="i"
              shadow="never"
              class="card-never mb-16"
            >
              <div class="flex-between">
                <span>{{ child.title }}</span>
                <div>
                  <el-button link>
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button link>
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
              <div class="lighter mt-12">
                {{ child.content }}
              </div>
              <div class="lighter mt-12">
                <el-text type="info"> {{ child.content.length }} 个字符 </el-text>
              </div>
            </el-card>
          </div>
        </el-scrollbar>
      </el-tab-pane>
    </template>
  </el-tabs>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import type { TabsPaneContext } from 'element-plus'
import { filesize, getImgUrl } from '@/utils/utils'
defineProps({
  data: {
    type: Array<any>,
    default: () => []
  }
})

const activeName = ref(0)
onMounted(() => {})

const handleClick = (tab: TabsPaneContext, event: Event) => {
  console.log(tab, event)
}
</script>
<style scoped lang="scss">
.segment-tabs {
  :deep(.el-tabs__item) {
    background: var(--app-text-color-primary-light-1);
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
.segment-list {
  height: calc(100vh - 340px);
}
</style>
