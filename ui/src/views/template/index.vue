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
      <div class="template-manage__right p-24">
        <h4>全部模型</h4>
        <card-box :title="model.name" v-for="model in model_list">
          <template #icon>
            <AppAvatar
              class="mr-12"
              shape="square"
              style="--el-avatar-bg-color: rgba(255, 255, 255, 0)"
              :size="32"
            >
              <span style="height: 24px; width: 24px" :innerHTML="get_model_icon(model)"></span
            ></AppAvatar>
          </template>
          <template #description>
            {{ model.model_type }}
            {{ model.model_name }}
          </template>
        </card-box>
      </div>
    </div>
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, watch } from 'vue'
import ModelApi from '@/api/model'
import type { Provider, Model } from '@/api/type/model'
import AppIcon from '@/components/icons/AppIcon.vue'
const loading = ref<boolean>(false)

const active_provider = ref<Provider>()

const provider_list = ref<Array<Provider>>([])
const get_model_icon = (model: Model) => {
  return provider_list.value.find((p) => p.provider === model.provider)?.icon
}
const model_list = ref<Array<Model>>([])
watch(
  active_provider,
  () => {
    ModelApi.getModel(
      active_provider.value ? { provider: active_provider.value.provider } : {}
    ).then((ok) => {
      model_list.value = ok.data
    })
  },
  {
    immediate: true
  }
)
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
}
</style>
