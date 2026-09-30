<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import SystemResourceApplicationApi from '@/api/admin/system/resource-management/application/application'
import SystemCommonApi from '@/api/admin/system/common'
import SystemWorkspaceApi from '@/api/admin/system/workspace'
import SystemResourceTriggerApi from '@/api/admin/system/resource-management/resource-trigger'
import type { ApplicationDetail, Dict, OptionItem } from '@/api/types'
import { useStore } from '@/stores'
import { datetimeFormat } from '@/utils/time'
import { APPLICATION_TYPE } from '@/api/enums'
import { isWorkFlow } from '@/utils/application'
import {
  AuthorizeApplicationAction,
  ExportApplicationAction,
  DeleteApplicationAction,
  TriggerApplicationAction,
} from '@/views/application/application-card/action-dropdown'

const { auth } = useStore()

/* 工具分页与筛选 */
const loading = ref(false)
const operationLoading = ref(false)
const applicationData = ref<ApplicationDetail[]>([])
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })
const applicationQuery = ref<Dict<unknown>>()
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
      { value: APPLICATION_TYPE.WORK_FLOW, label: '高级' },
      { value: APPLICATION_TYPE.SIMPLE, label: '简易' },
    ],
  },
])
const selectedStatusType = ref<boolean | null>(null)
const applicationStatusOptions = computed(() => [
  { value: true, label: '已发布' },
  { value: false, label: '未发布' },
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
    ...(selectedWorkspaceIds.value.length ? { workspace_ids: JSON.stringify(selectedWorkspaceIds.value) } : {}),
    ...(selectedStatusType.value !== null ? { status: JSON.stringify([selectedStatusType.value]) } : {}),
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
        resizable
      >
        <el-table-column prop="name" label="名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex-align-center gap-2">
              <ApplicationIcon :icon="row.icon" class="shrink-0" />
              <span class="truncate" :title="row.name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="150">
          <template #default="{ row }">
            <el-tag v-if="isWorkFlow(row.type)" type="warning" size="small">高级</el-tag>
            <el-tag v-else type="primary" class="default" size="small">简易</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="150">
          <template #header>
            <MkTableFilter mode="single" v-model="selectedStatusType" label="状态" :options="applicationStatusOptions" @change="handleFilterChange" />
          </template>
          <template #default="{ row }">
            <MkStatusLabel :active="row.is_publish" active-text="已发布" inactive-text="未发布" inactive-icon="icon_time_filled" />
          </template>
        </el-table-column>
        <el-table-column v-if="auth.isEE" prop="workspace_name" min-width="160" show-overflow-tooltip>
          <template #header>
            <MkTableFilter mode="multiple" v-model="selectedWorkspaceIds" label="工作空间" :options="workspaceOptions" @change="handleFilterChange" />
          </template>
        </el-table-column>
        <el-table-column prop="nick_name" label="创建者" min-width="120" show-overflow-tooltip />
        <el-table-column label="发布时间" width="180">
          <template #default="{ row }">{{ datetimeFormat(row.publish_time) || '-' }}</template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <div class="flex-align-center">
              <!-- TODO 对话&管理 -->
              <MkTableMoreDropdown>
                <!-- 资源授权 -->
                <AuthorizeApplicationAction label="资源授权" :application="row" />
                <!-- 智能体触发器 -->
                <TriggerApplicationAction label="触发器" :api="SystemResourceTriggerApi" :application="row" />
                <!-- 导出 -->
                <ExportApplicationAction v-model:loading="operationLoading" label="导出" :api="SystemResourceApplicationApi" :application="row" />
                <!-- 删除 -->
                <DeleteApplicationAction
                  v-model:loading="operationLoading"
                  label="删除"
                  :api="SystemResourceApplicationApi"
                  :application="row"
                  @delete="loadApplicationPage"
                />
              </MkTableMoreDropdown>
            </div>
          </template>
        </el-table-column>
      </MkTable>
    </template>
  </MkViewLayout>
</template>
