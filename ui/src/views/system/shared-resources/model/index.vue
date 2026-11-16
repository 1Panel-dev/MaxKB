<script lang="ts" setup>
import { computed, nextTick, onMounted, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Dict, ModelItem, ModelProviderItem, OptionItem } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import ProviderApi from '@/api/admin/model-provider'
import CommonSystemApi from '@/api/admin/system/common'
import SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import RelatedResourcesApi from '@/api/admin/system/shared-resources/related-resources'
import ModelProvider from '@/views/model/components/ModelProvider.vue'
import ButtonAddModel from '@/views/model/create-model/ButtonAddModel.vue'
import ModelCard from '@/views/model/model-card/ModelCard.vue'
import { DeleteModelAction, ParamSettingAction, RelatedResourcesModelAction } from '@/views/model/model-card/action-dropdown'
import EditModelDrawer from '@/views/model/model-card/action-dropdown/edit-model-action/EditModelDrawer.vue'
import AuthorizedWorkspaceAction from '../authorized-workspace-action/index.vue'
import { MODEL_TYPE_MESSAGE_KEYS } from '@/constants/model'
import perm from '@/permission'

const { t } = useI18n({ useScope: 'global' })

const DEFAULT_MODEL_PROVIDER: ModelProviderItem = { icon: '', name: '全部模型', provider: 'all' }

const loading = ref(false)
const currentProvider = ref<ModelProviderItem>(DEFAULT_MODEL_PROVIDER)
const modelProviders = ref<ModelProviderItem[]>([])
const ModelItems = ref<ModelItem[]>([])
const modelQuery = ref<Dict<unknown>>()
const creatorOptions = ref<OptionItem<string>[]>([])
const currentProviderName = computed(() =>
  currentProvider.value.provider === 'all'
    ? t('model.categories.all')
    : currentProvider.value.provider === 'shared'
      ? t('model.categories.shared')
      : currentProvider.value.name,
)

function getModelProvider(model: ModelItem): ModelProviderItem {
  return modelProviders.value.find(({ provider }) => provider === model.provider) ?? { icon: '', name: model.provider, provider: model.provider }
}

/* 搜索 */
const searchFields = computed(() => [
  { label: t('model.fields.name.label'), value: 'name' },
  {
    label: t('model.fields.type.label'),
    value: 'model_type',
    options: Object.entries(MODEL_TYPE_MESSAGE_KEYS).map(([value, key]) => ({ label: t(key), value })),
  },
  { label: t('common.labels.creator'), value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])

function loadCreatorOptions(keyword: string) {
  return CommonSystemApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
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
  const query = { ...modelQuery.value, ...(provider !== 'all' ? { provider } : {}) }

  return SystemSharedModelApi.getModelList(query)
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

/* 卡片与菜单共用编辑抽屉，沿用共享模型编辑权限。 */
const editDrawerMounted = ref(false)
const editModelDrawerRef = useTemplateRef<InstanceType<typeof EditModelDrawer>>('editModelDrawerRef')

async function handleOpenEditModel(model: ModelItem) {
  if (!perm.model.share.modify() || editDrawerMounted.value) return
  editDrawerMounted.value = true
  await nextTick()
  editModelDrawerRef.value?.open(getModelProvider(model), model)
}

onMounted(() => {
  Promise.all([loadModelProviders(), loadModels()])
})
</script>

<template>
  <MkViewLayout :title="t('model.title')" class="shared-model-view" collapsible>
    <template #aside>
      <ModelProvider :model-value="currentProvider" :providers="modelProviders" @update:model-value="handleProviderSelect" />
    </template>

    <template #default="{ Header }">
      <component :is="Header">
        <h4>{{ currentProviderName }}</h4>
        <div class="flex-align-center">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <!-- 添加模型 -->
          <ButtonAddModel
            v-if="perm.model.share.create()"
            :api="SystemSharedModelApi"
            :current-provider="currentProvider"
            :providers="modelProviders"
            @refresh="loadModels"
          />
        </div>
      </component>
      <div v-loading="loading">
        <div v-if="ModelItems.length" class="mk-resource-card-grid">
          <template v-for="model in ModelItems" :key="model.id">
            <ModelCard
              :api="SystemSharedModelApi"
              :model="model"
              :provider="getModelProvider(model)"
              :refresh="loadModels"
              :shared="true"
              @click="handleOpenEditModel(model)"
            >
              <template #action-dropdown>
                <!-- 编辑 -->
                <MkAction
                  v-if="perm.model.share.modify()"
                  :label="t('common.actions.edit')"
                  icon="icon_edit_outlined"
                  @click="handleOpenEditModel(model)"
                />
                <!-- 模型参数设置 -->
                <ParamSettingAction
                  v-if="model.model_type !== 'RERANKER' && perm.model.share.paramSetting()"
                  :label="t('model.actions.parameters')"
                  :api="SystemSharedModelApi"
                  :model="model"
                />
                <!-- 授权工作空间 -->
                <AuthorizedWorkspaceAction
                  v-if="perm.model.share.authToWorkspace()"
                  :label="t('resource.workspaceAuthorization.title')"
                  :resource="model"
                  :resource-type="RESOURCE_TYPE.MODEL"
                />

                <!-- 查看关联资源 -->
                <RelatedResourcesModelAction
                  v-if="perm.model.share.relateMap()"
                  :label="t('resource.relations.title')"
                  :api="RelatedResourcesApi"
                  :model="model"
                />

                <!-- 删除 -->
                <DeleteModelAction
                  v-if="perm.model.share.delete()"
                  :label="t('common.actions.delete')"
                  :api="SystemSharedModelApi"
                  :model="model"
                  @refresh="loadModels"
                />
              </template>
            </ModelCard>
          </template>
        </div>
        <MkEmpty v-else class="mt-24" />
      </div>
    </template>
  </MkViewLayout>
  <EditModelDrawer
    v-if="editDrawerMounted"
    ref="editModelDrawerRef"
    :api="SystemSharedModelApi"
    @closed="editDrawerMounted = false"
    @refresh="loadModels"
  />
</template>
