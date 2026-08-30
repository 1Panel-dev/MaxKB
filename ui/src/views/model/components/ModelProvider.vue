<script setup lang="ts">
import { computed } from 'vue'
import type { ModelProviderItem } from '@/api/types'
import { isWorkspaceResource } from '@/utils/resource-context'

defineOptions({ name: 'ModelProvider' })

const ALL_MODEL_PROVIDER: ModelProviderItem = { icon: '', name: '全部模型', provider: 'all' }
const SHARED_MODEL_PROVIDER: ModelProviderItem = { icon: '', name: '共享模型', provider: 'shared' }

const LOCAL_PROVIDER_IDS = new Set(['model_docker_ai_provider', 'model_local_provider', 'model_ollama_provider', 'model_vllm_provider', 'model_xinference_provider'])

const props = defineProps<{ modelValue: ModelProviderItem; providers: ModelProviderItem[] }>()
const emit = defineEmits<{ 'update:modelValue': [value: ModelProviderItem] }>()

const publicProviders = computed(() => props.providers.filter(({ provider }) => !LOCAL_PROVIDER_IDS.has(provider)))
const privateProviders = computed(() => props.providers.filter(({ provider }) => LOCAL_PROVIDER_IDS.has(provider)))

function handleProviderSelect(provider: ModelProviderItem) {
  emit('update:modelValue', provider)
}
</script>

<template>
  <div class="px-4">
    <template v-if="isWorkspaceResource()">
      <MkListItem class="-mt-2" :active="modelValue.provider === SHARED_MODEL_PROVIDER.provider" @click="handleProviderSelect(SHARED_MODEL_PROVIDER)">
        <MkIcon :name="modelValue.provider === SHARED_MODEL_PROVIDER.provider ? 'icon_folder-share_filled' : 'icon_folder_outlined'" :size="18" class="mr-2" />
        <span>共享模型</span>
      </MkListItem>

      <el-divider class="my-1!" />
    </template>

    <MkListItem :active="modelValue.provider === ALL_MODEL_PROVIDER.provider" @click="handleProviderSelect(ALL_MODEL_PROVIDER)">
      <MkIcon :name="modelValue.provider === ALL_MODEL_PROVIDER.provider ? 'icon_card_filled' : 'icon_card_outlined'" :size="18" class="mr-2" />
      <span>全部模型</span>
    </MkListItem>
  </div>

  <el-scrollbar class="min-h-0 flex-1 px-4 pb-4">
    <div class="mt-1">
      <MkCollapse v-if="publicProviders.length" :default-expanded="false" triggerClass="hover:bg-N900/10 rounded-md py-[9px] px-2 mb-1">
        <template #label>
          <MkIcon name="icon_file-folder_colorful" :size="18" />
          <span>公有模型</span>
        </template>
        <div class="flex flex-col gap-1">
          <MkListItem v-for="item in publicProviders" :key="item.provider" :active="modelValue.provider === item.provider" @click="handleProviderSelect(item)">
            <span class="ml-8.5 h-5 w-5" :innerHTML="item.icon" />
            <span class="ml-2 min-w-0 flex-1 truncate" :title="item.name">
              {{ item.name }}
            </span>
          </MkListItem>
        </div>
      </MkCollapse>

      <MkCollapse v-if="privateProviders.length" :default-expanded="false" triggerClass="hover:bg-N900/10 rounded-md py-[9px] px-2 mb-1">
        <template #label>
          <MkIcon name="icon_file-folder_colorful" :size="18" />
          <span>私有模型</span>
        </template>
        <div class="flex flex-col gap-1">
          <MkListItem v-for="item in privateProviders" :key="item.provider" :active="modelValue.provider === item.provider" @click="handleProviderSelect(item)">
            <span class="ml-8.5 h-5 w-5" :innerHTML="item.icon" />
            <span class="ml-2 min-w-0 flex-1 truncate" :title="item.name">
              {{ item.name }}
            </span>
          </MkListItem>
        </div>
      </MkCollapse>
    </div>
  </el-scrollbar>
</template>
