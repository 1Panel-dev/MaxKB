<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import { KNOWLEDGE_SEARCH_MODE } from '@/api/enums'
import { KNOWLEDGE_SEARCH_MODE_OPTIONS } from '@/constants/knowledge'
import type { KnowledgeHitTestImage, KnowledgeHitTestPayload, KnowledgeHitTestResult } from '@/api/types'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import emptyHitTestImage from '@/assets/empty/hit-test.png'
import HitTestInput from './components/HitTestInput.vue'
import HitTestResult from './components/HitTestResult.vue'

defineOptions({ name: 'HitTestView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ customHeader: true })

const { knowledgeId, resourceApi } = useKnowledgeDetailContext({ resourceScopes: ['workspace', 'system-resource', 'system-shared'] })

// 检索参数与待测试内容，图片查询仅支持向量和混合检索。
const searchForm = reactive<Pick<KnowledgeHitTestPayload, 'search_mode' | 'similarity' | 'top_number'>>({
  search_mode: KNOWLEDGE_SEARCH_MODE.EMBEDDING,
  similarity: 0.6,
  top_number: 6,
})
const searchFormRef = useTemplateRef<FormInstance>('searchFormRef')
const searchRules: FormRules = {
  similarity: [{ required: true, type: 'number', message: '请输入相似度', trigger: 'change' }],
  top_number: [{ required: true, type: 'number', message: '请输入召回数量', trigger: 'change' }],
}
const queryText = ref('')
const queryImages = ref<KnowledgeHitTestImage[]>([])
const uploading = ref(false)
const hasFailedImages = ref(false)
const loading = ref(false)
const hasImages = computed(() => queryImages.value.length > 0)
const isKeywordSearch = computed(() => searchForm.search_mode === KNOWLEDGE_SEARCH_MODE.KEYWORDS)
const canTest = computed(() => !loading.value && !uploading.value && !hasFailedImages.value && (!!queryText.value.trim() || hasImages.value))

function changeSearchMode() {
  searchForm.similarity = isKeywordSearch.value ? 0 : 0.6
}

// 仅展示本次提交的查询快照，失败保留输入和检索参数供重试。
const resultParagraphs = ref<KnowledgeHitTestResult[]>([])
const tested = ref(false)
const testFailed = ref(false)
const submittedQuery = ref('')

function testKnowledge() {
  if (!canTest.value) return
  searchFormRef.value?.validate((valid) => {
    if (!valid || !canTest.value) return
    const payload: KnowledgeHitTestPayload = {
      ...searchForm,
      query_text: queryText.value.trim(),
      image_list: queryImages.value.map((queryImage) => ({ ...queryImage })),
    }
    const queryTitle = payload.query_text || `图片检索（${queryImages.value.length} 张）`
    loading.value = true
    testFailed.value = false
    return resourceApi.knowledge
      .postKnowledgeHitTest(knowledgeId.value, payload)
      .then((paragraphs) => {
        resultParagraphs.value = paragraphs
        submittedQuery.value = queryTitle
        tested.value = true
      })
      .catch(() => {
        // 通用错误由请求层提示；结果区标记失败，避免误认为是本次测试结果。
        testFailed.value = true
      })
      .finally(() => {
        loading.value = false
      })
  })
}
</script>

<template>
  <Teleport v-if="headerTarget" :to="headerTarget">
    <div class="flex-align-center gap-2">
      <h4>{{ title }}</h4>
      <MkTooltip content="针对用户提问召回匹配的知识内容，保障回答效果" placement="right">
        <MkIcon name="icon_info_outlined" class="text-N600!" />
      </MkTooltip>
    </div>
  </Teleport>
  <div class="grid min-h-0 flex-1 grid-cols-2 gap-6 -pr-0!">
    <section class="min-w-0 space-y-4">
      <div
        class="relative rounded-xl border bg-white p-4 after:absolute after:-bottom-1.5 after:left-1/2 after:size-3 after:rotate-45 after:border-r after:border-b after:bg-white"
      >
        <h4 class="mb-5">检索参数</h4>
        <el-form
          ref="searchFormRef"
          :model="searchForm"
          :rules="searchRules"
          label-position="top"
          hide-required-asterisk
          :disabled="loading"
          @submit.prevent
        >
          <el-form-item label="检索模式" class="mb-4!">
            <!-- 选择检索模式 -->
            <el-radio-group v-model="searchForm.search_mode" class="mk-radio-group-vertical" @change="changeSearchMode">
              <template v-for="searchMode in KNOWLEDGE_SEARCH_MODE_OPTIONS" :key="searchMode.value">
                <el-card
                  shadow="never"
                  class="w-full rounded-xl!"
                  body-class="p-4!"
                  :class="{ 'border-primary!': searchForm.search_mode === searchMode.value }"
                >
                  <el-radio
                    :value="searchMode.value"
                    :disabled="loading || (searchMode.value === KNOWLEDGE_SEARCH_MODE.KEYWORDS && (hasImages || uploading))"
                    class="mk-card-radio items-center! [&_.el-radio__input]:mt-0!"
                  >
                    <h6>{{ searchMode.label }}</h6>
                    <span class="mt-1 block text-sm text-N600">{{ searchMode.description }}</span>
                    <span v-if="searchMode.value === KNOWLEDGE_SEARCH_MODE.KEYWORDS && hasImages" class="mt-1 block text-sm text-N500">
                      图片不支持全文检索，请先移除图片
                    </span>
                  </el-radio>
                </el-card>
              </template>
            </el-radio-group>
          </el-form-item>
          <div class="grid grid-cols-2 gap-4">
            <el-form-item prop="similarity" class="mb-0!">
              <template #label>
                <span class="flex-align-center gap-1">
                  相似度高于
                  <MkTooltip content="仅召回得分高于此值的分段。向量和全文检索范围为 0–1，混合检索范围为 0–2。">
                    <MkIcon name="icon_info_outlined" :size="16" class="text-N500" />
                  </MkTooltip>
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
            <el-form-item label="召回 TOP K" prop="top_number" class="mb-0!">
              <!-- 设置召回数量 -->
              <el-input-number
                v-model="searchForm.top_number"
                class="w-full!"
                :min="1"
                :max="10000"
                :precision="0"
                :value-on-clear="1"
                controls-position="right"
                align="left"
              />
            </el-form-item>
          </div>
        </el-form>
      </div>

      <HitTestInput
        v-model="queryText"
        :disabled="loading"
        :allow-images="!isKeywordSearch"
        @update:images="queryImages = $event"
        @update:uploading="uploading = $event"
        @update:failed="hasFailedImages = $event"
      />
      <!-- 执行召回测试 -->
      <el-button type="primary" class="w-full" :loading="loading" :disabled="!canTest" @click="testKnowledge">
        <MkIcon v-if="!loading" name="icon_play_outlined" class="mr-1" />
        测试
      </el-button>
    </section>

    <section v-loading="loading" class="flex-column min-h-[520px] min-w-0 rounded-xl border bg-N100 p-4">
      <div v-if="!tested" class="flex-center flex-1">
        <MkEmpty :image="emptyHitTestImage" description="召回的知识显示在这里" :image-size="125" />
      </div>
      <template v-else>
        <header class="mb-4 space-y-2">
          <div class="flex-between gap-3">
            <h4>召回结果</h4>
            <span class="shrink-0 text-sm text-N500">共 {{ resultParagraphs.length }} 条</span>
          </div>
          <p class="break-words text-N600">{{ submittedQuery }}</p>
        </header>
        <div v-if="!resultParagraphs.length" class="flex-center flex-1">
          <MkEmpty type="search" description="未召回相关知识，请调整检索参数或测试内容" />
        </div>
        <div v-else class="space-y-3">
          <template v-for="(paragraph, paragraphIndex) in resultParagraphs" :key="paragraph.id">
            <HitTestResult :paragraph="paragraph" :index="paragraphIndex + 1" />
          </template>
        </div>
      </template>
    </section>
  </div>
</template>
