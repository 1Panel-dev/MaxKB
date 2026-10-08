<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import SystemResourceKnowledgeApi from '@/api/admin/system/resource-management/knowledge/knowledge'
import SystemCommonApi from '@/api/admin/system/common'
import SystemWorkspaceApi from '@/api/admin/system/workspace'
import type { KnowledgeItem, Dict, OptionItem } from '@/api/types'
import { useStore } from '@/stores'
import { datetimeFormat } from '@/utils/time'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import SystemRelatedResourcesApi from '@/api/admin/system/resource-management/related-resources'

import {
  AuthorizeKnowledgeAction,
  DeleteKnowledgeAction,
  EmbeddingKnowledgeAction,
  ExportKnowledgeAction,
  GenerateQuestionsAction,
  KeywordIndexKnowledgeAction,
  McpConfigKnowledgeAction,
  RelatedResourcesKnowledgeAction,
  SettingKnowledgeAction,
  SyncKnowledgeAction,
} from '@/views/knowledge/knowledge-card/action-dropdown/index.ts'

const { auth } = useStore()

/* 工具分页与筛选 */
const loading = ref(false)
const knowledgeOperationLoading = ref(false)
const knowledgeData = ref<KnowledgeItem[]>([])
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })
const KnowledgeQuery = ref<Dict<unknown>>()
const creatorOptions = ref<OptionItem<string>[]>([])
const workspaceOptions = ref<OptionItem<string>[]>([])
const selectedWorkspaceIds = ref<string[]>([])
const searchFields = computed(() => [
  { label: '创建者', value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
  { label: '名称', value: 'name' },
  {
    label: '类型',
    value: 'type',
    options: [
      { value: KNOWLEDGE_TYPE.BASE, label: '通用知识库' },
      { value: KNOWLEDGE_TYPE.WEB, label: 'Web 知识库' },
      { value: KNOWLEDGE_TYPE.LARK, label: '飞书知识库' },
      { value: KNOWLEDGE_TYPE.WORKFLOW, label: '工作流知识库' },
    ],
  },
])

function loadCreatorOptions(keyword: string) {
  return SystemCommonApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ value: id, label: nick_name }))
  })
}

function loadKnowledgePage() {
  loading.value = true
  return SystemResourceKnowledgeApi.getKnowledgePage(pagination.value, {
    ...KnowledgeQuery.value,
    ...(selectedWorkspaceIds.value.length ? { workspace_ids: JSON.stringify(selectedWorkspaceIds.value) } : {}),
  })
    .then((page) => {
      knowledgeData.value = page.records
      pagination.value.total = page.total
    })
    .finally(() => {
      loading.value = false
    })
}

function getKnowledgeType(knowledge: KnowledgeItem) {
  switch (knowledge.type) {
    case KNOWLEDGE_TYPE.WEB:
      return 'Web 知识库'
    case KNOWLEDGE_TYPE.LARK:
      return '飞书知识库'
    case KNOWLEDGE_TYPE.WORKFLOW:
      return '工作流知识库'
    default:
      return '通用知识库'
  }
}

function handleSearchChange(query?: Dict<unknown>) {
  KnowledgeQuery.value = query
  return handleFilterChange()
}

function handleFilterChange() {
  pagination.value.currentPage = 1
  return loadKnowledgePage()
}

onMounted(() => {
  loadKnowledgePage()
  if (auth.isEE) {
    SystemWorkspaceApi.getSystemWorkspaceList().then((workspaces) => {
      workspaceOptions.value = workspaces.flatMap(({ id, name }) => (id ? [{ value: id, label: name }] : []))
    })
  }
})
</script>

<template>
  <MkViewLayout>
    <template #default="{ Header, title }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
      </component>
      <MkTable
        v-model:pagination-config="pagination"
        v-loading="loading || knowledgeOperationLoading"
        :data="knowledgeData"
        :max-table-height="210"
        @current-change="loadKnowledgePage"
        @size-change="loadKnowledgePage"
      >
        <el-table-column prop="name" label="名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex-align-center gap-2">
              <KnowledgeIcon :type="row.type" class="shrink-0" />
              <span class="truncate" :title="row.name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="200">
          <template #default="{ row }">
            {{ getKnowledgeType(row) }}
          </template>
        </el-table-column>
        <el-table-column v-if="auth.isEE" prop="workspace_name" min-width="160" show-overflow-tooltip>
          <template #header>
            <MkTableFilter mode="multiple" v-model="selectedWorkspaceIds" label="工作空间" :options="workspaceOptions" @change="handleFilterChange" />
          </template>
        </el-table-column>
        <el-table-column prop="nick_name" label="创建者" min-width="120" show-overflow-tooltip />
        <el-table-column label="更新时间" width="180">
          <template #default="{ row }">{{ datetimeFormat(row.update_time) }}</template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <div class="flex-align-center">
              <!-- 向量化 -->
              <EmbeddingKnowledgeAction
                v-model:loading="knowledgeOperationLoading"
                display="button"
                label="向量化"
                :api="SystemResourceKnowledgeApi"
                :knowledge="row"
              />
              <MkTableMoreDropdown>
                <!-- 同步 Web 知识库 -->
                <SyncKnowledgeAction
                  v-if="row.type === KNOWLEDGE_TYPE.WEB"
                  v-model:loading="knowledgeOperationLoading"
                  label="同步"
                  :api="SystemResourceKnowledgeApi"
                  :knowledge="row"
                />
                <!-- 生成问题 -->
                <GenerateQuestionsAction
                  v-model:loading="knowledgeOperationLoading"
                  label="生成问题"
                  :api="SystemResourceKnowledgeApi"
                  :knowledge="row"
                />
                <!-- 设置 -->
                <SettingKnowledgeAction label="设置" :knowledge="row" />
                <!-- 分词索引 -->
                <KeywordIndexKnowledgeAction
                  v-model:loading="knowledgeOperationLoading"
                  label="分词索引"
                  :api="SystemResourceKnowledgeApi"
                  :knowledge="row"
                />
                <!-- MCP 配置详情 -->
                <McpConfigKnowledgeAction
                  v-model:loading="knowledgeOperationLoading"
                  label="MCP 配置详情"
                  :api="SystemResourceKnowledgeApi"
                  :knowledge="row"
                />
                <!-- 资源授权 -->
                <AuthorizeKnowledgeAction label="资源授权" :knowledge="row" />
                <!-- 查看关联资源 -->
                <RelatedResourcesKnowledgeAction label="查看关联资源" :api="SystemRelatedResourcesApi" :knowledge="row" />
                <!-- 导出 -->
                <ExportKnowledgeAction v-model:loading="knowledgeOperationLoading" label="导出" :api="SystemResourceKnowledgeApi" :knowledge="row" />
                <!-- 删除 -->
                <DeleteKnowledgeAction
                  v-model:loading="knowledgeOperationLoading"
                  label="删除"
                  :api="SystemResourceKnowledgeApi"
                  :knowledge="row"
                  @delete="loadKnowledgePage"
                />
              </MkTableMoreDropdown>
            </div>
          </template>
        </el-table-column>
      </MkTable>
    </template>
  </MkViewLayout>
</template>
