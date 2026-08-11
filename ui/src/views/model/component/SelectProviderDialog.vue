<template>
  <el-dialog
    v-model="dialogVisible"
    width="560px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
    append-to-body
  >
    <template #header>
      <div class="flex items-center justify-between">
        <h4 class="m-0">选择供应商</h4>
        <el-dropdown>
          <span class="cursor-pointer flex items-center gap-1">
            {{ currentModelType || '全部模型' }}
            <el-icon><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="item in modelTypeOptions"
                :key="item.value"
                @click="checkModelType(item.value)"
              >
                <span>{{ item.text }}</span>
                <el-icon v-if="currentModelType === item.text" class="ml-2"><Check /></el-icon>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </template>
    <el-row :gutter="12" v-loading="loading">
      <el-col :span="12" class="mb-4" v-for="(data, index) in list_provider" :key="index">
        <el-card shadow="hover" class="provider-card" @click="goCreate(data)">
          <div class="flex items-center cursor-pointer">
            <span v-html="data.icon" class="w-6 h-6 mr-2 shrink-0" />
            <span>{{ data.name }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ProviderApi from '@/api/model/provider'
import type { Provider } from '@/api/type/model'
import { modelTypeList } from './data'

const loading = ref(false)
const dialogVisible = ref(false)
const list_provider = ref<Provider[]>([])
const currentModelType = ref('')
const selectModelType = ref('')

const modelTypeOptions = [
  { text: '全部模型', value: '' },
  ...modelTypeList,
]

const emit = defineEmits<{
  (e: 'change', provider: Provider, model_type?: string): void
}>()

function open(model_type?: string) {
  dialogVisible.value = true
  checkModelType(model_type || '')
}

function close() {
  dialogVisible.value = false
}

function checkModelType(model_type: string) {
  selectModelType.value = model_type
  currentModelType.value = modelTypeOptions.find(item => item.value === model_type)?.text || '全部模型'
  ProviderApi.getProviderByModelType(model_type, loading).then((ok) => {
    list_provider.value = ok.data
    list_provider.value.sort((a, b) => a.provider.localeCompare(b.provider))
  })
}

function goCreate(provider: Provider) {
  close()
  emit('change', provider, selectModelType.value)
}

defineExpose({ open, close })
</script>

<style lang="scss" scoped>
.provider-card {
  cursor: pointer;
  &:hover {
    border-color: var(--el-color-primary);
  }
}
</style>
