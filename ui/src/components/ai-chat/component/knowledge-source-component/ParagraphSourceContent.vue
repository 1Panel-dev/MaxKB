<template>
  <el-scrollbar>
    <div class="paragraph-source-height p-8">
      <div v-if="props.detail?.paragraph_list.length > 0" class="w-full">
        <template v-for="(item, index) in props.detail.paragraph_list" :key="index">
          <ParagraphCard :data="item" :content="item.content" :index="index" />
        </template>
      </div>
      <span v-else> {{ $t('chat.KnowledgeSource.noSource') }}</span>
    </div>
  </el-scrollbar>
</template>

<script setup lang="ts">
import ParagraphCard from '@/components/ai-chat/component/knowledge-source-component/ParagraphCard.vue'

const props = defineProps<{
  detail?: any
}>()
</script>
<style lang="scss" scoped>
.paragraph-source-height {
  max-height: calc(100vh - 260px);
}
</style>
