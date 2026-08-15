<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { WarningFilled } from '@element-plus/icons-vue'
import type { ModelProvider, WorkspaceModel } from '@/api/types'
import ModelApi from '@/api/admin/workspace/model/model'
import ProviderApi from '@/api/admin/workspace/model/provider'
import MkListItem from '@/components/mk-search-list/mk-list-item.vue'
import { dateFormat } from '@/utils/time'

type ModelNavigation = 'all' | 'shared' | `provider:${string}`

const LOCAL_PROVIDER_IDS = new Set([
  'model_docker_ai_provider',
  'model_local_provider',
  'model_ollama_provider',
  'model_vllm_provider',
  'model_xinference_provider',
])

const MODEL_TYPE_LABELS: Record<string, string> = {
  EMBEDDING: '向量模型',
  IMAGE: '图像模型',
  ITV: '图生视频',
  LLM: '大语言模型',
  RERANKER: '重排模型',
  STT: '语音识别',
  TTI: '文生图',
  TTS: '语音合成',
  TTV: '文生视频',
}

const route = useRoute()
const workspaceId = computed(() => String(route.params.workspaceId))
const loading = ref(false)
const activeNavigation = ref<ModelNavigation>('all')
const modelProviders = ref<ModelProvider[]>([])
const workspaceModels = ref<WorkspaceModel[]>([])
const sharedModels = ref<WorkspaceModel[]>([])
const selectedModelId = ref('')
const sortOrder = ref<'newest' | 'oldest'>('newest')

const publicProviders = computed(() =>
  modelProviders.value.filter(({ provider }) => !LOCAL_PROVIDER_IDS.has(provider)),
)
const privateProviders = computed(() =>
  modelProviders.value.filter(({ provider }) => LOCAL_PROVIDER_IDS.has(provider)),
)
const providerIconMap = computed(
  () => new Map(modelProviders.value.map((provider) => [provider.provider, provider.icon])),
)
const activeTitle = computed(() => {
  if (activeNavigation.value === 'shared') return '共享模型'
  if (activeNavigation.value === 'all') return '全部模型'

  const providerId = activeNavigation.value.replace('provider:', '')
  return modelProviders.value.find(({ provider }) => provider === providerId)?.name ?? '全部模型'
})
const visibleModels = computed(() => {
  let result = activeNavigation.value === 'shared' ? sharedModels.value : workspaceModels.value
  if (activeNavigation.value.startsWith('provider:')) {
    const providerId = activeNavigation.value.replace('provider:', '')
    result = result.filter(({ provider }) => provider === providerId)
  }

  return [...result].sort((left, right) => {
    const leftTime = new Date(left.create_time ?? 0).getTime()
    const rightTime = new Date(right.create_time ?? 0).getTime()
    return sortOrder.value === 'newest' ? rightTime - leftTime : leftTime - rightTime
  })
})

/* 模型目录与列表 */
function loadModels() {
  loading.value = true
  return Promise.all([
    ProviderApi.getProviderList(),
    ModelApi.getSelectableModelList(workspaceId.value),
  ])
    .then(([providers, modelCatalog]) => {
      modelProviders.value = [...providers].sort((left, right) =>
        left.name.localeCompare(right.name),
      )
      workspaceModels.value = modelCatalog.model.map((model) => ({
        ...model,
        source: 'workspace',
      }))
      sharedModels.value = modelCatalog.shared_model.map((model) => ({
        ...model,
        source: 'shared',
      }))
    })
    .finally(() => {
      loading.value = false
    })
}

function handleNavigationSelect(navigation: ModelNavigation) {
  activeNavigation.value = navigation
  selectedModelId.value = ''
}

function handleModelSelect(model: WorkspaceModel) {
  selectedModelId.value = model.id
}

function formatCreatedDate(timestamp?: string) {
  return timestamp ? String(dateFormat(timestamp)) : '-'
}

function getModelCreatorText(model: WorkspaceModel) {
  return `${model.nick_name || model.username || '-'} 创建于 ${formatCreatedDate(model.create_time)}`
}

watch(workspaceId, loadModels, { immediate: true })
</script>

<template>
  <MkViewLayout class="workspace-model-view" :loading="loading">
    <template #aside>
      <div class="px-4">
        <MkListItem
          class="-mt-2"
          :active="activeNavigation === 'shared'"
          @click="handleNavigationSelect('shared')"
        >
          <template #default>
            <MkIcon name="icon_assigned_outlined" :size="20" />
            <span>共享模型</span>
          </template>
        </MkListItem>

        <el-divider class="my-1!" />

        <MkListItem :active="activeNavigation === 'all'" @click="handleNavigationSelect('all')">
          <template #default>
            <MkIcon name="icon_moments-categories_outlined" :size="18" />
            <span>全部模型</span>
          </template>
        </MkListItem>
      </div>
      <el-scrollbar class="min-h-0 flex-1 px-4 pb-4">
        <div class="mt-1">
          <MkCollapse v-if="publicProviders.length" :default-expanded="false">
            <template #label>
              <MkIcon name="icon_book_filled" class="text-warning!" :size="20" />
              <span>公有模型</span>
            </template>
            <div class="flex flex-col gap-1">
              <MkListItem
                v-for="provider in publicProviders"
                :key="provider.provider"
                :active="activeNavigation === `provider:${provider.provider}`"
                @click="handleNavigationSelect(`provider:${provider.provider}`)"
              >
                <template #default>
                  <span :innerHTML="provider.icon" class="w-5 h-5" />
                  <span class="min-w-0 flex-1 truncate" :title="provider.name">
                    {{ provider.name }}
                  </span>
                </template>
              </MkListItem>
            </div>
          </MkCollapse>

          <MkCollapse v-if="privateProviders.length" :default-expanded="false">
            <template #label>
              <MkIcon name="icon_book_filled" class="text-warning!" :size="20" />
              <span>私有模型</span>
            </template>
            <div class="flex flex-col gap-1">
              <MkListItem
                v-for="provider in privateProviders"
                :key="provider.provider"
                :active="activeNavigation === `provider:${provider.provider}`"
                @click="handleNavigationSelect(`provider:${provider.provider}`)"
              >
                <template #default>
                  <span :innerHTML="provider.icon" class="w-5 h-5" />

                  <span class="min-w-0 flex-1 truncate" :title="provider.name">
                    {{ provider.name }}
                  </span>
                </template>
              </MkListItem>
            </div>
          </MkCollapse>
        </div>
      </el-scrollbar>
    </template>

    <template #default="{ Header }">
      <component :is="Header">
        <h4>{{ activeTitle }}</h4>
      </component>

      <div v-if="visibleModels.length" class="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <article
          v-for="model in visibleModels"
          :key="`${model.source}:${model.id}`"
          class="model-card"
          :class="{ active: selectedModelId === model.id }"
          @click="handleModelSelect(model)"
        >
          <header class="flex min-w-0 items-start gap-3">
            <span class="w-8 h-8" :innerHTML="providerIconMap.get(model.provider)" />

            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2">
                <h5 class="truncate" :title="model.name">{{ model.name }}</h5>
                <el-tooltip
                  v-if="model.status === 'ERROR' || model.status === 'PAUSE_DOWNLOAD'"
                  :content="String(model.meta?.message ?? '模型不可用')"
                >
                  <MkIcon :icon="WarningFilled" class="text-danger!" />
                </el-tooltip>
              </div>
              <p class="truncate text-N600" :title="getModelCreatorText(model)">
                {{ getModelCreatorText(model) }}
              </p>
            </div>
          </header>

          <dl class="mt-7 grid grid-cols-[auto_minmax(0,1fr)] gap-x-4 gap-y-2">
            <dt class="text-N600">模型类型</dt>
            <dd class="truncate" :title="MODEL_TYPE_LABELS[model.model_type] ?? model.model_type">
              {{ MODEL_TYPE_LABELS[model.model_type] ?? model.model_type }}
            </dd>
            <dt class="text-N600">基础模型</dt>
            <dd class="truncate" :title="model.model_name">{{ model.model_name }}</dd>
          </dl>
        </article>
      </div>
      <MkEmpty v-else class="mt-24" />
    </template>
  </MkViewLayout>
</template>

<style scoped lang="scss"></style>
