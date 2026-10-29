<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import { getFileIconUrl } from '@/utils/icon'

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
      typeof document === 'string' ? { name: `文档 ${index + 1}`, content: document } : document,
    ),
)
const selectedDocumentIndex = ref(0)
const selectedDocument = computed(() => documents.value[selectedDocumentIndex.value] ?? documents.value[0])
watch(documents, () => {
  selectedDocumentIndex.value = 0
})
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">
        <span>输出参数</span>
        <span class="text-N600 font-normal">（每个文档仅支持预览 500 字）</span>
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
              <img v-if="file.meta?.source_type === 'web'" src="@/assets/file-type/web-link-icon.svg" alt="" width="24" />
              <img v-else :src="getFileIconUrl(file.name || '')" alt="" width="24" />
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
        <div class="text-N600 mt-2">{{ Math.min(selectedDocument.content?.length ?? 0, 500) }} 字符</div>
      </el-card>
      <template v-else>-</template>
    </div>
  </DetailContainer>
</template>
