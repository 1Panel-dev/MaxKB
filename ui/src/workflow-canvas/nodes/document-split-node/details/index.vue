<script setup lang="ts">
import { computed, ref } from 'vue'
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

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

const documentList = computed<SplitDocument[]>(
  () => (props.data?.paragraph_list as SplitDocument[] | undefined) || [],
)

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
    <template #header="{ show }">
      <BaseHeader :data="data" :show="show" />
    </template>

    <!-- 输入参数 -->
    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">输入参数</h5>
      <div class="flex flex-col gap-2 border-t border-dashed px-3 py-2 text-N900">
        <div><span class="text-N600">分段规则：</span>{{ data.split_strategy || '-' }}</div>
        <div><span class="text-N600">分段长度：</span>{{ data.chunk_size ?? '-' }}</div>
        <div class="truncate" :title="inputNames">
          <span class="text-N600">输入内容：</span>{{ inputNames || '-' }}
        </div>
      </div>
    </div>

    <!-- 输出参数 -->
    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">输出参数（每个文档仅展示前 5 个分段）</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <el-tabs v-if="documentList.length > 0" v-model="activeTab" class="paragraph-tabs">
          <el-tab-pane
            v-for="(doc, docIndex) in documentList"
            :key="docIndex"
            :label="doc.name"
            :name="docIndex"
          >
            <template v-if="(doc.paragraphs || []).length > 0">
              <div
                v-for="(paragraph, paragraphIndex) in doc.paragraphs"
                :key="paragraphIndex"
                class="mb-2 overflow-hidden rounded-md bg-white p-2 last:mb-0"
              >
                <div class="truncate" :title="paragraph.title">
                  {{ paragraphIndex + 1 }}.{{ paragraph.title || '-' }}
                </div>
                <el-scrollbar height="150" class="mt-1">
                  <MdPreview :model-value="paragraph.content" class="paragraph-answer" no-img-zoom-in />
                </el-scrollbar>
                <div class="mt-1 border-t border-dashed pt-1 text-N600">
                  字符：{{ (paragraph.content || '').length }}
                </div>
              </div>
            </template>
            <div v-else class="text-N600">-</div>
          </el-tab-pane>
        </el-tabs>
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>

<style scoped lang="scss">
:deep(.paragraph-answer.md-editor) {
  background: transparent;
  height: auto;
}
</style>
