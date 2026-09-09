<script setup lang="ts">
import { computed } from 'vue'
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import { getFileUrl } from '@/utils/common'
import { getFileIconUrl } from '@/utils/icon'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'SearchKnowledgeNodeDetail' })

const props = defineProps<{
  data: ExecutionNodeDetail
}>()

interface SearchParagraph {
  content?: string
  document_name?: string
  knowledge_name?: string
  knowledge_type?: string
  similarity?: number
  title?: string
}

const sortedParagraphs = computed<SearchParagraph[]>(() =>
  [...((props.data?.paragraph_list as SearchParagraph[] | undefined) || [])].sort(
    (a, b) => (b.similarity || 0) - (a.similarity || 0),
  ),
)
</script>

<template>
  <DetailContainer :data="data">
    <template #header="{ show }">
      <BaseHeader :data="data" :show="show" />
    </template>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">检索内容</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">{{ data.question || '-' }}</div>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">检索结果</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <template v-if="sortedParagraphs.length > 0">
          <div
            v-for="(paragraph, paragraphIndex) in sortedParagraphs"
            :key="paragraphIndex"
            class="overflow-hidden rounded-md bg-white p-2 mb-2"
          >
            <div class="flex-between">
              <span class="truncate">{{ paragraphIndex + 1 }}.{{ paragraph.title || '-' }}</span>
              <span class="ml-2 shrink-0 text-primary">
                {{ paragraph.similarity?.toFixed(3) }}
              </span>
            </div>
            <el-scrollbar height="150" class="mt-1">
              <MdPreview
                :model-value="paragraph.content"
                class="paragraph-answer"
                no-img-zoom-in
              />
            </el-scrollbar>
            <div
              v-if="paragraph.document_name?.trim()"
              class="mt-1 flex items-center gap-1"
            >
              <img :src="getFileIconUrl(paragraph.document_name.trim())" alt="" width="20" />
              <a
                v-if="paragraph.meta?.source_file_id || paragraph.meta?.source_url"
                :href="getFileUrl(paragraph.meta?.source_file_id) || paragraph.meta?.source_url"
                target="_blank"
                class="truncate"
                :title="paragraph.document_name.trim()"
              >
                {{ paragraph.document_name }}
              </a>
              <span v-else class="truncate" :title="paragraph.document_name.trim()">
                {{ paragraph.document_name.trim() }}
              </span>
            </div>
            <div class="mt-1 flex items-center gap-1 border-t border-dashed pt-1">
              <KnowledgeIcon :type="paragraph.knowledge_type" :size="18" />
              <span class="truncate">{{ paragraph.knowledge_name || '-' }}</span>
            </div>
          </div>
        </template>
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>

<style scoped lang="scss">
:deep(.paragraph-answer.md-editor) {
  background: transparent;
  height: auto;
}
</style>
