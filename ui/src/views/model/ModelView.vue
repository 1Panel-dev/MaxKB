<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { ModelProviderItem, OptionItem, RequestParams, ModelItem } from '@/api/types'
import { MODEL_TYPE_LABELS } from '@/constants'
import CommonApi from '@/api/admin/workspace/common'
import ModelApi from '@/api/admin/workspace/model/model'
import CommonSystemApi from '@/api/admin/system/common'
import SharedApi from '@/api/admin/workspace/shared.ts'
import ProviderApi from '@/api/admin/workspace/model/provider'
import ModelCard from './components/ModelCard.vue'
import ModelProvider from './components/ModelProvider.vue'
import CreateModelDrawer from './create-model/CreateModelDrawer.vue'
import SelectProviderDrawer from './create-model/SelectProviderDrawer.vue'

const DEFAULT_MODEL_PROVIDER: ModelProviderItem = {
  icon: '',
  name: '全部模型',
  provider: 'all',
}

const loading = ref(false)
const currentProvider = ref<ModelProviderItem>(DEFAULT_MODEL_PROVIDER)
const modelProviders = ref<ModelProviderItem[]>([])
const ModelItems = ref<ModelItem[]>([])
const modelQuery = ref<RequestParams>()
const creatorOptions = ref<OptionItem<string>[]>([])
const selectProviderDrawerRef = ref<InstanceType<typeof SelectProviderDrawer>>()
const createModelDrawerRef = ref<InstanceType<typeof CreateModelDrawer>>()

const isShared = computed(() => currentProvider.value.provider === 'shared')

const getModelIcon = computed(
  () => (model: ModelItem) =>
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
  const requestApi = isShared.value ? CommonSystemApi : CommonApi
  return requestApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
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
    ? SharedApi.getModelList(modelQuery.value)
    : ModelApi.getModelList(query)

  return request
    .then((models) => {
      ModelItems.value = models
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

/* 创建模型 */
function handleOpenCreateModel() {
  selectProviderDrawerRef.value?.open()
}

function handleCreateProviderSelect(provider: ModelProviderItem) {
  createModelDrawerRef.value?.open(provider)
}

function handleBackToProviderSelect() {
  selectProviderDrawerRef.value?.open()
}

onMounted(() => {
  Promise.all([loadModelProviders(), loadModels()])
})
</script>

<template>
  <MkViewLayout class="workspace-model-view" collapsible>
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
          <el-button type="primary" class="ml-3" @click="handleOpenCreateModel">
            <MkIcon name="icon_add_outlined" />
            <span>添加模型</span>
          </el-button>
        </div>
      </component>
      <div v-loading="loading">
        <div v-if="ModelItems.length" class="mk-resource-card-grid">
          <ModelCard
            v-for="model in ModelItems"
            :key="model.id"
            :model="model"
            :icon="getModelIcon(model)"
            :shared="isShared"
          />
        </div>
        <MkEmpty v-else class="mt-24" />
      </div>

      <SelectProviderDrawer
        ref="selectProviderDrawerRef"
        :providers="modelProviders"
        @select="handleCreateProviderSelect"
      />
      <CreateModelDrawer
        ref="createModelDrawerRef"
        :providers="modelProviders"
        @back="handleBackToProviderSelect"
        @refresh="loadModels"
      />
    </template>
  </MkViewLayout>
</template>

<style scoped lang="scss"></style>
