<template>
  <LayoutContainer header="模版管理">
    <div class="template-manage flex main-calc-height">
      <div class="template-manage__left p-8 border-r">
        <h4 class="p-16">供应商</h4>
        <common-list
          v-model="active_provider"
          :data="provider_list"
          class="mt-8"
          v-loading="loading"
        >
          <template #prefix>
            <div class="flex">
              <AppIcon
                style="height: 24px; width: 24px"
                class="mr-8"
                :iconName="active_provider ? 'app-all-menu' : 'app-all-menu-active'"
              ></AppIcon>
              <span>全部模型</span>
            </div>
          </template>
          <template #default="{ row }">
            <div class="flex">
              <span :innerHTML="row.icon" alt="" style="height: 24px; width: 24px" class="mr-8" />
              <span>{{ row.name }}</span>
            </div>
          </template>
        </common-list>
      </div>
      <div class="template-manage__right p-24" v-loading="list_model_loading">
        <h3 v-if="active_provider">{{ active_provider.name }}</h3>
        <h3 v-else>全部模型</h3>
        <div class="flex-between mt-8">
          <el-button type="primary" @click="openCreateModel(active_provider)">创建模型</el-button>
          <el-input
            v-model="model_search_form.name"
            @change="list_model"
            placeholder="按 名称 搜索"
            prefix-icon="Search"
            class="w-240"
          />
        </div>

        <el-row :gutter="15" v-for="row in model_split_list">
          <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12" class="mt-8" v-for="model in row">
            <ModelVue @change="list_model" :model="model" :provider_list="provider_list">
            </ModelVue>
          </el-col>
        </el-row>
      </div>
    </div>
    <CreateModel ref="createModelRef" @submit="list_model"></CreateModel>

    <SelectProvider ref="selectProviderRef" @change="openCreateModel($event)"></SelectProvider>
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, computed, watch } from 'vue'
import ModelApi from '@/api/model'
import type { Provider, Model } from '@/api/type/model'

import AppIcon from '@/components/icons/AppIcon.vue'
import ModelVue from '@/views/template/component/Model.vue'
import { splitArray } from '@/utils/common'
import CreateModel from '@/views/template/component/CreateModel.vue'
import SelectProvider from '@/views/template/component/SelectProvider.vue'

const loading = ref<boolean>(false)

const active_provider = ref<Provider>()
const model_search_form = ref<{ name: string }>({ name: '' })
const list_model_loading = ref<boolean>(false)
const provider_list = ref<Array<Provider>>([])

const model_list = ref<Array<Model>>([])

const model_split_list = computed(() => {
  return splitArray(model_list.value, 2)
})
const createModelRef = ref<InstanceType<typeof CreateModel>>()
const selectProviderRef = ref<InstanceType<typeof SelectProvider>>()

const openCreateModel = (provider?: Provider) => {
  if (provider) {
    createModelRef.value?.open(provider)
  } else {
    selectProviderRef.value?.open()
  }
}

const list_model = () => {
  const params = active_provider.value ? { provider: active_provider.value.provider } : {}
  ModelApi.getModel({ ...model_search_form.value, ...params }, list_model_loading).then((ok) => {
    model_list.value = ok.data
  })
}

watch(active_provider, list_model, {
  immediate: true
})

onMounted(() => {
  ModelApi.getProvider(loading).then((ok) => {
    provider_list.value = [...ok.data]
  })
})
</script>

<style lang="scss" scoped>
.template-manage {
  &__left {
    box-sizing: border-box;
    width: var(--setting-left-width);
    min-width: var(--setting-left-width);
  }
  &__right {
    width: 100%;
    overflow: scroll;
  }
}
</style>
