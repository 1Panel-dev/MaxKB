<template>
  <LayoutContainer header="模版管理">
    <div class="template-manage flex main-calc-height">
      <div class="template-manage__left p-8 border-r">
        <h4 class="p-16">供应商</h4>
        <common-list :data="list" class="mt-8" v-loading="loading" @click="clickHandle">
          <template #default="{ row }">
            <div class="flex">
              <img src="@/assets/icon_document.svg" alt="" class="mr-8" />
              <span>{{ row.name }}</span>
            </div>
          </template>
        </common-list>
      </div>
      <div class="template-manage__right p-24">
        <h4>全部模型</h4>
        
      </div>
    </div>
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, watch } from 'vue'
const loading = ref(false)
const list = ref([
  {
    name: '1111'
  }
])

function clickHandle(row: any) {}

onMounted(() => {})
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
