<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import SystemModelApi from '@/api/admin/system/resource-management/model'
import SystemRelatedResourcesApi from '@/api/admin/system/resource-management/related-resources'
import SystemCommonApi from '@/api/admin/system/common'
import SystemWorkspaceApi from '@/api/admin/system/workspace'
import SystemModelProviderApi from '@/api/admin/model-provider'
import type { Dict, ModelItem, ModelProviderItem, OptionItem } from '@/api/types'
import { MODEL_TYPE_LABELS } from '@/constants'
import { useStore } from '@/stores'
import { datetimeFormat } from '@/utils/time'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { EditModelAction, AuthorizeModelAction, ParamSettingAction, RelatedResourcesModelAction } from '@/views/model/model-card/action-dropdown'

const { auth } = useStore()

/* 模型分页与筛选 */
const loading = ref(false)
const modelsData = ref<ModelItem[]>([])
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })
const modelQuery = ref<Dict<unknown>>()
const creatorOptions = ref<OptionItem<string>[]>([])
const workspaceOptions = ref<OptionItem<string>[]>([])
const selectedWorkspaceIds = ref<string[]>([])
const searchFields = computed(() => [
  { label: '模型名称', value: 'name' },
  { label: '模型类型', value: 'model_type', options: Object.entries(MODEL_TYPE_LABELS).map(([value, label]) => ({ value, label })) },
  { label: '创建者', value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])

function loadCreatorOptions(keyword: string) {
  return SystemCommonApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ value: id, label: nick_name }))
  })
}

function loadModels() {
  loading.value = true
  return SystemModelApi.getModelPage(pagination.value, {
    ...modelQuery.value,
    ...(selectedWorkspaceIds.value.length ? { workspace_ids: JSON.stringify(selectedWorkspaceIds.value) } : {}),
  })
    .then((page) => {
      modelsData.value = page.records
      pagination.value.total = page.total
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSearchChange(query?: Dict<unknown>) {
  modelQuery.value = query
  return handleFilterChange()
}

function handleFilterChange() {
  pagination.value.currentPage = 1
  return loadModels()
}

/* 供应商展示 */
const providers = ref<ModelProviderItem[]>([])
const providerById = computed(() => new Map(providers.value.map((provider) => [provider.provider, provider])))

function getProvider(model: ModelItem): ModelProviderItem {
  return providerById.value.get(model.provider) ?? { provider: model.provider, name: model.provider, icon: '' }
}

/* 删除成功后保留筛选，末页删空时退回上一页。 */
function handleDeleteModel(model: ModelItem) {
  return MsgConfirm(
    `确认删除模型：${model.name}？`,
    model.resource_count ? `该模型已被 ${model.resource_count} 个资源引用，删除后相关资源将无法正常运行，请谨慎操作。` : '',
  )
    .then(() => {
      loading.value = true
      return SystemModelApi.deleteModel(model.id).then(() => {
        MsgSuccess('删除成功')
        if (modelsData.value.length === 1 && pagination.value.currentPage > 1) pagination.value.currentPage -= 1
        return loadModels()
      })
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

onMounted(() => {
  loadCreatorOptions('')
  loadModels()
  SystemModelProviderApi.getProviderList().then((result) => {
    providers.value = result
  })
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
        v-loading="loading"
        :data="modelsData"
        :max-table-height="210"
        @current-change="loadModels"
        @size-change="loadModels"
        resizable
      >
        <el-table-column prop="name" label="名称" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex-align-center gap-2">
              <span v-if="getProvider(row).icon" class="h-5 w-5 shrink-0" v-html="getProvider(row).icon" />
              <span class="truncate" :title="row.name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="provider" label="供应商" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex-align-center gap-2">
              <span v-if="getProvider(row).icon" class="h-5 w-5 shrink-0" v-html="getProvider(row).icon" />
              <span class="truncate" :title="getProvider(row).name">{{ getProvider(row).name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="model_type" label="模型类型" width="140">
          <template #default="{ row }">{{ MODEL_TYPE_LABELS[row.model_type] ?? row.model_type }}</template>
        </el-table-column>
        <el-table-column prop="model_name" label="基础模型" min-width="180" show-overflow-tooltip />
        <el-table-column v-if="auth.isEE" prop="workspace_name" label="工作空间" min-width="160" show-overflow-tooltip>
          <template #header
            ><MkTableFilter v-model="selectedWorkspaceIds" label="工作空间" :options="workspaceOptions" @change="handleFilterChange"
          /></template>
        </el-table-column>
        <el-table-column prop="nick_name" label="创建者" min-width="120" show-overflow-tooltip />
        <el-table-column label="更新时间" width="180"
          ><template #default="{ row }">{{ datetimeFormat(row.update_time) }}</template></el-table-column
        >
        <el-table-column label="创建时间" width="180"
          ><template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template></el-table-column
        >
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <div class="flex-align-center gap-1">
              <!-- 编辑模型 -->
              <EditModelAction
                display="button"
                label="编辑"
                :api="SystemModelApi"
                :model="row"
                :provider="getProvider(row)"
                :disabled="loading"
                @refresh="loadModels"
              />

              <!-- 资源授权 -->
              <AuthorizeModelAction display="button" label="资源授权" :model="row" />
              <!-- 更多模型操作 -->
              <MkTableMoreDropdown persistent>
                <!-- 模型参数设置 -->
                <ParamSettingAction
                  v-if="['TTS', 'LLM', 'IMAGE', 'TTI', 'STT', 'EMBEDDING'].includes(row.model_type)"
                  label="模型参数设置"
                  :api="SystemModelApi"
                  :model="row"
                />
                <!-- 查看关联资源 -->
                <RelatedResourcesModelAction label="查看关联资源" :api="SystemRelatedResourcesApi" :model="row" />
                <!-- 删除模型 -->
                <MkDropdownItem divided :disabled="loading" @click="handleDeleteModel(row)">
                  <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>删除
                </MkDropdownItem>
              </MkTableMoreDropdown>
            </div>
          </template>
        </el-table-column>
      </MkTable>
    </template>
  </MkViewLayout>
</template>
