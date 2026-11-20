<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Dict, ModelItem, ModelProviderItem, OptionItem } from '@/api/types'
import SystemModelProviderApi from '@/api/admin/model-provider'
import SystemCommonApi from '@/api/admin/system/common'
import SystemModelApi from '@/api/admin/system/resource-management/model'
import SystemRelatedResourcesApi from '@/api/admin/system/resource-management/related-resources'
import SystemWorkspaceApi from '@/api/admin/system/workspace'
import { AuthorizeModelAction, EditModelAction, ParamSettingAction, RelatedResourcesModelAction } from '@/views/model/model-card/action-dropdown'
import { MODEL_TYPE_LABELS } from '@/constants/model'
import { useStore } from '@/stores'
import { toOrderBy } from '@/utils/common'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { datetimeFormat } from '@/utils/time'
import perm from '@/permission'

const { t } = useI18n({ useScope: 'global' })
const { auth } = useStore()

/* 模型分页与筛选 */
const loading = ref(false)
const modelsData = ref<ModelItem[]>([])
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })
const modelQuery = ref<Dict<unknown>>()
const orderBy = ref<string>()
const creatorOptions = ref<OptionItem<string>[]>([])
const workspaceOptions = ref<OptionItem<string>[]>([])
const selectedModelType = ref('')
const selectedProvider = ref('')
const selectedWorkspaceIds = ref<string[]>([])
const searchFields = computed(() => [
  { label: t('model.fields.name.label'), value: 'name' },
  { label: t('common.labels.creator'), value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])
const modelTypeOptions = computed(() => Object.entries(MODEL_TYPE_LABELS).map(([value, label]) => ({ value, label })))

function loadCreatorOptions(keyword: string) {
  return SystemCommonApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ value: id, label: nick_name }))
  })
}

function loadModels() {
  loading.value = true
  return SystemModelApi.getModelPage(pagination.value, {
    ...modelQuery.value,
    order_by: orderBy.value,
    ...(selectedModelType.value ? { model_type: selectedModelType.value } : {}),
    ...(selectedProvider.value ? { provider: selectedProvider.value } : {}),
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

/* 表头排序：保留筛选并重新查询第一页。 */
function handleSortChange(sort: Parameters<typeof toOrderBy>[0]) {
  orderBy.value = toOrderBy(sort)
  return handleFilterChange()
}

/* 供应商展示 */
const providers = ref<ModelProviderItem[]>([])
const providerById = computed(() => new Map(providers.value.map((provider) => [provider.provider, provider])))
const providerOptions = computed(() => providers.value.map((provider) => ({ value: provider.provider, label: provider.name })))

function getProvider(model: ModelItem): ModelProviderItem {
  return providerById.value.get(model.provider) ?? { provider: model.provider, name: model.provider, icon: '' }
}

/* 删除成功后保留筛选，末页删空时退回上一页。 */
function handleDeleteModel(model: ModelItem) {
  return MsgConfirm(
    t('model.delete.title', { name: model.name }),
    model.resource_count ? t('model.delete.description', { count: model.resource_count }, model.resource_count) : '',
    { confirmButtonText: t('common.actions.delete') },
  )
    .then(() => {
      loading.value = true
      return SystemModelApi.deleteModel(model.id).then(() => {
        MsgSuccess(t('common.messages.deleteSuccess'))
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
  <MkViewLayout :title="t('model.title')">
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
        @sort-change="handleSortChange"
        resizable
      >
        <el-table-column prop="name" :label="t('common.name.label')" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex-align-center gap-2">
              <span v-if="getProvider(row).icon" class="h-5 w-5 shrink-0" v-html="getProvider(row).icon" />
              <span class="truncate">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="provider" :label="t('model.provider.label')" min-width="160" show-overflow-tooltip>
          <template #header>
            <MkTableFilter
              mode="single"
              v-model="selectedProvider"
              :label="t('model.provider.label')"
              :options="providerOptions"
              @change="handleFilterChange"
            />
          </template>
          <template #default="{ row }">
            <div class="flex-align-center gap-2">
              <span v-if="getProvider(row).icon" class="h-5 w-5 shrink-0" v-html="getProvider(row).icon" />
              <span class="truncate">{{ getProvider(row).name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="model_type" :label="t('model.fields.type.label')" width="140">
          <template #header>
            <MkTableFilter
              mode="single"
              v-model="selectedModelType"
              :label="t('model.fields.type.label')"
              :options="modelTypeOptions"
              @change="handleFilterChange"
            />
          </template>
          <template #default="{ row }">
            {{ MODEL_TYPE_LABELS[row.model_type] ?? row.model_type }}
          </template>
        </el-table-column>
        <el-table-column prop="model_name" :label="t('model.fields.baseModel.label')" min-width="180" show-overflow-tooltip />
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
              <!-- 编辑模型 -->
              <EditModelAction
                display="button"
                :label="t('common.actions.edit')"
                :api="SystemModelApi"
                :model="row"
                :provider="getProvider(row)"
                :disabled="loading"
                @refresh="loadModels"
                v-if="perm.model.system.modify()"
              />

              <!-- 资源授权 -->
              <AuthorizeModelAction v-if="perm.model.system.auth()" display="button" :label="t('authorization.resource.title')" :model="row" />
              <!-- 更多模型操作 -->
              <MkTableMoreDropdown>
                <!-- 模型参数设置 -->
                <ParamSettingAction
                  v-if="['TTS', 'LLM', 'IMAGE', 'TTI', 'STT', 'EMBEDDING'].includes(row.model_type) && perm.model.system.paramSetting()"
                  :label="t('model.actions.parameters')"
                  :api="SystemModelApi"
                  :model="row"
                />
                <!-- 查看关联资源 -->
                <RelatedResourcesModelAction
                  v-if="perm.model.system.relateMap()"
                  :label="t('resource.relations.title')"
                  :api="SystemRelatedResourcesApi"
                  :model="row"
                />
                <!-- 删除模型 -->
                <MkDropdownItem v-if="perm.model.system.delete()" :disabled="loading" @click="handleDeleteModel(row)">
                  <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
                  {{ t('common.actions.delete') }}
                </MkDropdownItem>
              </MkTableMoreDropdown>
            </div>
          </template>
        </el-table-column>
      </MkTable>
    </template>
  </MkViewLayout>
</template>
