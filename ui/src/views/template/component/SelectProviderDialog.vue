<template>
  <el-dialog
    v-model="dialogVisible"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
    append-to-body
  >
    <template #header>
      <div class="flex-between">
        <h4>选择供应商</h4>
        <el-dropdown>
          <span class="el-dropdown-link">
            {{ currentModelType || '全部模型' }}
            <el-icon class="el-icon--right">
              <arrow-down />
            </el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="item in modelTypeOptions"
                :key="item.value"
                @click="checkModelType(item.value)"
              >
                <span>{{ item.text }}</span>
                <el-icon v-if="currentModelType === item.text"><Check /></el-icon>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </template>
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
const currentModelType = ref('')

const modelTypeOptions = ref([
  { text: '全部模型', value: '' },
  { text: '大语言模型', value: 'LLM' },
  { text: '向量模型', value: 'EMBEDDING' },
  { text: '重排模型', value: 'RERANKER' },
  { text: '语音识别', value: 'STT' },
  { text: '语音合成', value: 'TTS' },
  { text: '图片理解', value: 'IMAGE' },
  { text: '图片生成', value: 'TTI' },
])

const open = () => {
  dialogVisible.value = true
  const option = modelTypeOptions.value.find((item) => item.text === currentModelType.value)
  checkModelType(option ? option.value : '')
}

const close = () => {
  dialogVisible.value = false
}

const checkModelType = (model_type: string) => {
  currentModelType.value = modelTypeOptions.value.filter(
    (item) => item.value === model_type
  )[0].text
  ModelApi.getProviderByModelType(model_type, loading).then((ok) => {
    list_provider.value = ok.data
    list_provider.value.sort((a, b) => a.provider.localeCompare(b.provider))
  })
}

const emit = defineEmits(['change'])
const go_create = (provider: Provider) => {
  close()
  emit('change', provider)
}
defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
