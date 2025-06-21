<template>
  <div class="model-shared">
    <ContentContainer
        :header="t('views.system.share_model')"
        v-loading="list_model_loading"
      >
        <template #search>
          <div class="flex">
            <div class="flex-between complex-search">
              <el-select
                class="complex-search__left"
                v-model="search_type"
                style="width: 120px"
                @change="search_type_change"
              >
                <el-option :label="$t('common.creator')" value="create_user" />

                <el-option
                  :label="$t('views.model.modelForm.model_type.label')"
                  value="model_type"
                />
                <el-option :label="$t('views.model.modelForm.modeName.label')" value="name" />
              </el-select>
              <el-input
                v-if="search_type === 'name'"
                v-model="model_search_form.name"
                @change="list_model"
                :placeholder="$t('common.searchBar.placeholder')"
                style="width: 220px"
                clearable
              />
              <el-select
                v-else-if="search_type === 'create_user'"
                v-model="model_search_form.create_user"
                @change="list_model"
                clearable
                style="width: 220px"
              >
                <el-option
                  v-for="u in user_options"
                  :key="u.id"
                  :value="u.id"
                  :label="u.username"
                />
              </el-select>

              <el-select
                v-else-if="search_type === 'model_type'"
                v-model="model_search_form.model_type"
                clearable
                @change="list_model"
                style="width: 220px"
              >
                <template v-for="item in modelTypeList" :key="item.value">
                  <el-option :label="item.text" :value="item.value" />
                </template>
              </el-select>
            </div>
          </div>
        </template>

        <div class="model-list-height">
          <el-scrollbar>
            <el-row v-if="model_split_list.length > 0" :gutter="15" class="w-full">
              <template v-for="(row, index) in model_split_list" :key="index">
                <el-col
                  :xs="24"
                  :sm="12"
                  :md="12"
                  :lg="8"
                  :xl="6"
                  class="mb-16"
                  v-for="(model, i) in row"
                  :key="i"
                >
                  <ModelCard
                    @change="list_model"
                    :updateModelById="updateModelById"
                    :model="model"
                    :provider_list="provider_list"
                  >
                  </ModelCard>
                </el-col>
              </template>
            </el-row>
            <el-empty :description="$t('common.noData')" v-else />
          </el-scrollbar>
        </div>
      </ContentContainer>

      <CreateModelDialog
        ref="createModelRef"
        @submit="list_model"
        @change="openCreateModel($event)"
      ></CreateModelDialog>

      <SelectProviderDialog
        ref="selectProviderRef"
        @change="(provider, modelType) => openCreateModel(provider, modelType)"
      ></SelectProviderDialog>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, computed } from 'vue'
import ProviderApi from '@/api/model/provider'
import ModelApi from '@/api/system-shared/model'
import ModelWorkspaceApi from '@/api/shared-workspace'
import type { Provider, Model } from '@/api/type/model'
import ModelCard from '@/views/shared/model-shared/component/ModelCardSharedWorkspace.vue'
import ProviderComponent from '@/views/shared/model-shared/component/Provider.vue'
import { splitArray } from '@/utils/common'
import { modelTypeList, allObj } from '@/views/shared/model-shared/component/data'
import CreateModelDialog from '@/views/shared/model-shared/component/CreateModelDialog.vue'
import iconMap from '@/components/app-icon/icons/common'
import SelectProviderDialog from '@/views/shared/model-shared/component/SelectProviderDialog.vue'
import useStore from '@/stores/modules-shared-system'
import { t } from '@/locales'

const { model } = useStore()
const rightOutlined = iconMap['right-outlined'].iconReader()

const commonList1 = ref()
const commonList2 = ref()
const loading = ref<boolean>(false)

const active_provider = ref<Provider>()
const search_type = ref('name')
const model_search_form = ref<{
  name: string
  create_user: string
  model_type: string
}>({
  name: '',
  create_user: '',
  model_type: '',
})
const user_options = ref<any[]>([])
const list_model_loading = ref<boolean>(false)
const provider_list = ref<Array<Provider>>([])

const model_list = ref<Array<Model>>([])

const updateModelById = (model_id: string, model: Model) => {
  model_list.value
    .filter((m) => m.id == model_id)
    .forEach((m) => {
      m.status = model.status
    })
}
const model_split_list = computed(() => {
  return splitArray(model_list.value, 2)
})
const createModelRef = ref<InstanceType<typeof CreateModelDialog>>()
const selectProviderRef = ref<InstanceType<typeof SelectProviderDialog>>()

const clickListHandle = (item: Provider) => {
  active_provider.value = item
  list_model()
  if (active_provider.value.provider === '') {
    commonList1.value.clearCurrent()
    commonList2.value.clearCurrent()
  }
}

const openCreateModel = (provider?: Provider, model_type?: string) => {
  if (provider && provider.provider) {
    createModelRef.value?.open(provider, model_type)
  } else {
    selectProviderRef.value?.open()
  }
}

const list_model = () => {
  const params = active_provider.value?.provider ? { provider: active_provider.value.provider } : {}
  ModelWorkspaceApi
    .getSharedWorkspaceModelPage({ ...model_search_form.value, ...params }, list_model_loading)
    .then((ok: any) => {
      model_list.value = ok.data
      const v = model_list.value.map((m) => ({ id: m.user_id, username: m.username }))
      if (user_options.value.length === 0) {
        user_options.value = Array.from(new Map(v.map((item) => [item.id, item])).values())
      }
    })
}

const search_type_change = () => {
  model_search_form.value = { name: '', create_user: '',  model_type: '' }
}

onMounted(() => {
  ProviderApi.getProvider(loading).then((ok) => {
    active_provider.value = allObj
    provider_list.value = [allObj, ...ok.data]

    list_model()
  })
})
</script>

<style lang="scss" scoped>
.model-shared {
  height: 100%;

  .shared-header {
    color: #646a73;
    font-weight: 400;
    font-size: 14px;
    line-height: 22px;
    display: flex;
    align-items: center;
    margin-bottom: 21px;

    :deep(.el-icon i) {
      height: 12px;
    }

    .sub-title {
      color: #1f2329;
    }
  }

  .h-full {
    border-radius: 8px;
    box-shadow: 0px 2px 4px 0px #1f23291f;
    background: #fff;
  }
}
</style>
