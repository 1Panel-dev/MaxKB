<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'

import type { ModelItem, ModelProviderItem } from '@/api/types'
import { MODEL_STATUS } from '@/api/enums'
import { MODEL_TYPE_LABELS } from '@/constants'
import MkSourceCard from '@/components/mk-source-card/index.vue'
import EditModelDrawer from '../EditModelDrawer.vue'
import ParamSettingDrawer from '../ParamSettingDrawer.vue'
import ModelDownloadStatus from './ModelDownloadStatus.vue'

defineOptions({ name: 'ModelCard' })

const props = defineProps<{
  model: ModelItem
  provider: ModelProviderItem
  refresh: () => Promise<void>
  shared: boolean
}>()

const errMessage = computed(() => {
  if (props.model.meta?.message) {
    if (props.model.meta.message === 'pull model manifest: file does not exist') {
      return `${props.model.model_name} 模型在 Ollama 不存在`
    }
    return props.model.meta.message
  }
  return ''
})

/* 编辑 */
const editModelDrawerRef =
  useTemplateRef<InstanceType<typeof EditModelDrawer>>('editModelDrawerRef')

function handleOpenEditModel() {
  editModelDrawerRef.value?.open(props.provider, props.model)
}

/* 模型参数设置 */
const paramSettingDrawerRef =
  useTemplateRef<InstanceType<typeof ParamSettingDrawer>>('paramSettingDrawerRef')

function handleOpenParamSetting() {
  paramSettingDrawerRef.value?.open(props.model)
}
</script>

<template>
  <MkSourceCard
    class="relative overflow-hidden"
    :title="model.name"
    :nick_name="model.nick_name || '-'"
    :create_time="model.create_time"
  >
    <template #icon>
      <span class="block h-6 w-6" :innerHTML="provider.icon" />
    </template>
    <template #title="{ title }">
      <h6 class="min-w-0 truncate" :title="title">{{ title }}</h6>

      <el-tooltip :content="errMessage" v-if="model.status === MODEL_STATUS.ERROR">
        <MkIcon name="icon_warning_filled" class="text-danger!" />
      </el-tooltip>
      <el-tooltip
        v-if="model.status === MODEL_STATUS.PAUSE_DOWNLOAD"
        :content="`基础模型: ${model.model_name} 下载失败`"
      >
        <MkIcon name="icon_warning_filled" type="danger" />
      </el-tooltip>
    </template>
    <template #tag>
      <el-tag v-if="props.shared" size="small" type="info">共享</el-tag>
    </template>

    <ul class="flex flex-col gap-2">
      <li class="flex gap-4">
        <span class="shrink-0">模型类型</span>
        <span
          class="min-w-0 flex-1 truncate text-N900"
          :title="MODEL_TYPE_LABELS[model.model_type] ?? model.model_type"
        >
          {{ MODEL_TYPE_LABELS[model.model_type] ?? model.model_type }}
        </span>
      </li>
      <li class="flex gap-4">
        <span class="shrink-0">基础模型</span>
        <span class="min-w-0 flex-1 truncate text-N900" :title="model.model_name">
          {{ model.model_name }}
        </span>
      </li>
    </ul>
    <!-- 下载状态 -->
    <ModelDownloadStatus
      v-if="model.status === MODEL_STATUS.DOWNLOAD"
      :model="model"
      :refresh="refresh"
    />

    <template #footer="{ Action, ActionDropdown }">
      <component :is="Action" v-if="!shared">
        <component :is="ActionDropdown">
          <MkDropdownItem @click="handleOpenEditModel">
            <template #icon><MkIcon name="icon_edit_outlined" /></template>
            <span>编辑</span>
          </MkDropdownItem>
          <MkDropdownItem @click="handleOpenParamSetting" v-if="model.model_type !== 'RERANKER'">
            <template #icon><MkIcon name="icon_preferences_outlined" /></template>
            <span>模型参数设置</span>
          </MkDropdownItem>
          <MkDropdownItem>
            <template #icon><MkIcon name="icon_passkeys_outlined" /></template>
            <span>资源授权</span>
          </MkDropdownItem>
          <MkDropdownItem>
            <template #icon><MkIcon name="icon_passkeys_outlined" /></template>
            <span>查看关联资源</span>
          </MkDropdownItem>
          <MkDropdownItem divided>
            <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
            <span>删除</span>
          </MkDropdownItem>
        </component>
      </component>
    </template>
  </MkSourceCard>
  <EditModelDrawer v-if="!shared" ref="editModelDrawerRef" @refresh="refresh" />
  <ParamSettingDrawer v-if="!shared" ref="paramSettingDrawerRef" />
</template>
