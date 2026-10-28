<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import SystemResourceApplicationApi from '@/api/admin/system/resource-management/application/application'
import SystemCommonApi from '@/api/admin/system/common'
import SystemWorkspaceApi from '@/api/admin/system/workspace'
import SystemResourceTriggerApi from '@/api/admin/system/resource-management/resource-trigger'
import type { ApplicationDetail, Dict, OptionItem } from '@/api/types'
import { APPLICATION_TYPE } from '@/api/enums'
import { useStore } from '@/stores'
import { datetimeFormat } from '@/utils/time'
import { isWorkFlow, toOrderBy } from '@/utils/common'
import {
  AuthorizeApplicationAction,
  ExportApplicationAction,
  PortalApplicationAction,
  DeleteApplicationAction,
  TriggerApplicationAction,
} from '@/views/application/application-card/action-dropdown'
import perm from '@/permission'

const { auth } = useStore()
const router = useRouter()

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
  { label: '名称', value: 'name' },
  { label: '创建者', value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])
const selectedType = ref<string | null>(null)
const typeOptions = computed(() => [
  { value: APPLICATION_TYPE.SIMPLE, label: '简易' },
  { value: APPLICATION_TYPE.WORK_FLOW, label: '高级' },
])
const selectedStatus = ref<string | null>(null)
const applicationStatusOptions = computed(() => [
  { value: 'unpublished', label: '未发布' },
  { value: 'published', label: '已发布' },
  { value: 'on_portal', label: '已上架' },
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
  <MkViewLayout>
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
        <el-table-column prop="name" label="名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex-align-center gap-2">
              <ApplicationIcon :icon="row.icon" :size="20" class="shrink-0" />
              <!-- 查看智能体详情 -->
              <el-link class="min-w-0" @click="handleOpenApplication(row)">
                <span class="truncate">{{ row.name }}</span>
              </el-link>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100">
          <template #header>
            <MkTableFilter mode="single" v-model="selectedType" label="类型" :options="typeOptions" @change="handleFilterChange" />
          </template>
          <template #default="{ row }">
            <el-tag v-if="isWorkFlow(row.type)" type="warning" size="small">高级</el-tag>
            <el-tag v-else type="primary" class="default" size="small">简易</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #header>
            <MkTableFilter mode="single" v-model="selectedStatus" label="状态" :options="applicationStatusOptions" @change="handleFilterChange" />
          </template>
          <template #default="{ row }">
            <MkStatusLabel v-if="row.is_portal" type="custom" label="已上架" icon="icon_launch" />
            <MkStatusLabel
              v-else
              :active="row.is_publish"
              active-text="已发布"
              inactive-text="未发布"
              :icon="row.is_publish ? undefined : 'icon_time_filled'"
            />
          </template>
        </el-table-column>
        <el-table-column v-if="auth.isEE" prop="workspace_name" min-width="160" show-overflow-tooltip>
          <template #header>
            <MkTableFilter mode="multiple" v-model="selectedWorkspaceIds" label="工作空间" :options="workspaceOptions" @change="handleFilterChange" />
          </template>
        </el-table-column>
        <el-table-column prop="nick_name" label="创建者" min-width="120" show-overflow-tooltip />
        <el-table-column prop="publish_time" label="发布时间" width="180" sortable>
          <template #default="{ row }">{{ datetimeFormat(row.publish_time) || '-' }}</template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" sortable>
          <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <div class="flex-align-center">
              <!-- TODO：对话 -->
              <MkTooltip content="去对话">
                <el-button text type="primary">
                  <MkIcon name="icon_new-chat_outlined" />
                </el-button>
              </MkTooltip>
              <!-- 进入智能体详情 -->
              <MkTooltip v-if="perm.application.system.edit()" content="管理">
                <el-button text type="primary" @click="handleOpenApplication(row)">
                  <MkIcon name="icon_admin_outlined" />
                </el-button>
              </MkTooltip>

              <MkTableMoreDropdown>
                <!-- 资源授权 -->
                <AuthorizeApplicationAction v-if="perm.application.system.auth()" label="资源授权" :application="row" />
                <!-- 智能体触发器 -->
                <TriggerApplicationAction v-if="perm.application.system.triggerRead()" label="触发器" :api="SystemResourceTriggerApi" :application="row" />
                <!-- 门户上下架 -->
                <PortalApplicationAction
                  v-model:loading="operationLoading"
                  :api="SystemResourceApplicationApi"
                  :application="row"
                  @change="row.is_portal = $event"
                  v-if="perm.application.system.portalUp() && row.is_publish"
                />
                <!-- 导出 -->
                <ExportApplicationAction v-if="perm.application.system.export()" v-model:loading="operationLoading" label="导出" :api="SystemResourceApplicationApi" :application="row" />
                <!-- 删除 -->
                <DeleteApplicationAction
                  v-model:loading="operationLoading"
                  label="删除"
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
