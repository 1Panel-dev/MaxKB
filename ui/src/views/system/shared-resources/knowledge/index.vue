<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { ParamsPage } from '@/api/admin/core/types'
import type { Dict, KnowledgeItem, OptionItem } from '@/api/types'
import { KNOWLEDGE_TYPE, RESOURCE_TYPE } from '@/api/enums'
import SystemCommonApi from '@/api/admin/system/common'
import SystemSharedKnowledgeApi from '@/api/admin/system/shared-resources/knowledge/knowledge'
import SystemSharedRelatedResourcesApi from '@/api/admin/system/shared-resources/related-resources'
import ButtonCreateKnowledge from '@/views/knowledge/components/ButtonCreateKnowledge.vue'
import ButtonTemplateStore from '@/views/knowledge/components/ButtonTemplateStore.vue'
import KnowledgeCard from '@/views/knowledge/knowledge-card/KnowledgeCard.vue'
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
import AuthorizedWorkspaceAction from '../authorized-workspace-action/index.vue'
import { KNOWLEDGE_TYPE_MAP } from '@/constants/knowledge'
import perm from '@/permission/index.ts'

const { t } = useI18n({ useScope: 'global' })

/* 共享知识库详情入口 */
const router = useRouter()
function handleOpenKnowledge(knowledge: KnowledgeItem) {
  void router.push({
    name: 'system-shared-knowledge-detail',
    params: { knowledgeId: knowledge.id, type: KNOWLEDGE_TYPE_MAP[knowledge.type] },
  })
}

function handleOpenKnowledgeSetting(knowledge: KnowledgeItem) {
  void router.push({
    name: knowledge.type === KNOWLEDGE_TYPE.BASE ? 'system-shared-knowledge-setting' : 'system-shared-knowledge-base-setting',
    params: { knowledgeId: knowledge.id, type: KNOWLEDGE_TYPE_MAP[knowledge.type] },
  })
}

/* 共享知识库查询 */
const knowledgeData = ref<KnowledgeItem[]>([])
const knowledgeQuery = ref<Dict<unknown>>()
const knowledgeOperationLoading = ref(false)
const creatorOptions = ref<OptionItem<string>[]>([])
const infiniteScrollRef = useTemplateRef<{ reset: () => Promise<void> }>('infiniteScrollRef')
const searchFields = computed(() => [
  { label: t('common.name.label'), value: 'name' },
  {
    label: t('common.labels.type'),
    value: 'type',
    options: [
      { value: KNOWLEDGE_TYPE.BASE, label: t('knowledge.base.label') },
      { value: KNOWLEDGE_TYPE.WEB, label: t('knowledge.web.label') },
      { value: KNOWLEDGE_TYPE.LARK, label: t('knowledge.lark.label') },
      { value: KNOWLEDGE_TYPE.WORKFLOW, label: t('knowledge.workflow.label') },
    ],
  },
  { label: t('common.labels.creator'), value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
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
  <MkViewLayout :title="t('knowledge.title')" class="shared-knowledge-view">
    <template #default="{ Header, title }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <div class="flex-align-center gap-3">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <!-- 模板中心 -->
          <ButtonTemplateStore folder-id="default" :api="SystemSharedKnowledgeApi" @refresh="refreshKnowledge" />
          <!-- 创建共享知识库 -->
          <ButtonCreateKnowledge
            v-if="perm.knowledge.share.create()"
            folder-id="default"
            :api="SystemSharedKnowledgeApi"
            @refresh="refreshKnowledge"
          />
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
                    v-if="knowledge.type !== KNOWLEDGE_TYPE.BASE && perm.knowledge.share.sync()"
                    v-model:loading="knowledgeOperationLoading"
                    :label="t('knowledge.sync.label')"
                    :api="SystemSharedKnowledgeApi"
                    :knowledge="knowledge"
                  />
                  <!-- 向量化 -->
                  <EmbeddingKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    :label="t('knowledge.actions.generateEmbeddings')"
                    :api="SystemSharedKnowledgeApi"
                    :knowledge="knowledge"
                    v-if="perm.knowledge.share.vector()"
                  />
                  <!-- 生成问题 -->
                  <GenerateQuestionsAction
                    v-model:loading="knowledgeOperationLoading"
                    :label="t('knowledge.generateQuestions.title')"
                    :api="SystemSharedKnowledgeApi"
                    :knowledge="knowledge"
                    v-if="perm.knowledge.share.generate()"
                  />
                  <!-- 设置 -->
                  <MkDropdownItem v-if="perm.knowledge.share.settingRead()" @click.stop="handleOpenKnowledgeSetting(knowledge)">
                    <template #icon><MkIcon name="icon_setting" /></template>
                    {{ t('common.labels.settings') }}
                  </MkDropdownItem>
                  <!-- 分词索引 -->
                  <KeywordIndexKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    :label="t('knowledge.actions.buildKeywordIndex')"
                    :api="SystemSharedKnowledgeApi"
                    :knowledge="knowledge"
                    v-if="perm.knowledge.share.token()"
                  />
                  <!-- MCP 服务配置 -->
                  <McpConfigKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    :label="t('resource.mcpConfig.title')"
                    :api="SystemSharedKnowledgeApi"
                    :knowledge="knowledge"
                    v-if="perm.knowledge.share.mcpConfig()"
                  />

                  <!-- 授权工作空间 -->
                  <AuthorizedWorkspaceAction
                    v-if="perm.knowledge.share.authToWorkspace()"
                    :label="t('resource.workspaceAuthorization.title')"
                    :resource="knowledge"
                    :resource-type="RESOURCE_TYPE.KNOWLEDGE"
                  />

                  <!-- 查看关联资源 -->
                  <RelatedResourcesKnowledgeAction
                    v-if="perm.knowledge.share.relateMap()"
                    :label="t('resource.relations.title')"
                    :api="SystemSharedRelatedResourcesApi"
                    :knowledge="knowledge"
                  />
                  <!-- 导出共享知识库 -->
                  <ExportKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    :label="t('common.actions.export')"
                    :api="SystemSharedKnowledgeApi"
                    :knowledge="knowledge"
                    v-if="perm.knowledge.share.export()"
                  />
                  <!-- 删除共享知识库 -->
                  <DeleteKnowledgeAction
                    v-model:loading="knowledgeOperationLoading"
                    :label="t('common.actions.delete')"
                    :api="SystemSharedKnowledgeApi"
                    :knowledge="knowledge"
                    @delete="refreshKnowledge"
                    v-if="perm.knowledge.share.delete()"
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
