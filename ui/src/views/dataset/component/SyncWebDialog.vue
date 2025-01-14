<template>
  <el-dialog
    :title="$t('views.dataset.syncWeb.title')"
    v-model="dialogVisible"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
  >
    <p class="mb-8">{{ $t('views.dataset.syncWeb.syncMethod') }}</p>
    <el-radio-group v-model="method" class="card__radio">
      <el-card shadow="never" class="mb-16" :class="method === 'replace' ? 'active' : ''">
        <el-radio value="replace" size="large">
          <p class="mb-4">{{ $t('views.dataset.syncWeb.replace') }}</p>
          <el-text type="info">{{ $t('views.dataset.syncWeb.replaceText') }}</el-text>
        </el-radio>
      </el-card>

      <el-card shadow="never" class="mb-16" :class="method === 'complete' ? 'active' : ''">
        <el-radio value="complete" size="large">
          <p class="mb-4">{{ $t('views.dataset.syncWeb.complete') }}</p>
          <el-text type="info">{{ $t('views.dataset.syncWeb.completeText') }}</el-text>
        </el-radio>
      </el-card>
    </el-radio-group>
    <p class="danger">{{ $t('views.dataset.syncWeb.tip') }}</p>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit" :loading="loading">
          {{ $t('common.confirm') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'

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
  dataset.asyncSyncDataset(datasetId.value, method.value, loading).then((res: any) => {
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
