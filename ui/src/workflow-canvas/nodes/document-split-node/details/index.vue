<script setup lang="ts">
import { computed, ref } from 'vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

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
}

const documentList = computed<SplitDocument[]>(() => (props.data?.paragraph_list as SplitDocument[] | undefined) || [])

// 输入内容取输入文档名；无 document_list 时回退用分段结果里的文档名
const inputNames = computed(() =>
  ((props.data?.document_list as SplitDocument[] | undefined) || documentList.value)
    .map((doc) => doc.name)
    .filter(Boolean)
    .join('、'),
)

const activeTab = ref(0)
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <!-- 输入参数 -->
    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">输入参数</h6>
      <div class="flex flex-col gap-2">
        <div><span class="text-N600">分段规则：</span>{{ data.split_strategy || '-' }}</div>
        <div><span class="text-N600">分段长度：</span>{{ data.chunk_size ?? '-' }}</div>
        <div class="truncate" :title="inputNames"><span class="text-N600">输入内容：</span>{{ inputNames || '-' }}</div>
      </div>
    </div>

    <!-- 输出参数 -->
    <div class="mk-gray-card py-2! rounded-xl!">
      <h6 class="mb-2">输出参数 <span class="text-N600 font-normal">（每个文档仅展示前 5 个分段）</span></h6>
      <div class="space-y-2">
        <el-tabs v-if="documentList.length > 0" v-model="activeTab" class="paragraph-tabs">
          <el-tab-pane v-for="(doc, docIndex) in documentList" :key="docIndex" :label="doc.name" :name="docIndex">
            <template v-if="(doc.paragraphs || []).length > 0">
              <template v-for="(paragraph, paragraphIndex) in doc.paragraphs" :key="paragraphIndex">
                <el-card shadow="never">
                  <div class="truncate" :title="paragraph.title">#{{ paragraphIndex + 1 }} {{ paragraph.title || '-' }}</div>
                  <el-scrollbar max-height="150" class="mt-1">
                    <MdPreview :model-value="paragraph.content" no-img-zoom-in />
                  </el-scrollbar>
                  <div class="mt-1 border-t border-dashed pt-1 text-N600">字符：{{ (paragraph.content || '').length }}</div>
                </el-card>
              </template>
            </template>
            <div v-else class="text-N600">-</div>
          </el-tab-pane>
        </el-tabs>
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
