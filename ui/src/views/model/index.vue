<template>
  <LayoutContainer showCollapse class="model-manage">
    <template #left>
      <h4 class="p-12-16 pb-0 mt-12">{{ $t('views.model.provider') }}</h4>
      <ProviderComponent
        :data="provider_list"
        @click="clickListHandle"
        :loading="loading"
        :showShared="permissionPrecise['is_share']()"
        :active="active_provider"
      />
    </template>
    <ContentContainer
      :header="active_provider?.name"
      v-loading="list_model_loading"
      style="padding: 0"
    >
      <template #search>
        <div class="flex">
          <div class="complex-search">
            <el-select
              class="complex-search__left"
              v-model="search_type"
              style="width: 120px"
              @change="search_type_change"
            >
              <el-option :label="$t('common.creator')" value="create_user" />
              <el-option :label="$t('views.model.modelForm.model_type.label')" value="model_type" />
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
              filterable
              clearable
              style="width: 220px"
            >
              <el-option v-for="u in user_options" :key="u.id" :value="u.id" :label="u.nick_name" />
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
          <el-button
            v-if="!isShared && permissionPrecise.create()"
            class="ml-16"
            type="primary"
            @click="openCreateModel(active_provider)"
          >
            {{ $t('views.model.addModel') }}
          </el-button>
        </div>
      </template>

      <div class="model-list-height">
        <el-row v-if="model_split_list.length > 0" :gutter="15" class="w-full">
          <template v-for="(row, index) in model_split_list" :key="index">
            <el-col
              :xs="24"
              :sm="12"
              :md="isSystemShare ? 24 : 12"
              :lg="isSystemShare ? 12 : 8"
              :xl="isSystemShare ? 12 : 8"
              class="mb-16"
              v-for="(model, i) in row"
              :key="i"
            >
              <ModelCard
                @change="list_model"
                :updateModelById="updateModelById"
                :model="model"
                :provider_list="provider_list"
                :isShared="isShared"
                :isSystemShare="isSystemShare"
                :apiType="apiType"
              >
              </ModelCard>
            </el-col>
          </template>
        </el-row>
        <el-empty :description="$t('common.noData')" v-else />
      </div>
    </ContentContainer>

    <CreateModelDialog
      ref="createModelRef"
      @submit="list_model"
      @change="openCreateModel($event)"
      v-if="!isShared"
    ></CreateModelDialog>

    <SelectProviderDialog
      ref="selectProviderRef"
      @change="(provider, modelType) => openCreateModel(provider, modelType)"
      v-if="!isShared"
    ></SelectProviderDialog>
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, computed } from 'vue'
import type { Provider, Model } from '@/api/type/model'
import ModelCard from '@/views/model/component/ModelCard.vue'
import ProviderComponent from '@/views/model/component/Provider.vue'
import { splitArray } from '@/utils/array'
import { modelTypeList, allObj } from '@/views/model/component/data'
import CreateModelDialog from '@/views/model/component/CreateModelDialog.vue'
import SelectProviderDialog from '@/views/model/component/SelectProviderDialog.vue'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import useStore from '@/stores'
import { useRoute } from 'vue-router'
import permissionMap from '@/permission'

const route = useRoute()
const { model, user } = useStore()
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const permissionPrecise = computed(() => {
  return permissionMap['model'][apiType.value]
})
const isSystemShare = computed(() => {
  return apiType.value === 'systemShare'
})
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

const isShared = computed(() => {
  return active_provider.value && active_provider.value.provider === 'share'
})
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
    commonList1.value?.clearCurrent()
    commonList2.value?.clearCurrent()
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
  const params = active_provider.value?.provider && active_provider.value?.provider !=='share' ? { provider: active_provider.value.provider } : {}
  loadSharedApi({ type: 'model', isShared: isShared.value, systemType: apiType.value })
    .getModelList({ ...model_search_form.value, ...params }, list_model_loading)
    .then((ok: any) => {
      model_list.value = ok.data
    })
  loadSharedApi({ type: 'workspace', isShared: isShared.value, systemType: apiType.value })
    .getAllMemberList(user.getWorkspaceId(), loading)
    .then((res: any) => {
      user_options.value = res.data
    })
}

const search_type_change = () => {
  model_search_form.value = { name: '', create_user: '', model_type: '' }
}

onMounted(() => {
  model.asyncGetProvider(loading).then((ok: any) => {
    active_provider.value = allObj
    provider_list.value = [allObj, ...ok.data]
    list_model()
  })
})
</script>

<style lang="scss" scoped>
.model-manage {
  .model-list-height {
    height: calc(var(--app-main-height));
    padding-right: 0 !important;
  }
}
</style>
