<script setup lang="ts">
import { computed } from 'vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import { getFileUrl } from '@/utils/common'
import { getFileIconUrl } from '@/utils/icon'
import { DOCUMENT_RESOURCE_TYPE, KNOWLEDGE_HIT_UNIT_TYPE } from '@/api/enums'
import type { DocumentResourceType, KnowledgeHitTestAsset } from '@/api/types'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'SearchKnowledgeNodeDetail' })

const props = defineProps<{
  data: ExecutionNodeDetail
}>()

interface SearchParagraph {
  content?: string
  document_name?: string
  document_resource_type?: DocumentResourceType | null
  document_image_id?: string | null
  hit_asset?: KnowledgeHitTestAsset | null
  knowledge_name?: string
  knowledge_type?: string
  meta?: {
    source_file_id?: string
    source_url?: string
  }
  similarity?: number
  title?: string
}

const sortedParagraphs = computed<SearchParagraph[]>(() =>
  [...((props.data?.paragraph_list as SearchParagraph[] | undefined) || [])].sort((a, b) => (b.similarity || 0) - (a.similarity || 0)),
)

function getParagraphImageUrl(paragraph: SearchParagraph) {
  const fileId =
    (paragraph.document_resource_type === DOCUMENT_RESOURCE_TYPE.IMAGE ? paragraph.document_image_id : undefined) || paragraph.hit_asset?.file_id
  if (!fileId || paragraph.content?.includes(`/oss/file/${fileId}`)) return ''
  return getFileUrl(fileId)
}
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
      <h6 class="mb-2">检索结果</h6>
      <div class="space-y-2" v-if="sortedParagraphs.length > 0">
        <template v-for="(paragraph, paragraphIndex) in sortedParagraphs" :key="paragraphIndex">
          <MkSourceCard :title="`${paragraph.title || '-'}`" disabled>
            <template #title="{ title }">
              <span class="flex-align-center min-w-0 gap-2">
                <h4 class="shrink-0">{{ `#${paragraphIndex + 1}` }}</h4>
                <el-divider direction="vertical" />
                <h4 class="min-w-0 truncate" :title="title">{{ title }}</h4>
              </span>
            </template>
            <template #tag>
              <div class="flex-align-center gap-2">
                <el-tag size="small" type="info">
                  {{ paragraph.document_resource_type === KNOWLEDGE_HIT_UNIT_TYPE.IMAGE ? '图片向量' : '文本向量' }}
                </el-tag>
                <h6 class="shrink-0 text-primary">{{ paragraph.similarity?.toFixed(3) }}</h6>
              </div>
            </template>

            <!-- 放大预览召回图片 -->
            <el-image
              v-if="getParagraphImageUrl(paragraph)"
              :src="getParagraphImageUrl(paragraph)"
              :alt="paragraph.title || ''"
              fit="contain"
              class="mb-2"
              :preview-src-list="[getParagraphImageUrl(paragraph)]"
              preview-teleported
            />

            <MdPreview :model-value="paragraph.content" no-img-zoom-in />

            <!-- 打开来源文档 -->

            <a
              v-if="paragraph.document_name?.trim()"
              :href="paragraph.meta?.source_file_id || paragraph.meta?.source_url || undefined"
              target="_blank"
              rel="noopener noreferrer"
              :download="paragraph.document_name.trim()"
              class="mt-2 block min-w-0"
            >
              <el-card shadow="never" class="small cursor-pointer">
                <div class="flex-align-center gap-2">
                  <img :src="getFileIconUrl(paragraph.document_name.trim())" alt="" width="24" />
                  <span class="min-w-0 truncate" :title="paragraph.document_name.trim()">{{ paragraph.document_name.trim() }}</span>
                </div>
              </el-card>
            </a>

            <template #footer>
              <div class="flex-align-center w-full gap-2 border-t pt-2">
                <KnowledgeIcon :type="paragraph.knowledge_type" :size="16" class="small" />
                <span class="truncate">{{ paragraph.knowledge_name || '-' }}</span>
              </div>
            </template>
          </MkSourceCard>
        </template>
      </div>
      <template v-else>-</template>
    </div>
  </DetailContainer>
</template>
