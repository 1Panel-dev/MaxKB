<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { Dict, ModelItem, ModelProviderItem, OptionItem } from '@/api/types'
import { MODEL_TYPE_LABELS } from '@/constants'
import CommonApi from '@/api/admin/workspace/common'
import ModelApi from '@/api/admin/workspace/model/model'
import CommonSystemApi from '@/api/admin/system/common'
import SharedApi from '@/api/admin/workspace/shared.ts'
import ProviderApi from '@/api/admin/model-provider.ts'
import ModelCard from './model-card/ModelCard.vue'
import ModelCreateButton from './create-model/ModelCreateButton.vue'
import ModelProvider from './components/ModelProvider.vue'
import { DeleteModelAction, EditModelAction, ParamSettingAction } from './model-card/action-dropdown'

const DEFAULT_MODEL_PROVIDER: ModelProviderItem = { icon: '', name: '全部模型', provider: 'all' }

const loading = ref(false)
const currentProvider = ref<ModelProviderItem>(DEFAULT_MODEL_PROVIDER)
const modelProviders = ref<ModelProviderItem[]>([])
const ModelItems = ref<ModelItem[]>([])
const modelQuery = ref<Dict<unknown>>()
const creatorOptions = ref<OptionItem<string>[]>([])

const isShared = computed(() => currentProvider.value.provider === 'shared')

function getModelProvider(model: ModelItem): ModelProviderItem {
  return modelProviders.value.find(({ provider }) => provider === model.provider) ?? { icon: '', name: model.provider, provider: model.provider }
}

/* 搜索 */
const searchFields = computed(() => [
  { label: '模型名称', value: 'name' },
  { label: '模型类型', value: 'model_type', options: Object.entries(MODEL_TYPE_LABELS).map(([value, label]) => ({ label, value })) },
  { label: '创建者', value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])

function loadCreatorOptions(keyword: string) {
  const requestApi = isShared.value ? CommonSystemApi : CommonApi
  return requestApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ label: nick_name, value: id }))
  })
}

function handleSearchChange(query?: Dict<unknown>) {
  modelQuery.value = query
  loadModels()
}

/* 模型列表 */
function loadModels() {
  loading.value = true

  const provider = currentProvider.value.provider
  const query = { ...modelQuery.value, ...(provider !== 'all' && provider !== 'shared' ? { provider } : {}) }

  const request = isShared.value ? SharedApi.getModelList(modelQuery.value) : ModelApi.getModelList(query)

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

onMounted(() => {
  Promise.all([loadModelProviders(), loadModels()])
})
</script>

<template>
  <MkViewLayout class="workspace-model-view" collapsible>
    <template #aside>
      <ModelProvider :model-value="currentProvider" :providers="modelProviders" @update:model-value="handleProviderSelect" />
    </template>

    <template #default="{ Header }">
      <component :is="Header">
        <h4>{{ currentProvider.name }}</h4>
        <div class="flex items-center">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <ModelCreateButton v-if="!isShared" :current-provider="currentProvider" :providers="modelProviders" @refresh="loadModels" :api="ModelApi" />
        </div>
      </component>
      <div v-loading="loading">
        <div v-if="ModelItems.length" class="mk-resource-card-grid">
          <template v-for="model in ModelItems" :key="model.id">
            <ModelCard
              :api="ModelApi"
              :model="model"
              :provider="getModelProvider(model)"
              :refresh="loadModels"
              :shared="isShared"
              :disabled="isShared"
            >
              <template #action-dropdown>
                <EditModelAction label="编辑" :api="ModelApi" :model="model" :provider="getModelProvider(model)" @refresh="loadModels" />
                <ParamSettingAction v-if="model.model_type !== 'RERANKER'" label="模型参数设置" :api="ModelApi" :model="model" />
                <!-- // TODO: 资源授权-统一处理-->
                <!-- // TODO: 查看关联资源-->

                <DeleteModelAction label="删除" :api="ModelApi" :model="model" @refresh="loadModels" />
              </template>
            </ModelCard>
          </template>
        </div>
        <MkEmpty v-else class="mt-24" />
      </div>
    </template>
  </MkViewLayout>
</template>

<style scoped lang="scss"></style>
