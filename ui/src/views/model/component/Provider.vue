<template>
  <div class="provider-list">
    <el-scrollbar>
      <div class="p-8">
        <div v-if="showShared && hasPermission(EditionConst.IS_EE, 'OR')" class="border-b mb-4">
          <div
            @click="handleSharedNodeClick"
            class="shared-button flex cursor"
            :class="active?.provider === 'share' && 'active'"
          >
            <AppIcon
              iconName="app-shared-active"
              style="font-size: 18px"
              class="color-primary"
            ></AppIcon>
            <span class="ml-8">{{ $t('views.shared.shared_model') }}</span>
          </div>
        </div>
        <div
          class="all-mode flex cursor"
          @click="clickListHandle(allObj as Provider)"
          :class="!active?.provider ? 'all-mode-active color-primary-1' : ''"
        >
          <AppIcon
            class="mr-8 color-primary"
            style="height: 20px; width: 20px"
            :iconName="'app-all-menu-active'"
          ></AppIcon>
          <span>{{ $t('views.model.modelType.allModel') }}</span>
        </div>

        <el-collapse class="model-collapse" expand-icon-position="left">
          <el-collapse-item
            :title="$t('views.model.modelType.publicModel')"
            name="1"
            icon="CaretRight"
          >
            <template #title>
              <div class="flex align-center">
                <AppIcon iconName="app-folder" style="font-size: 20px"></AppIcon>
                <span class="ml-8">
                  {{ $t('views.model.modelType.publicModel') }}
                </span>
              </div>
            </template>
            <common-list
              :data="online_provider_list"
              v-loading="loading"
              @click="clickListHandle"
              value-key="provider"
              default-active=""
              ref="commonList1"
            >
              <template #default="{ row }">
                <div class="flex align-center">
                  <span
                    :innerHTML="row.icon"
                    alt=""
                    style="height: 20px; width: 20px"
                    class="mr-8"
                  />
                  <span class="ellipsis-1" :title="row.name">{{ row.name }}</span>
                </div>
              </template>
            </common-list>
          </el-collapse-item>
          <el-collapse-item
            :title="$t('views.model.modelType.privateModel')"
            name="2"
            icon="CaretRight"
          >
            <template #title>
              <div class="flex align-center">
                <AppIcon iconName="app-folder" style="font-size: 20px"></AppIcon>
                <span class="ml-8">
                  {{ $t('views.model.modelType.privateModel') }}
                </span>
              </div>
            </template>
            <common-list
              :data="local_provider_list"
              v-loading="loading"
              @click="clickListHandle"
              value-key="provider"
              default-active=""
              ref="commonList2"
            >
              <template #default="{ row }">
                <div class="flex align-center">
                  <span
                    :innerHTML="row.icon"
                    alt=""
                    style="height: 20px; width: 20px"
                    class="mr-8"
                  />
                  <span class="ellipsis-1" :title="row.name">{{ row.name }}</span>
                </div>
              </template>
            </common-list>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-scrollbar>
  </div>
</template>
<script lang="ts" setup>
import { watch, ref } from 'vue'
import type { Provider, Model } from '@/api/type/model'
import { modelTypeList, allObj } from '@/views/model/component/data'
import { EditionConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import { t } from '@/locales'
const props = defineProps<{
  data: Array<Provider>
  loading: boolean
  showShared?: boolean
  active?: Provider
}>()
const emit = defineEmits(['click'])

const online_provider_list = ref<Array<Provider>>([])
const local_provider_list = ref<Array<Provider>>([])

watch(
  () => props.data,
  (list) => {
    const local_provider = [
      'model_ollama_provider',
      'model_local_provider',
      'model_xinference_provider',
      'model_vllm_provider',
    ]
    list
      .filter((v) => v.provider)
      ?.forEach((item) => {
        if (local_provider.indexOf(item.provider) > -1) {
          local_provider_list.value.push(item)
        } else {
          online_provider_list.value.push(item)
        }
      })
    online_provider_list.value.sort((a, b) => a.provider.localeCompare(b.provider))
    local_provider_list.value.sort((a, b) => a.provider.localeCompare(b.provider))
  },
  { immediate: true },
)

const clickListHandle = (item: Provider) => {
  emit('click', item)
}

const handleSharedNodeClick = () => {
  emit('click', { provider: 'share', name: t('views.shared.shared_model') })
}
</script>
<style lang="scss" scoped>
.provider-list {
  height: calc(var(--app-main-height));
  .all-mode {
    padding: 10px 8px;
    font-weight: 400;
    &:hover {
      border-radius: var(--app-border-radius-small);
      background: var(--app-text-color-light-1);
    }
  }
  .all-mode-active {
    border-radius: var(--app-border-radius-small);
    color: var(--el-color-primary);
    font-weight: 500 !important;
    background: var(--el-color-primary-light-9);
    &:hover {
      background: var(--el-color-primary-light-9);
    }
  }
  .model-collapse {
    border-top: none !important;
    border-bottom: none !important;
    :deep(.el-collapse-item__header) {
      border-bottom: none !important;
      padding-left: 8px;
      font-size: 14px;
      font-weight: 400;
      height: 40px;
      background: none;
      &:hover {
        background: var(--app-text-color-light-1);
        border-radius: var(--app-border-radius-small);
      }
    }
    :deep(.el-collapse-item) {
      margin-top: 2px;
    }
    :deep(.common-list) {
      li {
        padding-left: 50px !important;
      }
    }
    :deep(.el-collapse-item__wrap) {
      border-bottom: none !important;
      background: none !important;
    }
    :deep(.el-collapse-item__content) {
      padding-bottom: 0 !important;
    }
  }
  .shared-button {
    padding: 10px 8px;
    font-weight: 400;
    font-size: 14px;
    margin-bottom: 4px;
    &.active {
      background: var(--el-color-primary-light-9);
      border-radius: var(--app-border-radius-small);
      color: var(--el-color-primary);
      font-weight: 500;
      &:hover {
        background: var(--el-color-primary-light-9);
      }
    }
    &:hover {
      border-radius: var(--app-border-radius-small);
      background: var(--app-text-color-light-1);
    }
    &.is-active {
      &:hover {
        color: var(--el-color-primary);
        background: var(--el-color-primary-light-9);
      }
    }
  }
}
</style>
