<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { Dict, KnowledgeItem, OptionItem } from '@/api/types'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import SystemCommonApi from '@/api/admin/system/common'
import SystemResourceKnowledgeApi from '@/api/admin/system/resource-management/knowledge/knowledge'
import SystemRelatedResourcesApi from '@/api/admin/system/resource-management/related-resources'
import SystemWorkspaceApi from '@/api/admin/system/workspace'
import {
  AuthorizeKnowledgeAction,
  DeleteKnowledgeAction,
  EmbeddingKnowledgeAction,
  ExportKnowledgeAction,
  GenerateQuestionsAction,
  KeywordIndexKnowledgeAction,
  McpConfigKnowledgeAction,
  RelatedResourcesKnowledgeAction,
  SyncKnowledgeAction,
} from '@/views/knowledge/knowledge-card/action-dropdown/index.ts'
import { KNOWLEDGE_TYPE_MAP } from '@/constants/knowledge'
import { useStore } from '@/stores'
import { toOrderBy } from '@/utils/common'
import { datetimeFormat } from '@/utils/time'
import perm from '@/permission'

const { t } = useI18n({ useScope: 'global' })

const { auth } = useStore()
const router = useRouter()

/* 系统资源知识库详情入口 */
function handleOpenKnowledge(knowledge: KnowledgeItem) {
  void router.push({
    name: 'system-resource-knowledge-detail',
    params: { knowledgeId: knowledge.id, type: KNOWLEDGE_TYPE_MAP[knowledge.type] },
  })
}

function handleOpenKnowledgeSetting(knowledge: KnowledgeItem) {
  void router.push({
    name: knowledge.type === KNOWLEDGE_TYPE.BASE ? 'system-resource-knowledge-setting' : 'system-resource-knowledge-base-setting',
    params: { knowledgeId: knowledge.id, type: KNOWLEDGE_TYPE_MAP[knowledge.type] },
  })
}

/* 知识库分页与筛选 */
const loading = ref(false)
const knowledgeOperationLoading = ref(false)
const knowledgeData = ref<KnowledgeItem[]>([])
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })
const KnowledgeQuery = ref<Dict<unknown>>()
const orderBy = ref<string>()
const creatorOptions = ref<OptionItem<string>[]>([])
const workspaceOptions = ref<OptionItem<string>[]>([])
const selectedWorkspaceIds = ref<string[]>([])
const searchFields = computed(() => [
  { label: t('common.name.label'), value: 'name' },
  { label: t('common.labels.creator'), value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])
const selectedType = ref<number | null>(null)
const typeOptions = computed(() => [
  { value: KNOWLEDGE_TYPE.BASE, label: t('knowledge.base.label') },
  { value: KNOWLEDGE_TYPE.WEB, label: t('knowledge.web.label') },
  { value: KNOWLEDGE_TYPE.LARK, label: t('knowledge.lark.label') },
  { value: KNOWLEDGE_TYPE.WORKFLOW, label: t('knowledge.workflow.label') },
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
    order_by: orderBy.value,
    ...(selectedWorkspaceIds.value.length ? { workspace_ids: JSON.stringify(selectedWorkspaceIds.value) } : {}),
    ...(selectedType.value !== null && selectedType.value !== undefined ? { type: selectedType.value } : {}),
  })
    .then((page) => {
      knowledgeData.value = page.records
      pagination.value.total = page.total
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSearchChange(query?: Dict<unknown>) {
  KnowledgeQuery.value = query
  return handleFilterChange()
}

function handleFilterChange() {
  pagination.value.currentPage = 1
  return loadKnowledgePage()
}

/* 表头排序：保留筛选并重新查询第一页。 */
function handleSortChange(sort: Parameters<typeof toOrderBy>[0]) {
  orderBy.value = toOrderBy(sort)
  return handleFilterChange()
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
  <MkViewLayout :title="t('knowledge.title')">
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
        @sort-change="handleSortChange"
        resizable
      >
        <el-table-column prop="name" :label="t('common.name.label')" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex-align-center gap-2">
              <KnowledgeIcon :type="row.type" :size="20" class="shrink-0" />
              <span class="truncate" :title="row.name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="type" :label="t('common.labels.type')" width="150">
          <template #header>
            <MkTableFilter
              mode="single"
              v-model="selectedType"
              :label="t('common.labels.type')"
              :options="typeOptions"
              @change="handleFilterChange"
            />
          </template>
          <template #default="{ row }">
            {{ typeOptions.find((option) => option.value === row.type)?.label ?? t('knowledge.base.label') }}
          </template>
        </el-table-column>
        <el-table-column v-if="auth.isEE" prop="workspace_name" min-width="160" show-overflow-tooltip>
          <template #header>
            <MkTableFilter
              mode="multiple"
              v-model="selectedWorkspaceIds"
              :label="t('workspace.title')"
              filterable
              :options="workspaceOptions"
              @change="handleFilterChange"
            />
          </template>
        </el-table-column>
        <el-table-column prop="nick_name" :label="t('common.labels.creator')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="update_time" :label="t('common.labels.updateTime')" width="180" sortable>
          <template #default="{ row }">{{ datetimeFormat(row.update_time) }}</template>
        </el-table-column>
        <el-table-column prop="create_time" :label="t('common.labels.createTime')" width="180" sortable>
          <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.labels.operation')" width="120" fixed="right">
          <template #default="{ row }">
            <div class="flex-align-center">
              <!-- 进入知识库详情 -->
              <MkTooltip v-if="perm.knowledge.system.edit()" :content="t('common.actions.manage')">
                <el-button text type="primary" @click="handleOpenKnowledge(row)">
                  <MkIcon name="icon_admin_outlined" />
                </el-button>
              </MkTooltip>
              <!-- 向量化 -->
              <EmbeddingKnowledgeAction
                v-model:loading="knowledgeOperationLoading"
                display="button"
                :label="t('knowledge.actions.generateEmbeddings')"
                :api="SystemResourceKnowledgeApi"
                :knowledge="row"
                v-if="perm.knowledge.system.vector()"
              />
              <MkTableMoreDropdown>
                <!-- 同步 Web 知识库 -->
                <SyncKnowledgeAction
                  v-if="row.type !== KNOWLEDGE_TYPE.BASE && perm.knowledge.system.sync()"
                  v-model:loading="knowledgeOperationLoading"
                  :label="t('knowledge.sync.label')"
                  :api="SystemResourceKnowledgeApi"
                  :knowledge="row"
                />
                <!-- 生成问题 -->
                <GenerateQuestionsAction
                  v-model:loading="knowledgeOperationLoading"
                  :label="t('knowledge.generateQuestions.title')"
                  :api="SystemResourceKnowledgeApi"
                  :knowledge="row"
                  v-if="perm.knowledge.system.generate()"
                />
                <!-- 设置 -->
                <MkDropdownItem v-if="perm.knowledge.system.settingRead()" @click.stop="handleOpenKnowledgeSetting(row)">
                  <template #icon><MkIcon name="icon_setting" /></template>
                  {{ t('common.labels.settings') }}
                </MkDropdownItem>
                <!-- 分词索引 -->
                <KeywordIndexKnowledgeAction
                  v-model:loading="knowledgeOperationLoading"
                  :label="t('knowledge.actions.buildKeywordIndex')"
                  :api="SystemResourceKnowledgeApi"
                  :knowledge="row"
                  v-if="perm.knowledge.system.token()"
                />
                <!-- MCP 服务配置 -->
                <McpConfigKnowledgeAction
                  v-model:loading="knowledgeOperationLoading"
                  :label="t('resource.mcpConfig.title')"
                  :api="SystemResourceKnowledgeApi"
                  :knowledge="row"
                  v-if="perm.knowledge.system.mcpConfig()"
                />
                <!-- 资源授权 -->
                <AuthorizeKnowledgeAction v-if="perm.knowledge.system.auth()" :label="t('authorization.resource.title')" :knowledge="row" />
                <!-- 查看关联资源 -->
                <RelatedResourcesKnowledgeAction
                  v-if="perm.knowledge.system.relateMap()"
                  :label="t('resource.relations.title')"
                  :api="SystemRelatedResourcesApi"
                  :knowledge="row"
                />
                <!-- 导出 -->
                <ExportKnowledgeAction
                  v-if="perm.knowledge.system.export()"
                  v-model:loading="knowledgeOperationLoading"
                  :label="t('common.actions.export')"
                  :api="SystemResourceKnowledgeApi"
                  :knowledge="row"
                />
                <!-- 删除 -->
                <DeleteKnowledgeAction
                  v-model:loading="knowledgeOperationLoading"
                  :label="t('common.actions.delete')"
                  :api="SystemResourceKnowledgeApi"
                  :knowledge="row"
                  @delete="loadKnowledgePage"
                  v-if="perm.knowledge.system.delete()"
                />
              </MkTableMoreDropdown>
            </div>
          </template>
        </el-table-column>
      </MkTable>
    </template>
  </MkViewLayout>
</template>
