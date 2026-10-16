<script setup lang="ts">
import { reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance } from 'element-plus'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import { KNOWLEDGE_SEARCH_MODE, KNOWLEDGE_TYPE } from '@/api/enums'
import { KNOWLEDGE_SEARCH_MODE_OPTIONS } from '@/constants/knowledge'
import type { KnowledgeHitTestPayload, KnowledgeHitTestResult } from '@/api/types'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import emptyHitTestImage from '@/assets/empty/hit-test.png'
import HitTestInput from './components/HitTestInput.vue'

defineOptions({ name: 'HitTestView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ hideHeader: true })

const { knowledge, knowledgeId, resourceApi } = useKnowledgeDetailContext({ resourceScopes: ['workspace', 'system-resource', 'system-shared'] })

// 检索参数与待测试内容，仅通用知识库支持查询图片。
const searchForm = reactive<Pick<KnowledgeHitTestPayload, 'search_mode' | 'similarity' | 'top_number'>>({
  search_mode: KNOWLEDGE_SEARCH_MODE.EMBEDDING,
  similarity: 0.6,
  top_number: 5,
})
const searchFormRef = useTemplateRef<FormInstance>('searchFormRef')

const loading = ref(false)

function changeSearchMode() {
  searchForm.similarity = searchForm.search_mode === KNOWLEDGE_SEARCH_MODE.KEYWORDS ? 0 : 0.6
}

// 仅展示本次提交的查询快照，失败保留输入和检索参数供重试。
const resultParagraphs = ref<KnowledgeHitTestResult[]>([])
const hasTestResult = ref(false)
const submittedQuery = ref<Required<Pick<KnowledgeHitTestPayload, 'query_text' | 'image_list'>>>({ query_text: '', image_list: [] })

function testKnowledge(query: Required<Pick<KnowledgeHitTestPayload, 'query_text' | 'image_list'>>) {
  if (loading.value) return
  searchFormRef.value?.validate((valid) => {
    if (!valid || loading.value) return
    const payload: KnowledgeHitTestPayload = {
      ...searchForm,
      ...query,
    }

    loading.value = true
    return resourceApi.knowledge
      .postKnowledgeHitTest(knowledgeId.value, payload)
      .then((paragraphs) => {
        resultParagraphs.value = paragraphs
        submittedQuery.value = query
        hasTestResult.value = true
      })
      .catch(() => {
        // 请求层统一提示错误，保留输入与已有结果供重试。
      })
      .finally(() => {
        loading.value = false
      })
  })
}
</script>

<template>
  <div class="-ml-6 -mr-6 -mb-6 grid h-layout-content shrink-0 grid-cols-2 overflow-hidden">
    <!-- 左侧 -->
    <el-scrollbar class="min-h-0 min-w-0" view-class="px-6 pb-6">
      <header class="flex-align-center gap-2 py-4">
        <h4>{{ title }}</h4>
        <MkTooltip content="针对用户提问召回匹配的知识内容，保障回答效果" placement="right">
          <MkIcon name="icon_info_outlined" class="text-N600!" />
        </MkTooltip>
      </header>
      <el-card shadow="never" class="has-bottom-arrow mb-5">
        <h4 class="mb-4">检索参数</h4>
        <el-form ref="searchFormRef" :model="searchForm" label-position="top" require-asterisk-position="right" @submit.prevent>
          <el-form-item label="检索模式">
            <!-- 选择检索模式 -->
            <el-radio-group v-model="searchForm.search_mode" @change="changeSearchMode" class="space-y-2">
              <template v-for="searchMode in KNOWLEDGE_SEARCH_MODE_OPTIONS" :key="searchMode.value">
                <el-card shadow="never" class="w-full!" :class="{ 'border-primary!': searchForm.search_mode === searchMode.value }">
                  <el-radio :value="searchMode.value" :disabled="loading" class="mk-card-radio">
                    <h6>{{ searchMode.label }}</h6>
                    <span class="block text-sm text-N600">{{ searchMode.description }}</span>
                  </el-radio>
                </el-card>
              </template>
            </el-radio-group>
          </el-form-item>
          <div class="grid grid-cols-2 gap-4">
            <el-form-item class="mb-0!">
              <template #label>
                <span class="flex-align-center gap-1">
                  相似度高于
                  <MkTooltip content="相似度越高相关性越强。" placement="right"><MkIcon name="icon_info_outlined" class="text-N600!" /></MkTooltip>
                </span>
              </template>
              <!-- 设置相似度阈值 -->
              <el-input-number
                v-model="searchForm.similarity"
                class="w-full!"
                :min="0"
                :max="searchForm.search_mode === KNOWLEDGE_SEARCH_MODE.BLEND ? 2 : 1"
                :precision="3"
                :step="0.1"
                :value-on-clear="0"
                controls-position="right"
                align="left"
              />
            </el-form-item>
            <el-form-item label="召回分段数 TOP" class="mb-0!">
              <!-- 设置召回数量 -->
              <el-input-number
                v-model="searchForm.top_number"
                class="w-full!"
                :min="1"
                :max="10000"
                :value-on-clear="1"
                controls-position="right"
                align="left"
              />
            </el-form-item>
          </div>
        </el-form>
      </el-card>

      <HitTestInput
        :file-count-limit="knowledge?.file_count_limit"
        :file-size-limit="knowledge?.file_size_limit"
        :loading="loading"
        :allow-images="knowledge?.type === KNOWLEDGE_TYPE.BASE"
        @submit="testKnowledge"
      />
    </el-scrollbar>
    <!-- 右侧 -->
    <section v-loading="loading" class="min-h-0 min-w-0 border-l">
      <el-scrollbar height="100%" view-class="flex-column min-h-full p-4">
        <div v-if="!hasTestResult" class="flex-center flex-1">
          <MkEmpty :image="emptyHitTestImage" description="召回的知识显示在这里" :image-size="125" />
        </div>
        <template v-else>
          <section class="mb-6">
            <h4 class="mb-4">本次查询</h4>
            <div v-if="submittedQuery.image_list.length" class="flex flex-wrap gap-2">
              <template v-for="image in submittedQuery.image_list" :key="image.file_id">
                <!-- 预览本次查询图片 -->
                <el-image :src="image.url" :alt="image.name" fit="cover" class="size-12" />
              </template>
            </div>
            <p v-if="submittedQuery.query_text" class="mt-3 whitespace-pre-wrap break-words">{{ submittedQuery.query_text }}</p>
          </section>
          <h4 class="mb-4">查询结果</h4>
          <div v-if="!resultParagraphs.length" class="flex-center flex-1">
            <MkEmpty type="search" description="未召回相关知识，请调整检索参数内容" />
          </div>
          <div v-else class="space-y-3">
            <template v-for="(paragraph, paragraphIndex) in resultParagraphs" :key="paragraph.id">
              <MkSourceCard :title="paragraph.title || '-'">
                <template #icon>
                  <span>
                    <span>{{ `#${paragraphIndex + 1}` }}</span>
                    <el-divider direction="vertical" />
                  </span>
                </template>
                <template #tag>
                  <span class="shrink-0 text-primary">{{ paragraph.similarity.toFixed(3) }}</span>
                </template>

                <el-scrollbar max-height="280">
                  <MdPreview :model-value="paragraph.content" />
                </el-scrollbar>
                <template #footer>
                  <div class="text-sm text-N600">
                    <span class="truncate" :title="paragraph.document_name">{{ paragraph.document_name }}</span>
                  </div>
                </template>
              </MkSourceCard>
            </template>
          </div>
        </template>
      </el-scrollbar>
    </section>
  </div>
</template>
