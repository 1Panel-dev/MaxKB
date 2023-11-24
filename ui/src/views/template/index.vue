<template>
  <LayoutContainer header="模版管理">
    <div class="template-manage flex main-calc-height">
      <div class="template-manage__left p-8 border-r">
        <h4 class="p-16">供应商</h4>
        <common-list :data="provider_list" class="mt-8" v-loading="loading" @click="clickHandle">
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
        <Demo></Demo>
      </div>
    </div>
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, watch } from 'vue'
import ModelApi from '@/api/model'
import type { Provider } from '@/api/type/model'
const loading = ref<boolean>(false)

const provider_list = ref<Array<Provider>>([])

function clickHandle(row: any) {}

onMounted(() => {
  ModelApi.getProvider(loading).then((ok) => {
    provider_list.value = ok.data
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
