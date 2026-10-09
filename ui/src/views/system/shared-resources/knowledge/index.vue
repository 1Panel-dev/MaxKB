<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import type { ParamsPage } from '@/api/admin/core/types'
import SystemSharedKnowledgeApi from '@/api/admin/system/shared-resources/knowledge/knowledge'
import SystemSharedRelatedResourcesApi from '@/api/admin/system/shared-resources/related-resources'
import SystemCommonApi from '@/api/admin/system/common'
import type { Dict, KnowledgeItem, OptionItem } from '@/api/types'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import KnowledgeCard from '@/views/knowledge/knowledge-card/KnowledgeCard.vue'
import ButtonCreateKnowledge from '@/views/knowledge/components/ButtonCreateKnowledge.vue'
import ButtonTemplateStore from '@/views/knowledge/components/ButtonTemplateStore.vue'
import {
  DeleteKnowledgeAction,
  EmbeddingKnowledgeAction,
  ExportKnowledgeAction,
  GenerateQuestionsAction,
  KeywordIndexKnowledgeAction,
  McpConfigKnowledgeAction,
  RelatedResourcesKnowledgeAction,
  SyncKnowledgeAction,
} from '@/views/knowledge/knowledge-card/action-dropdown'

/* 共享知识库详情入口 */
function handleOpenKnowledge(knowledge: KnowledgeItem) {
  // TODO: 补齐系统共享知识库详情路由后，使用当前知识库的 id、type 调用 router.push。
  void knowledge
}

/* 共享知识库查询 */
const knowledgeData = ref<KnowledgeItem[]>([])
const knowledgeQuery = ref<Dict<unknown>>()
const knowledgeOperationLoading = ref(false)
const creatorOptions = ref<OptionItem<string>[]>([])
const infiniteScrollRef = useTemplateRef<{ reset: () => Promise<void> }>('infiniteScrollRef')
const searchFields = computed(() => [
  { label: '名称', value: 'name' },
  { label: '创建者', value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])

function loadCreatorOptions(keyword: string) {
  return SystemCommonApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ label: nick_name, value: id }))
  })
}

function loadKnowledgePage(pagination: ParamsPage) {
  return SystemSharedKnowledgeApi.getKnowledgePage(pagination, knowledgeQuery.value)
}

function refreshKnowledge() {
  return infiniteScrollRef.value?.reset()
}

function handleSearchChange(query?: Dict<unknown>) {
  knowledgeQuery.value = query
  return refreshKnowledge()
}
</script>

<template>
  <MkViewLayout class="shared-knowledge-view">
    <template #default="{ Header }">
      <component :is="Header">
        <h4>知识库</h4>
        <div class="flex-align-center gap-3">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <!-- 模板中心 -->
          <ButtonTemplateStore folder-id="default" :api="SystemSharedKnowledgeApi" @refresh="refreshKnowledge" />
          <!-- 创建共享知识库 -->
          <ButtonCreateKnowledge folder-id="default" :api="SystemSharedKnowledgeApi" @refresh="refreshKnowledge" />
        </div>
      </component>

      <div v-loading="knowledgeOperationLoading" class="min-h-0 flex-1">
        <MkInfiniteScroll ref="infiniteScrollRef" v-model="knowledgeData" :load="loadKnowledgePage">
          <div class="mk-resource-card-grid">
            <template v-for="knowledge in knowledgeData" :key="knowledge.id">
              <KnowledgeCard :knowledge="knowledge" shared @click="handleOpenKnowledge(knowledge)">
                <template #action-dropdown>
                  <!-- 同步 Web 知识库 -->
                  <SyncKnowledgeAction
                    v-if="knowledge.type !== KNOWLEDGE_TYPE.BASE"
                    v-model:loading="knowledgeOperationLoading"
                    label="同步"
                    :api="SystemSharedKnowledgeApi"
                    :knowledge="knowledge"
                  />
                  <!-- 向量化 -->
                  <EmbeddingKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    label="向量化"
                    :api="SystemSharedKnowledgeApi"
                    :knowledge="knowledge"
                  />
                  <!-- 生成问题 -->
                  <GenerateQuestionsAction
                    v-model:loading="knowledgeOperationLoading"
                    label="生成问题"
                    :api="SystemSharedKnowledgeApi"
                    :knowledge="knowledge"
                  />
                  <!-- 分词索引 -->
                  <KeywordIndexKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    label="分词索引"
                    :api="SystemSharedKnowledgeApi"
                    :knowledge="knowledge"
                  />
                  <!-- MCP 配置详情 -->
                  <McpConfigKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    label="MCP 配置详情"
                    :api="SystemSharedKnowledgeApi"
                    :knowledge="knowledge"
                  />
                  <!-- 查看关联资源 -->
                  <RelatedResourcesKnowledgeAction label="查看关联资源" :api="SystemSharedRelatedResourcesApi" :knowledge="knowledge" />
                  <!-- TODO 授权工作空间 -->
                  <!-- 导出共享知识库 -->
                  <ExportKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    label="导出"
                    :api="SystemSharedKnowledgeApi"
                    :knowledge="knowledge"
                  />
                  <!-- 删除共享知识库 -->
                  <DeleteKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    label="删除"
                    :api="SystemSharedKnowledgeApi"
                    :knowledge="knowledge"
                    @delete="refreshKnowledge"
                  />
                </template>
              </KnowledgeCard>
            </template>
          </div>
          <template #empty><MkEmpty class="mt-24" /></template>
        </MkInfiniteScroll>
      </div>
    </template>
  </MkViewLayout>
</template>
