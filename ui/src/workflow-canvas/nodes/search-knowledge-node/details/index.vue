<script setup lang="ts">
import { computed } from 'vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import { getFileUrl } from '@/utils/common'
import { getFileIconUrl } from '@/utils/icon'
import { DOCUMENT_RESOURCE_TYPE } from '@/api/enums'
import type { DocumentResourceType, KnowledgeHitTestAsset } from '@/api/types'
import fileImageIcon from '@/assets/file-type/file-image-icon.svg'
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
      <!-- TODO -->
      <div class="space-y-2">
        <template v-if="sortedParagraphs.length > 0">
          <div v-for="(paragraph, paragraphIndex) in sortedParagraphs" :key="paragraphIndex" class="overflow-hidden rounded-md bg-white p-2 mb-2">
            <div class="flex-between">
              <span class="text-N600 text-sm font-medium">#{{ paragraphIndex + 1 }} {{ paragraph.title || '-' }}</span>
              <span class="text-primary text-sm">
                {{ paragraph.similarity?.toFixed(3) }}
              </span>
            </div>
            <el-scrollbar max-height="150" class="my-2">
              <!-- 放大预览召回图片 -->
              <el-image
                v-if="getParagraphImageUrl(paragraph)"
                :src="getParagraphImageUrl(paragraph)"
                :alt="paragraph.title || ''"
                fit="contain"
                class="mb-2 h-28 w-full"
                :preview-src-list="[getParagraphImageUrl(paragraph)]"
                preview-teleported
              />
              <MdPreview :model-value="paragraph.content" no-img-zoom-in />
            </el-scrollbar>
            <div v-if="paragraph.document_name?.trim()" class="mt-1 flex-align-center gap-1">
              <img
                :src="
                  paragraph.document_resource_type === DOCUMENT_RESOURCE_TYPE.IMAGE ? fileImageIcon : getFileIconUrl(paragraph.document_name.trim())
                "
                alt=""
                width="20"
              />
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
            <div class="mt-1 flex-align-center gap-1 border-t border-dashed pt-1">
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
