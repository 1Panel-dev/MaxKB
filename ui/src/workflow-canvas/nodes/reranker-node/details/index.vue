<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import { getFileUrl } from '@/utils/common'
import { getFileIconUrl } from '@/utils/icon'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'RerankerNodeDetail' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">检索内容</h6>
      <div>{{ data.question || '-' }}</div>
    </div>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">重排内容</h6>
      <div class="space-y-2">
        <template v-if="data.document_list?.length > 0">
          <template v-for="(paragraph, paragraphIndex) in data.document_list" :key="paragraphIndex">
            <div class="mb-2 overflow-hidden rounded-md bg-white p-2">
              <div class="flex-between">
                <span class="truncate">#{{ Number(paragraphIndex) + 1 }} {{ paragraph.metadata?.title || '-' }}</span>
                <span class="ml-2 shrink-0 text-primary">
                  {{ paragraph.metadata?.similarity != null ? Number(paragraph.metadata.similarity).toFixed(3) : '' }}
                </span>
              </div>
              <el-scrollbar max-height="150" class="mt-1">
                <MdPreview :model-value="paragraph.page_content || paragraph.metadata?.content || ''" no-img-zoom-in />
              </el-scrollbar>
              <div v-if="paragraph.metadata?.document_name?.trim()" class="mt-1 flex-align-center gap-1">
                <img :src="getFileIconUrl(paragraph.metadata.document_name.trim())" alt="" width="20" />
                <a
                  v-if="paragraph.metadata?.source_file_id || paragraph.metadata?.source_url"
                  :href="getFileUrl(paragraph.metadata.source_file_id) || paragraph.metadata.source_url"
                  target="_blank"
                  class="truncate"
                  :title="paragraph.metadata.document_name.trim()"
                >
                  {{ paragraph.metadata.document_name }}
                </a>
                <span v-else class="truncate" :title="paragraph.metadata.document_name.trim()">
                  {{ paragraph.metadata.document_name.trim() }}
                </span>
              </div>
              <div class="mt-1 flex-align-center gap-1 border-t border-dashed pt-1">
                <KnowledgeIcon :type="paragraph.metadata?.knowledge_type" :size="18" />
                <span class="truncate">{{ paragraph.metadata?.knowledge_name || '-' }}</span>
              </div>
            </div>
          </template>
        </template>
        <template v-else>-</template>
      </div>
    </div>

    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">重排结果</h6>
      <div class="space-y-2">
        <template v-if="data.result_list?.length > 0">
          <template v-for="(paragraph, paragraphIndex) in data.result_list" :key="paragraphIndex">
            <div class="mb-2 overflow-hidden rounded-md bg-white p-2">
              <div class="flex-between">
                <span class="truncate">{{ Number(paragraphIndex) + 1 }}.{{ paragraph.metadata?.title || '-' }}</span>
                <span class="ml-2 shrink-0 text-primary">
                  {{ paragraph.metadata?.relevance_score != null ? Number(paragraph.metadata.relevance_score).toFixed(3) : '' }}
                </span>
              </div>
              <el-scrollbar height="150" class="mt-1">
                <MdPreview :model-value="paragraph.page_content || paragraph.metadata?.content || ''" no-img-zoom-in />
              </el-scrollbar>
              <div v-if="paragraph.metadata?.document_name?.trim()" class="mt-1 flex-align-center gap-1">
                <img :src="getFileIconUrl(paragraph.metadata.document_name.trim())" alt="" width="20" />
                <a
                  v-if="paragraph.metadata?.source_file_id || paragraph.metadata?.source_url"
                  :href="getFileUrl(paragraph.metadata.source_file_id) || paragraph.metadata.source_url"
                  target="_blank"
                  class="truncate"
                  :title="paragraph.metadata.document_name.trim()"
                >
                  {{ paragraph.metadata.document_name }}
                </a>
                <span v-else class="truncate" :title="paragraph.metadata.document_name.trim()">
                  {{ paragraph.metadata.document_name.trim() }}
                </span>
              </div>
              <div class="mt-1 flex-align-center gap-1 border-t border-dashed pt-1">
                <KnowledgeIcon :type="paragraph.metadata?.knowledge_type" :size="18" />
                <span class="truncate">{{ paragraph.metadata?.knowledge_name || '-' }}</span>
              </div>
            </div>
          </template>
        </template>
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
