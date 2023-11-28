<template>
  <el-dialog
    v-model="dialogVisible"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
  >
    <template #header="{ close, titleId, titleClass }">
      <el-breadcrumb separator=">">
        <el-breadcrumb-item>
          <span class="active-breadcrumb">选择供应商</span>
        </el-breadcrumb-item>
      </el-breadcrumb>
    </template>
    <RadioCard class="mb-8" :data_list="list_provider" @update:model-value="go_create"
      ><template #default="scope">
        <div class="center">
          <span
            :innerHTML="scope.icon"
            alt=""
            style="display: inline-block; height: 24px; width: 24px"
            class="mr-8"
          />
          <span>{{ scope.name }}</span>
        </div>
      </template></RadioCard
    >
  </el-dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import ModelApi from '@/api/model'
import type { Provider } from '@/api/type/model'
import RadioCard from '@/views/template/component/RadioCard.vue'
const loading = ref<boolean>(false)
const dialogVisible = ref<boolean>(false)
const list_provider = ref<Array<Provider>>([])

const open = () => {
  dialogVisible.value = true
  ModelApi.getProvider(loading).then((ok) => {
    list_provider.value = ok.data
  })
}

const close = () => {
  dialogVisible.value = false
}
const emit = defineEmits(['change'])
const go_create = (provider: Provider) => {
  close()
  emit('change', provider)
}
defineExpose({ open, close })
</script>
<style lang="scss" scoped>
.active-breadcrumb {
  font-size: 16px;
  color: rgba(31, 35, 41, 1);
  font-weight: 500;
  line-height: 24px;
}
.center {
  display: flex;
  align-items: center;
  cursor: pointer;
}
</style>
