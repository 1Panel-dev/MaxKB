<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import { getFileIconUrl } from '@/utils/icon'

defineOptions({ name: 'KnowledgeWriteNodeDetail' })

const props = defineProps<{
  data: ExecutionNodeDetail
}>()

interface WriteParagraph {
  title?: string
  content?: string
}

interface WriteDocument {
  name?: string
  paragraphs?: WriteParagraph[]
  meta?: {
    source_type?: string
  }
}

const writeContent = computed<WriteDocument[]>(() => (props.data?.write_content as WriteDocument[] | undefined) || [])

// 文档切换后展示对应分段，详情更新时默认选中首个文档。
const selectedDocumentIndex = ref(0)
const selectedParagraphs = computed(() => (writeContent.value[selectedDocumentIndex.value]?.paragraphs ?? []).slice(0, 5))
watch(writeContent, () => {
  selectedDocumentIndex.value = 0
})
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">写入内容（每个文档仅展示前 5 个分段）</h6>
      <MkHorizontalScroll v-if="writeContent.length" class="mb-2">
        <template v-for="(file, index) in writeContent" :key="index">
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
      <div class="space-y-2">
        <template v-if="selectedParagraphs.length > 0">
          <template v-for="(paragraph, paragraphIndex) in selectedParagraphs" :key="paragraphIndex">
            <el-card shadow="never">
              <h4 class="truncate mb-2" :title="paragraph.title">{{ paragraph.title || '-' }}</h4>
              <el-scrollbar max-height="400" class="-mr-4" view-class="pr-4">
                <MdPreview :model-value="paragraph.content" no-img-zoom-in />
              </el-scrollbar>
              <div class="text-N600 mt-2">{{ (paragraph.content || '').length }} 字符</div>
            </el-card>
          </template>
        </template>
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
