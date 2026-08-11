<template>
  <div class="provider-list">
    <el-scrollbar>
      <div class="p-3">
        <div
          class="all-mode flex cursor px-3 py-2 rounded-md"
          :class="{ 'all-mode-active': !active?.provider }"
          @click="handleClick(allObj)"
        >
          <MkIcon name="icon_all_menu_active" :size="18" class="mr-2 text-primary" />
          <span>全部模型</span>
        </div>

        <el-collapse class="model-collapse" expand-icon-position="left" :model-value="['1', '2']">
          <el-collapse-item title="在线模型" name="1">
            <template #title>
              <div class="flex items-center">
                <MkIcon name="icon_folder" :size="18" />
                <span class="ml-2">在线模型</span>
              </div>
            </template>
            <common-list
              :data="online_provider_list"
              :loading="loading"
              value-key="provider"
              @click="handleClick"
            >
              <template #default="{ row }">
                <div class="flex items-center">
                  <span v-html="row.icon" class="w-4 h-4 mr-2" />
                  <span class="truncate" :title="row.name">{{ row.name }}</span>
                </div>
              </template>
            </common-list>
          </el-collapse-item>
          <el-collapse-item title="本地模型" name="2">
            <template #title>
              <div class="flex items-center">
                <MkIcon name="icon_folder" :size="18" />
                <span class="ml-2">本地模型</span>
              </div>
            </template>
            <common-list
              :data="local_provider_list"
              :loading="loading"
              value-key="provider"
              @click="handleClick"
            >
              <template #default="{ row }">
                <div class="flex items-center">
                  <span v-html="row.icon" class="w-4 h-4 mr-2" />
                  <span class="truncate" :title="row.name">{{ row.name }}</span>
                </div>
              </template>
            </common-list>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Provider } from '@/api/type/model'
import { allObj } from './data'
import CommonList from '@/components/common-list/index.vue'

const localProviders = [
  'model_ollama_provider',
  'model_local_provider',
  'model_xinference_provider',
  'model_vllm_provider',
  'model_docker_ai_provider',
]

const props = defineProps<{
  data: Provider[]
  loading: boolean
  active?: Provider
}>()

const emit = defineEmits<{
  (e: 'click', item: Provider): void
}>()

const online_provider_list = ref<Provider[]>([])
const local_provider_list = ref<Provider[]>([])

watch(() => props.data, (list) => {
  online_provider_list.value = []
  local_provider_list.value = []
  list.filter(v => v.provider).forEach(item => {
    if (localProviders.indexOf(item.provider) > -1) {
      local_provider_list.value.push(item)
    } else {
      online_provider_list.value.push(item)
    }
  })
  online_provider_list.value.sort((a, b) => a.provider.localeCompare(b.provider))
  local_provider_list.value.sort((a, b) => a.provider.localeCompare(b.provider))
}, { immediate: true })

function handleClick(item: Provider) {
  emit('click', item)
}
</script>

<style lang="scss" scoped>
.provider-list {
  height: calc(100vh - 120px);
  :deep(.el-collapse) {
    border-top: none;
    border-bottom: none;
    --el-collapse-header-height: 40px;
    .el-collapse-item__header {
      border-bottom: none;
      padding-left: 8px;
      font-size: 14px;
      font-weight: 400;
      &:hover {
        background: rgba(var(--el-text-color-primary-rgb), 0.06);
        border-radius: 6px;
      }
    }
    .el-collapse-item__wrap {
      border-bottom: none;
      background: none;
    }
    .el-collapse-item__content {
      padding-bottom: 0;
    }
  }
  .all-mode {
    font-weight: 400;
    margin-bottom: 4px;
    &:hover {
      background: rgba(var(--el-text-color-primary-rgb), 0.06);
    }
  }
  .all-mode-active {
    background: var(--el-color-primary-light-9);
    color: var(--el-color-primary);
    font-weight: 500;
    &:hover {
      background: var(--el-color-primary-light-9);
    }
  }
}
</style>
