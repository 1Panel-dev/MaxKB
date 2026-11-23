<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { ApplicationDetail, Dict, OptionItem } from '@/api/types'
import type { ApiInputField } from '@/workflow-canvas/nodes/base-node/types'
import { APPLICATION_TYPE } from '@/api/enums'
import SystemCommonApi from '@/api/admin/system/common'
import SystemResourceApplicationApi from '@/api/admin/system/resource-management/application/application'
import SystemRelatedResourcesApi from '@/api/admin/system/resource-management/related-resources'
import SystemResourceTriggerApi from '@/api/admin/system/resource-management/resource-trigger'
import SystemWorkspaceApi from '@/api/admin/system/workspace'
import { CHAT_API_BASE_PATH } from '@/api/constants'
import {
  AuthorizeApplicationAction,
  DeleteApplicationAction,
  ExportApplicationAction,
  McpConfigApplicationAction,
  PortalApplicationAction,
  RelatedResourcesApplicationAction,
  TriggerApplicationAction,
} from '@/views/application/application-card/action-dropdown'
import { useStore } from '@/stores'
import { isWorkFlow, toOrderBy } from '@/utils/common'
import { datetimeFormat } from '@/utils/time'
import perm from '@/permission'

const { t } = useI18n({ useScope: 'global' })
const { auth } = useStore()
const router = useRouter()
const chatBasePath = CHAT_API_BASE_PATH.replace(/\/api$/, '')

function apiQuery(application: ApplicationDetail) {
  const query = application?.work_flow?.nodes
    ?.find((n) => n.id === 'base-node')
    ?.properties?.api_input_field_list.map((field: ApiInputField) => {
      return `${field.variable}=${field.default_value}`
    })
    .join('&')
  if (query) {
    return '?' + query
  }
  return ''
}

function toChat(application: ApplicationDetail) {
  return SystemResourceApplicationApi.getAccessToken(application.id).then((ok) => {
    const accessUrl = ok.access_token ? `${window.location.origin}${chatBasePath}/${ok.access_token}/${apiQuery(application)}` : ''
    window.open(accessUrl, '_blank')
  })
}

function handleOpenApplication(application: ApplicationDetail) {
  void router.push({ name: 'system-resource-application-detail', params: { applicationId: application.id, type: application.type } })
}

/* 工具分页与筛选 */
const loading = ref(false)
const operationLoading = ref(false)
const applicationData = ref<ApplicationDetail[]>([])
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })
const applicationQuery = ref<Dict<unknown>>()
const orderBy = ref<string>()
const creatorOptions = ref<OptionItem<string>[]>([])
const workspaceOptions = ref<OptionItem<string>[]>([])
const selectedWorkspaceIds = ref<string[]>([])
const searchFields = computed(() => [
  { label: t('common.name.label'), value: 'name' },
  { label: t('common.labels.creator'), value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])
const selectedType = ref<string | null>(null)
const typeOptions = computed(() => [
  { value: APPLICATION_TYPE.SIMPLE, label: t('application.simple.shortLabel') },
  { value: APPLICATION_TYPE.WORK_FLOW, label: t('application.advanced.shortLabel') },
])
const selectedStatus = ref<string | null>(null)
const applicationStatusOptions = computed(() => [
  { value: 'unpublished', label: t('application.status.unpublished') },
  { value: 'published', label: t('application.status.published') },
  { value: 'on_portal', label: t('application.status.onPortal') },
])

function loadCreatorOptions(keyword: string) {
  return SystemCommonApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ value: id, label: nick_name }))
  })
}

function loadApplicationPage() {
  loading.value = true
  return SystemResourceApplicationApi.getApplicationPage(pagination.value, {
    ...applicationQuery.value,
    order_by: orderBy.value,
    ...(selectedWorkspaceIds.value.length ? { workspace_ids: JSON.stringify(selectedWorkspaceIds.value) } : {}),
    ...(selectedStatus.value ? { status: selectedStatus.value } : {}),
    ...(selectedType.value ? { type: selectedType.value } : {}),
  })
    .then((page) => {
      applicationData.value = page.records
      pagination.value.total = page.total
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSearchChange(query?: Dict<unknown>) {
  applicationQuery.value = query
  return handleFilterChange()
}

function handleFilterChange() {
  pagination.value.currentPage = 1
  return loadApplicationPage()
}

/* 表头排序：保留筛选并重新查询第一页。 */
function handleSortChange(sort: Parameters<typeof toOrderBy>[0]) {
  orderBy.value = toOrderBy(sort)
  return handleFilterChange()
}

onMounted(() => {
  loadApplicationPage()
  if (auth.isEE) {
    SystemWorkspaceApi.getSystemWorkspaceList().then((workspaces) => {
      workspaceOptions.value = workspaces.flatMap(({ id, name }) => (id ? [{ value: id, label: name }] : []))
    })
  }
})
</script>

<template>
  <MkViewLayout :title="t('application.title')">
    <template #default="{ Header, title }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
      </component>
      <MkTable
        v-model:pagination-config="pagination"
        v-loading="loading || operationLoading"
        :data="applicationData"
        :max-table-height="210"
        @current-change="loadApplicationPage"
        @size-change="loadApplicationPage"
        @sort-change="handleSortChange"
        resizable
      >
        <el-table-column prop="name" :label="t('common.name.label')" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex-align-center gap-2">
              <ApplicationIcon :icon="row.icon" :size="20" class="shrink-0" />
              <span class="truncate">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="type" :label="t('common.labels.type')" width="100">
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
            <el-tag v-if="isWorkFlow(row.type)" type="warning" size="small">{{ t('application.advanced.shortLabel') }}</el-tag>
            <el-tag v-else type="primary" class="default" size="small">{{ t('application.simple.shortLabel') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column width="100">
          <template #header>
            <MkTableFilter
              mode="single"
              v-model="selectedStatus"
              :label="t('common.status.label')"
              :options="applicationStatusOptions"
              @change="handleFilterChange"
            />
          </template>
          <template #default="{ row }">
            <MkStatusLabel v-if="row.is_portal" type="custom" :label="t('application.status.onPortal')" icon="icon_launch" />
            <MkStatusLabel
              v-else
              :active="row.is_publish"
              :active-text="t('application.status.published')"
              :inactive-text="t('application.status.unpublished')"
              :icon="row.is_publish ? undefined : 'icon_time_filled'"
            />
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
        <el-table-column prop="publish_time" :label="t('application.publishTime')" width="180" sortable>
          <template #default="{ row }">{{ datetimeFormat(row.publish_time) || '-' }}</template>
        </el-table-column>
        <el-table-column prop="create_time" :label="t('common.labels.createTime')" width="180" sortable>
          <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.labels.operation')" width="120" fixed="right">
          <template #default="{ row }">
            <div class="flex-align-center">
              <!-- 去对话 -->
              <MkTooltip :content="t('application.actions.chat')">
                <el-button text type="primary" @click="toChat(row)">
                  <MkIcon name="icon_new-chat_outlined" />
                </el-button>
              </MkTooltip>
              <!-- 进入智能体详情 -->
              <MkTooltip v-if="perm.application.system.edit()" :content="t('common.actions.manage')">
                <el-button text type="primary" @click="handleOpenApplication(row)">
                  <MkIcon name="icon_admin_outlined" />
                </el-button>
              </MkTooltip>

              <MkTableMoreDropdown>
                <!-- 资源授权 -->
                <AuthorizeApplicationAction v-if="perm.application.system.auth()" :label="t('authorization.resource.title')" :application="row" />
                <!-- 智能体触发器 -->
                <TriggerApplicationAction
                  v-if="perm.application.system.triggerRead()"
                  :label="t('trigger.title')"
                  :api="SystemResourceTriggerApi"
                  :application-api="SystemResourceApplicationApi"
                  :application="row"
                />
                <!-- MCP 服务配置 -->
                <McpConfigApplicationAction v-if="perm.application.system.mcpConfig()" :label="t('resource.mcpConfig.title')" :application="row" />
                <!-- 查看关联资源 -->
                <RelatedResourcesApplicationAction
                  v-if="perm.application.system.relateMap()"
                  :label="t('resource.relations.title')"
                  :api="SystemRelatedResourcesApi"
                  :application="row"
                />
                <!-- 门户上下架 -->
                <PortalApplicationAction
                  v-model:loading="operationLoading"
                  :api="SystemResourceApplicationApi"
                  :application="row"
                  @change="row.is_portal = $event"
                  v-if="perm.application.system.portalUp() && row.is_publish"
                />
                <!-- 导出 -->
                <ExportApplicationAction
                  v-if="perm.application.system.export() || perm.application.system.exportSkills()"
                  v-model:loading="operationLoading"
                  :label="t('common.actions.export')"
                  :api="SystemResourceApplicationApi"
                  :application="row"
                />
                <!-- 删除 -->
                <DeleteApplicationAction
                  v-model:loading="operationLoading"
                  :label="t('common.actions.delete')"
                  :api="SystemResourceApplicationApi"
                  :application="row"
                  @delete="loadApplicationPage"
                  v-if="perm.application.system.delete()"
                />
              </MkTableMoreDropdown>
            </div>
          </template>
        </el-table-column>
      </MkTable>
    </template>
  </MkViewLayout>
</template>
