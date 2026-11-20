<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import { DOCUMENT_SPLIT_STRATEGY_LABELS } from '../constant'
import { getFileIconUrl } from '@/utils/icon'

defineOptions({ name: 'DocumentSplitNodeDetail' })
const { t } = useI18n({ useScope: 'global' })

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
      <h6 class="mb-2">{{ t('workflow.executionResult.inputParams') }}</h6>
      <div class="space-y-2">
        <div>
          <span class="text-N600">{{ t('workflow.documentSplit.strategy.label') }}：</span>
          {{ DOCUMENT_SPLIT_STRATEGY_LABELS[data.split_strategy] ?? (data.split_strategy || '-') }}
        </div>
        <div>
          <span class="text-N600">{{ t('workflow.documentSplit.childChunkLength.label') }}：</span>
          {{ data.chunk_size ?? '-' }}
        </div>
        <div v-if="data.split_strategy === 'custom'">
          <span class="text-N600">{{ t('knowledge.documentStrategy.delimiter.label') }}：</span>
          {{ data.patterns ?? '-' }}
        </div>
        <div v-if="data.split_strategy === 'custom'">
          <span class="text-N600">{{ t('knowledge.documentStrategy.paragraphLength') }}：</span>
          {{ data.limit ?? '-' }}
        </div>
        <div class="truncate" :title="inputNames">
          <span class="text-N600">{{ t('workflow.inputContent.label') }}：</span>
          {{ inputNames || '-' }}
        </div>
      </div>
    </div>

    <!-- 输出参数 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">
        {{ t('workflow.executionResult.outputParams') }}
        <span class="text-N600 font-normal">（{{ t('workflow.document.paragraphPreviewHint', { count: 5 }) }}）</span>
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
              <img :src="getFileIconUrl(file.name || '', file.meta?.source_type === 'web' ? KNOWLEDGE_TYPE.WEB : undefined)" alt="" width="24" />
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
              <div class="text-N600 mt-2">
                {{ (paragraph.content || '').length }} {{ t('knowledge.stats.characters', (paragraph.content || '').length) }}
              </div>
            </el-card>
          </template>
        </template>
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
