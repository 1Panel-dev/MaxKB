<template>
  <el-dialog
    title="同步知识库"
    v-model="dialogVisible"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
  >
    <p class="mb-8">同步方式</p>
    <el-radio-group v-model="method" class="card__radio">
      <el-card shadow="never" class="mb-16" :class="method === 'replace' ? 'active' : ''">
        <el-radio value="replace" size="large">
          <p class="mb-4">替换同步</p>
          <el-text type="info">重新获取 Web 站点文档，覆盖替换本地知识库中的文档</el-text>
        </el-radio>
      </el-card>

      <el-card shadow="never" class="mb-16" :class="method === 'complete' ? 'active' : ''">
        <el-radio value="complete" size="large">
          <p class="mb-4">整体同步</p>
          <el-text type="info">先删除本地知识库所有文档，重新获取 Web 站点文档</el-text>
        </el-radio>
      </el-card>
    </el-radio-group>
    <p class="danger">注意：所有同步都会删除已有数据重新获取新数据，请谨慎操作。</p>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submit" :loading="loading"> 确定 </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'

import { MsgSuccess } from '@/utils/message'

import useStore from '@/stores'
const { dataset } = useStore()

const emit = defineEmits(['refresh'])
const loading = ref<boolean>(false)
const method = ref('replace')
const datasetId = ref('')

const dialogVisible = ref<boolean>(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    method.value = 'replace'
  }
})

const open = (id: string) => {
  datasetId.value = id
  dialogVisible.value = true
}

const submit = () => {
  dataset.asyncSyncDateset(datasetId.value, method.value, loading).then((res: any) => {
    emit('refresh', res.data)
    dialogVisible.value = false
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped>
.select-provider {
  font-size: 16px;
  color: rgba(100, 106, 115, 1);
  font-weight: 400;
  line-height: 24px;
  cursor: pointer;
  &:hover {
    color: var(--el-color-primary);
  }
}
.active-breadcrumb {
  font-size: 16px;
  color: rgba(31, 35, 41, 1);
  font-weight: 500;
  line-height: 24px;
}
</style>
