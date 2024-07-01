<template>
  <el-dialog
    v-model="dialogVisible"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
    title="选择供应商"
    append-to-body
  >
    <el-row :gutter="12" v-loading="loading">
      <el-col :span="12" class="mb-16" v-for="(data, index) in list_provider" :key="index">
        <el-card shadow="hover" @click="go_create(data)">
          <div class="flex align-center cursor">
            <span :innerHTML="data.icon" alt="" style="height: 24px; width: 24px" class="mr-8" />
            <span>{{ data.name }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import ModelApi from '@/api/model'
import type { Provider } from '@/api/type/model'
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
<style lang="scss" scoped></style>
