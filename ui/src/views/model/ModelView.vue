<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import type {
  ModelProvider as ModelProviderItem,
  OptionItem,
  RequestParams,
  WorkspaceModel,
} from '@/api/types'
import { MODEL_TYPE_LABELS } from '@/constants/model'
import CommonApi from '@/api/admin/workspace/common'
import ModelApi from '@/api/admin/workspace/model/model'
import CommonSystemApi from '@/api/admin/system/common'
import ModelSharedApi from '@/api/admin/workspace/model/model-shared'
import ProviderApi from '@/api/admin/workspace/model/provider'
import ModelCard from './components/ModelCard.vue'
import ModelProvider from './components/ModelProvider.vue'

const DEFAULT_MODEL_PROVIDER: ModelProviderItem = {
  icon: '',
  name: '全部模型',
  provider: 'all',
}

const route = useRoute()
const {
  params: { workspaceId },
} = route

const loading = ref(false)
const currentProvider = ref<ModelProviderItem>(DEFAULT_MODEL_PROVIDER)
const modelProviders = ref<ModelProviderItem[]>([])
const workspaceModels = ref<WorkspaceModel[]>([])
const modelQuery = ref<RequestParams>()
const creatorOptions = ref<OptionItem<string>[]>([])

const isShared = computed(() => currentProvider.value.provider === 'shared')

const getModelIcon = computed(
  () => (model: WorkspaceModel) =>
    modelProviders.value.find(({ provider }) => provider === model.provider)?.icon ?? '',
)

/* 搜索 */
const searchFields = computed(() => [
  { label: '模型名称', value: 'name' },
  {
    label: '模型类型',
    value: 'model_type',
    options: Object.entries(MODEL_TYPE_LABELS).map(([value, label]) => ({ label, value })),
  },
  {
    label: '创建者',
    value: 'create_user',
    options: creatorOptions.value,
    remoteMethod: loadCreatorOptions,
  },
])

function loadCreatorOptions(keyword: string) {
  const request = isShared.value
    ? CommonSystemApi.getAllUsers(keyword ? { nick_name: keyword } : undefined)
    : CommonApi.getAllUsers(keyword ? { nick_name: keyword } : undefined)

  return request.then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ label: nick_name, value: id }))
  })
}

function handleSearchChange(query?: RequestParams) {
  modelQuery.value = query
  loadModels()
}

/* 模型列表 */
function loadModels() {
  loading.value = true

  const provider = currentProvider.value.provider
  const query = {
    ...modelQuery.value,
    ...(provider !== 'all' && provider !== 'shared' ? { provider } : {}),
  }

  const request = isShared.value
    ? ModelSharedApi.getModelList(modelQuery.value)
    : ModelApi.getModelList(query)

  return request
    .then((models) => {
      workspaceModels.value = models
    })
    .finally(() => {
      loading.value = false
    })
}

/* 供应商 */
function loadModelProviders() {
  return ProviderApi.getProviderList().then((providers) => {
    modelProviders.value = [...providers].sort((left, right) => left.name.localeCompare(right.name))
  })
}

function handleProviderSelect(provider: ModelProviderItem) {
  currentProvider.value = provider
  loadModels()
}

onMounted(() => {
  Promise.all([loadModelProviders(), loadModels()])
})
</script>

<template>
  <MkViewLayout class="workspace-model-view" :loading="loading">
    <template #aside>
      <ModelProvider
        :model-value="currentProvider"
        :providers="modelProviders"
        @update:model-value="handleProviderSelect"
      />
    </template>

    <template #default="{ Header }">
      <component :is="Header">
        <h4>{{ currentProvider.name }}</h4>
        <div class="flex items-center">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <el-button type="primary" class="ml-3">
            <MkIcon name="icon_add_outlined" />
            <span>添加模型</span>
          </el-button>
        </div>
      </component>

      <el-row v-if="workspaceModels.length" :gutter="16" class="gap-y-4">
        <el-col
          v-for="model in workspaceModels"
          :key="model.id"
          :xs="24"
          :sm="24"
          :md="12"
          :lg="8"
          :xl="6"
        >
          <ModelCard :model="model" :icon="getModelIcon(model)" :shared="isShared" />
        </el-col>
      </el-row>
      <MkEmpty v-else class="mt-24" />
    </template>
  </MkViewLayout>
</template>

<style scoped lang="scss"></style>
