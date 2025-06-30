<template>
  <el-scrollbar>
    <div class="paragraph-source-height p-16 pb-0">
      <el-form label-position="top">
        <el-form-item :label="$t('chat.paragraphSource.question')">
          <el-input :value="props.detail?.problem_text" disabled />
        </el-form-item>
        <el-form-item :label="$t('chat.paragraphSource.optimizationQuestion')">
          <el-input :value="props.detail?.padding_problem_text" disabled />
        </el-form-item>
        <el-form-item :label="$t('chat.KnowledgeSource.referenceParagraph')">
          <div v-if="props.detail?.paragraph_list.length > 0" class="w-full">
            <template v-for="(item, index) in props.detail.paragraph_list" :key="index">
              <ParagraphCard :data="item" :content="item.content" :index="index" />
            </template>
          </div>
          <span v-else> - </span>
        </el-form-item>
      </el-form>
    </div>
  </el-scrollbar>
</template>

<script setup lang="ts">
import ParagraphCard from '@/components/ai-chat/component/ParagraphCard.vue'

const props = defineProps<{
  detail?: any
}>()
</script>