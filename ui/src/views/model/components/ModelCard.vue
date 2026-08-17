<script setup lang="ts">
import { WarningFilled } from '@element-plus/icons-vue'
import type { WorkspaceModel } from '@/api/types'
import { MODEL_STATUS } from '@/api/types'
import { MODEL_TYPE_LABELS } from '@/constants/model'
import MkSourceCard from '@/components/mk-source-card/index.vue'

defineOptions({ name: 'ModelCard' })

const props = defineProps<{
  icon: string
  model: WorkspaceModel
  shared?: boolean
}>()

function getModelErrorMessage() {
  const message = props.model.meta?.message
  return typeof message === 'string' && message ? message : '模型不可用'
}
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
      <span v-if="model.status === MODEL_STATUS.ERROR" class="shrink-0">
        <el-tooltip effect="dark" :content="getModelErrorMessage()" placement="top">
          <el-icon class="shrink-0 text-danger" :size="18">
            <WarningFilled />
          </el-icon>
        </el-tooltip>
      </span>
      <span v-if="model.status === MODEL_STATUS.PAUSE_DOWNLOAD" class="shrink-0">
        <el-tooltip
          effect="dark"
          :content="`基础模型: ${model.model_name} 下载失败`"
          placement="top"
        >
          <el-icon class="shrink-0 text-danger" :size="18">
            <WarningFilled />
          </el-icon>
        </el-tooltip>
      </span>
    </template>
    <template #tag>
      <el-tag v-if="shared" size="small" type="info" class="text-N600!">共享</el-tag>
    </template>

    <ul class="flex flex-col gap-2">
      <li class="flex gap-4">
        <span class="shrink-0 text-N600">模型类型</span>
        <span
          class="min-w-0 flex-1 truncate"
          :title="MODEL_TYPE_LABELS[model.model_type] ?? model.model_type"
        >
          {{ MODEL_TYPE_LABELS[model.model_type] ?? model.model_type }}
        </span>
      </li>
      <li class="flex gap-4">
        <span class="shrink-0 text-N600">基础模型</span>
        <span class="min-w-0 flex-1 truncate" :title="model.model_name">
          {{ model.model_name }}
        </span>
      </li>
    </ul>

    <template #footer="{ Action, ActionDropdown }">
      <component :is="Action">
        <component :is="ActionDropdown">
          <MkDropdownMenu>
            <MkDropdownItem>编辑</MkDropdownItem>
            <MkDropdownItem>模型参数设置</MkDropdownItem>
            <MkDropdownItem>资源授权</MkDropdownItem>
            <MkDropdownItem divided>删除</MkDropdownItem>
          </MkDropdownMenu>
        </component>
      </component>
    </template>
  </MkSourceCard>
</template>
