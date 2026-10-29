<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import { getFileIconUrl } from '@/utils/icon'
import { DOCUMENT_SPLIT_STRATEGY_LABELS } from '../constant'

defineOptions({ name: 'DocumentSplitNodeDetail' })

const props = defineProps<{
  data: ExecutionNodeDetail
}>()

interface SplitParagraph {
  title?: string
  content?: string
}

interface SplitDocument {
  name?: string
  paragraphs?: SplitParagraph[]
  meta?: {
    source_type?: string
  }
}

const paragraphList = computed<SplitDocument[]>(
  () => (props.data?.paragraph_list as SplitDocument[] | undefined) || (props.data?.document_list as SplitDocument[] | undefined) || [],
)

// 输入内容取输入文档名；无 document_list 时回退用分段结果里的文档名
const inputNames = computed(() =>
  ((props.data?.document_list as SplitDocument[] | undefined) || paragraphList.value)
    .map((doc) => doc.name)
    .filter(Boolean)
    .join('、'),
)

// 文档切换后展示对应分段，详情数据更新时默认选中首个文档。
const selectedDocumentIndex = ref(0)
const selectedParagraphs = computed(() => (paragraphList.value[selectedDocumentIndex.value]?.paragraphs ?? []).slice(0, 5))
watch(paragraphList, () => {
  selectedDocumentIndex.value = 0
})
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <!-- 输入参数 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">输入参数</h6>
      <div class="space-y-2">
        <div>
          <span class="text-N600">分段策略：</span>
          {{ DOCUMENT_SPLIT_STRATEGY_LABELS[data.split_strategy] ?? (data.split_strategy || '-') }}
        </div>
        <div>
          <span class="text-N600">子分块长度：</span>
          {{ data.chunk_size ?? '-' }}
        </div>
        <div v-if="data.split_strategy === 'custom'">
          <span class="text-N600">分段标识：</span>
          {{ data.patterns ?? '-' }}
        </div>
        <div v-if="data.split_strategy === 'custom'">
          <span class="text-N600">分段长度：</span>
          {{ data.limit ?? '-' }}
        </div>
        <div class="truncate" :title="inputNames">
          <span class="text-N600">输入内容：</span>
          {{ inputNames || '-' }}
        </div>
      </div>
    </div>

    <!-- 输出参数 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">
        输出参数
        <span class="text-N600 font-normal">（每个文档仅展示前 5 个分段）</span>
      </h6>
      <MkHorizontalScroll v-if="paragraphList.length" class="mb-2">
        <template v-for="(file, index) in paragraphList" :key="index">
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
