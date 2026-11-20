<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import { getFileIconUrl } from '@/utils/icon'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'DocumentExtractNodeDetail' })

const props = defineProps<{
  data: ExecutionNodeDetail
}>()

interface ExtractedDocument {
  name?: string
  content?: string
  meta?: {
    source_type?: string
  }
}

// 优先展示提取后的文档，兼容旧详情的 content 数组。
const documents = computed<ExtractedDocument[]>(
  () =>
    props.data.document_list ??
    (props.data.content ?? []).map((document: ExtractedDocument | string, index: number) =>
      typeof document === 'string' ? { name: `${t('workflow.document.label')} ${index + 1}`, content: document } : document,
    ),
)
const selectedDocumentIndex = ref(0)
const selectedDocument = computed(() => documents.value[selectedDocumentIndex.value] ?? documents.value[0])
// 仅在执行数据变化时重置选择，翻译变化保留当前文档。
watch(
  () => props.data.document_list ?? (props.data.content ?? []).slice(),
  () => {
    selectedDocumentIndex.value = 0
  },
)
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">
        <span>{{ t('workflow.executionResult.outputParams') }}</span>
        <span class="text-N600 font-normal">（{{ t('workflow.document.characterPreviewHint', { count: 500 }) }}）</span>
      </h6>

      <MkHorizontalScroll v-if="documents.length" class="mb-2">
        <template v-for="(file, index) in documents" :key="index">
          <!-- 选择要查看的文档 -->
          <el-card
            shadow="hover"
            class="small w-45 shrink-0 cursor-pointer"
            :class="{ 'border-primary! bg-primary/10!': selectedDocumentIndex === index }"
            @click="selectedDocumentIndex = index"
          >
            <div class="flex-align-center gap-2">
              <img :src="getFileIconUrl(file.name || '', file.meta?.source_type === 'web' ? KNOWLEDGE_TYPE.WEB : undefined)" alt="" width="24" />
              <span class="min-w-0 truncate" :title="file.name">{{ file.name || '-' }}</span>
            </div>
          </el-card>
        </template>
      </MkHorizontalScroll>

      <el-card v-if="selectedDocument" shadow="never">
        <el-scrollbar max-height="400" class="-mr-4" view-class="pr-4">
          <MdPreview v-if="selectedDocument.content" :model-value="selectedDocument.content.slice(0, 500)" no-img-zoom-in />
          <template v-else>-</template>
        </el-scrollbar>
        <div class="text-N600 mt-2">
          {{ Math.min(selectedDocument.content?.length ?? 0, 500) }}
          {{ t('knowledge.stats.characters', Math.min(selectedDocument.content?.length ?? 0, 500)) }}
        </div>
      </el-card>
      <template v-else>-</template>
    </div>
  </DetailContainer>
</template>
