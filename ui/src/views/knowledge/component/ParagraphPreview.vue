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
          <el-text type="info">{{ item.content.length }} {{ $t('views.paragraph.title') }}</el-text>
        </div>
        <div class="paragraph-list" v-if="activeName == index">
          <el-scrollbar>
            <ParagraphList
              v-model="item.content"
              :isConnect="isConnect"
              :knowledge-id="knowledgeId"
            />
          </el-scrollbar>
        </div>
      </el-tab-pane>
    </template>
  </el-tabs>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { getImgUrl } from '@/utils/common'
import ParagraphList from './ParagraphList.vue'

defineProps({
  data: {
    type: Array<any>,
    default: () => [],
  },
  isConnect: Boolean,
  knowledgeId: String,
})

const activeName = ref(0)
</script>
<style scoped lang="scss">
.paragraph-list {
  height: calc(100vh - 319px);
}
</style>
