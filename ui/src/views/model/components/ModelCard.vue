<script setup lang="ts">
import type { WorkspaceModel } from '@/api/types'
import { MODEL_STATUS } from '@/api/enums'
import { MODEL_TYPE_LABELS } from '@/constants'
import MkSourceCard from '@/components/mk-source-card/index.vue'

defineOptions({ name: 'ModelCard' })

const props = defineProps<{
  icon: string
  model: WorkspaceModel
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
</script>

<template>
  <MkSourceCard
    :title="model.name"
    :nick_name="model.nick_name || '-'"
    :create_time="model.create_time"
  >
    <template #icon>
      <span class="block h-6 w-6" :innerHTML="icon" />
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
      <el-tag v-if="props.shared" size="small" type="info" class="text-N600!">共享</el-tag>
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

    <template #footer="{ Action, ActionDropdown }">
      <component :is="Action" v-if="!props.shared">
        <component :is="ActionDropdown">
          <MkDropdownMenu>
            <MkDropdownItem>
              <template #icon><MkIcon name="icon_edit_outlined" /></template>
              <span>编辑</span>
            </MkDropdownItem>
            <MkDropdownItem>
              <template #icon><MkIcon name="icon_preferences_outlined" /></template>
              <span>模型参数设置</span>
            </MkDropdownItem>
            <MkDropdownItem>
              <template #icon><MkIcon name="icon_passkeys_outlined" /></template>
              <span>资源授权</span>
            </MkDropdownItem>
            <MkDropdownItem divided>
              <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
              <span>删除</span>
            </MkDropdownItem>
          </MkDropdownMenu>
        </component>
      </component>
    </template>
  </MkSourceCard>
</template>
