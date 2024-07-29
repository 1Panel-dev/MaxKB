<template>
  <LayoutContainer header="模型设置">
    <div class="template-manage flex main-calc-height">
      <div class="template-manage__left p-8 border-r">
        <h4 class="p-16" style="padding-bottom: 8px">供应商</h4>
        <common-list
          :data="provider_list"
          v-loading="loading"
          @click="clickListHandle"
          value-key="provider"
          default-active=""
        >
          <template #default="{ row, index }">
            <div class="flex" v-if="index === 0">
              <AppIcon
                class="mr-8"
                style="height: 20px; width: 20px"
                :iconName="active_provider === row ? 'app-all-menu-active' : 'app-all-menu'"
              ></AppIcon>
              <span>全部模型</span>
            </div>
            <div class="flex" v-else>
              <span :innerHTML="row.icon" alt="" style="height: 20px; width: 20px" class="mr-8" />
              <span>{{ row.name }}</span>
            </div>
          </template>
        </common-list>
      </div>
      <div class="template-manage__right w-full" v-loading="list_model_loading">
        <div class="p-24 pb-0">
          <h4>{{ active_provider?.name }}</h4>
          <div class="flex-between mt-16 mb-16">
            <el-button type="primary" @click="openCreateModel(active_provider)">添加模型</el-button>
            <el-input
              v-model="model_search_form.name"
              @change="list_model"
              placeholder="按名称搜索"
              prefix-icon="Search"
              style="max-width: 240px"
              clearable
            />
          </div>
        </div>
        <div class="model-list-height">
          <el-scrollbar>
            <div class="p-24 pt-0">
              <el-row v-if="model_split_list.length > 0" :gutter="15">
                <template v-for="row in model_split_list" :key="row.id">
                  <el-col
                    :xs="24"
                    :sm="24"
                    :md="24"
                    :lg="12"
                    :xl="12"
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
              <el-empty description="暂无数据" v-else />
            </div>
          </el-scrollbar>
        </div>
      </div>
    </div>
    <CreateModelDialog
      ref="createModelRef"
      @submit="list_model"
      @change="openCreateModel($event)"
    ></CreateModelDialog>

    <SelectProviderDialog
      ref="selectProviderRef"
      @change="openCreateModel($event)"
    ></SelectProviderDialog>
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, computed } from 'vue'
import ModelApi from '@/api/model'
import type { Provider, Model } from '@/api/type/model'
import AppIcon from '@/components/icons/AppIcon.vue'
import ModelCard from '@/views/template/component/ModelCard.vue'
import { splitArray } from '@/utils/common'
import CreateModelDialog from '@/views/template/component/CreateModelDialog.vue'
import SelectProviderDialog from '@/views/template/component/SelectProviderDialog.vue'

const allObj = {
  icon: '',
  provider: '',
  name: '全部模型'
}

const loading = ref<boolean>(false)

const active_provider = ref<Provider>()
const model_search_form = ref<{ name: string }>({ name: '' })
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
}

const openCreateModel = (provider?: Provider) => {
  if (provider && provider.provider) {
    createModelRef.value?.open(provider)
  } else {
    selectProviderRef.value?.open()
  }
}

const list_model = () => {
  const params = active_provider.value?.provider ? { provider: active_provider.value.provider } : {}
  ModelApi.getModel({ ...model_search_form.value, ...params }, list_model_loading).then((ok) => {
    model_list.value = ok.data
  })
}

onMounted(() => {
  ModelApi.getProvider(loading).then((ok) => {
    active_provider.value = allObj
    provider_list.value = [allObj, ...ok.data]
    list_model()
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

  .model-list-height {
    height: calc(var(--create-dataset-height) - 70px);
  }
}
</style>
