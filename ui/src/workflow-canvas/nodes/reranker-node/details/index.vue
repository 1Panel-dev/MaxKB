<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import { getFileUrl } from '@/utils/common'
import { getFileIconUrl } from '@/utils/icon'
import { DOCUMENT_RESOURCE_TYPE } from '@/api/enums'
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

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">检索内容</h6>
      <div>{{ data.question || '-' }}</div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">重排内容</h6>
      <div v-if="data.document_list?.length > 0" class="space-y-2">
        <template v-for="(paragraph, paragraphIndex) in data.document_list" :key="paragraphIndex">
          <MkSourceCard :title="paragraph.metadata?.title || '-'" disabled>
            <template #title="{ title }">
              <span class="flex-align-center min-w-0 gap-2">
                <h4 class="shrink-0">{{ `#${Number(paragraphIndex) + 1}` }}</h4>
                <el-divider direction="vertical" />
                <h4 class="min-w-0 truncate" :title="title">{{ title }}</h4>
              </span>
            </template>
            <template #tag>
              <div class="flex-align-center gap-2">
                <el-tag size="small" type="info">
                  {{ paragraph.metadata?.document_resource_type === DOCUMENT_RESOURCE_TYPE.IMAGE ? '图片向量' : '文本向量' }}
                </el-tag>
                <h6 class="shrink-0 text-primary">
                  {{ paragraph.metadata?.similarity != null ? Number(paragraph.metadata.similarity).toFixed(3) : '' }}
                </h6>
              </div>
            </template>

            <MdPreview :model-value="paragraph.page_content || paragraph.metadata?.content || ''" no-img-zoom-in />

            <!-- 打开来源文档 -->
            <a
              v-if="paragraph.metadata?.document_name?.trim()"
              :href="getFileUrl(paragraph.metadata.source_file_id) || paragraph.metadata.source_url || undefined"
              target="_blank"
              rel="noopener noreferrer"
              :download="paragraph.metadata.document_name.trim()"
              class="mt-2 block min-w-0"
            >
              <el-card shadow="never" class="small cursor-pointer">
                <div class="flex-align-center gap-2">
                  <img :src="getFileIconUrl(paragraph.metadata.document_name.trim())" alt="" width="24" />
                  <span class="min-w-0 truncate" :title="paragraph.metadata.document_name.trim()">{{ paragraph.metadata.document_name.trim() }}</span>
                </div>
              </el-card>
            </a>

            <template #footer>
              <div class="flex-align-center w-full gap-2 border-t pt-2">
                <KnowledgeIcon :type="paragraph.metadata?.knowledge_type" :size="16" class="small" />
                <span class="truncate">{{ paragraph.metadata?.knowledge_name || '-' }}</span>
              </div>
            </template>
          </MkSourceCard>
        </template>
      </div>
      <template v-else>-</template>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">重排结果</h6>
      <div v-if="data.result_list?.length > 0" class="space-y-2">
        <template v-for="(paragraph, paragraphIndex) in data.result_list" :key="paragraphIndex">
          <MkSourceCard :title="paragraph.metadata?.title || '-'" disabled>
            <template #title="{ title }">
              <span class="flex-align-center min-w-0 gap-2">
                <h4 class="shrink-0">{{ `#${Number(paragraphIndex) + 1}` }}</h4>
                <el-divider direction="vertical" />
                <h4 class="min-w-0 truncate" :title="title">{{ title }}</h4>
              </span>
            </template>
            <template #tag>
              <div class="flex-align-center gap-2">
                <el-tag size="small" type="info">
                  {{ paragraph.metadata?.document_resource_type === DOCUMENT_RESOURCE_TYPE.IMAGE ? '图片向量' : '文本向量' }}
                </el-tag>
                <h6 class="shrink-0 text-primary">
                  {{ paragraph.metadata?.relevance_score != null ? Number(paragraph.metadata.relevance_score).toFixed(3) : '' }}
                </h6>
              </div>
            </template>

            <MdPreview :model-value="paragraph.page_content || paragraph.metadata?.content || ''" no-img-zoom-in />

            <!-- 打开来源文档 -->
            <a
              v-if="paragraph.metadata?.document_name?.trim()"
              :href="getFileUrl(paragraph.metadata.source_file_id) || paragraph.metadata.source_url || undefined"
              target="_blank"
              rel="noopener noreferrer"
              :download="paragraph.metadata.document_name.trim()"
              class="mt-2 block min-w-0"
            >
              <el-card shadow="never" class="small cursor-pointer">
                <div class="flex-align-center gap-2">
                  <img :src="getFileIconUrl(paragraph.metadata.document_name.trim())" alt="" width="24" />
                  <span class="min-w-0 truncate" :title="paragraph.metadata.document_name.trim()">{{ paragraph.metadata.document_name.trim() }}</span>
                </div>
              </el-card>
            </a>

            <template #footer>
              <div class="flex-align-center w-full gap-2 border-t pt-2">
                <KnowledgeIcon :type="paragraph.metadata?.knowledge_type" :size="16" class="small" />
                <span class="truncate">{{ paragraph.metadata?.knowledge_name || '-' }}</span>
              </div>
            </template>
          </MkSourceCard>
        </template>
      </div>
      <template v-else>-</template>
    </div>
  </DetailContainer>
</template>
