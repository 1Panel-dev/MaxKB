<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import { TOOL_TYPE } from '@/api/enums'
import type { ToolItem, ToolStoreResponse } from '@/api/types'
import MkSourceCard from '@/components/mk-source-card/index.vue'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'
import InitParamDialog from './InitParamDialog.vue'
import UpdateVersionButton from './UpdateVersionButton.vue'

defineOptions({ name: 'ToolCard' })

const props = defineProps<{
  api: typeof ToolApi
  disabled?: boolean
  selectable?: boolean
  selected?: boolean
  shared: boolean
  storeTools: ToolStoreResponse['apps']
  tool: ToolItem
}>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{
  selected: [selected: boolean]
  update: [tool: ToolItem]
}>()

defineSlots<{
  actions?: () => unknown
  'action-dropdown'?: () => unknown
}>()

const initParamDialogMounted = ref(false)
const initParamDialogRef =
  useTemplateRef<InstanceType<typeof InitParamDialog>>('initParamDialogRef')

function handleToolStatusChange() {
  if (props.tool.is_active) {
    return MsgConfirm(
      `是否禁用工具：${props.tool.name}？`,
      '禁用后，引用了该工具的资源执行会报错 ，请谨慎操作。',
      {
        confirmButtonText: '禁用',
      },
    )
      .then(() => updateToolStatus(false))
      .catch(() => false)
  }

  return props.api
    .getToolDetail(props.tool.id)
    .then((toolDetail) => {
      if (props.tool.tool_type === TOOL_TYPE.WORKFLOW && !toolDetail.is_publish) {
        MsgError('无法启用，请先发布工作流')
        return false
      }

      if (hasMissingInitParams(toolDetail)) {
        initParamDialogMounted.value = true
        void nextTick(() => initParamDialogRef.value?.open(toolDetail, !props.tool.is_active))
        return false
      }

      return updateToolStatus(true)
    })
    .catch(() => false)
}

function hasMissingInitParams(tool: ToolItem) {
  const initFields = tool.init_field_list ?? []
  const initParams =
    typeof tool.init_params === 'object' && tool.init_params ? tool.init_params : {}
  const configuredByDefault = initFields.every(
    (field) =>
      field.show_default_value &&
      field.default_value !== undefined &&
      field.default_value !== null &&
      field.default_value !== '',
  )

  return initFields.length > 0 && !Object.keys(initParams).length && !configuredByDefault
}

function updateToolStatus(active: boolean) {
  loading.value = true
  return props.api
    .putTool(props.tool.id, { is_active: active })
    .then((updatedTool) => {
      emit('update', updatedTool)
      MsgSuccess(active ? '启用成功' : '禁用成功')
      return true
    })
    .catch(() => false)
    .finally(() => (loading.value = false))
}

function handleInitParamDialogClosed() {
  initParamDialogMounted.value = false
}
</script>

<template>
  <MkSourceCard
    :create_time="tool.create_time"
    :nick_name="tool.nick_name || '-'"
    :selectable="selectable"
    :selected="selected"
    :title="tool.name"
    @selected="emit('selected', $event)"
  >
    <template #icon>
      <ToolIcon :type="tool.tool_type" :icon="tool.icon" />
    </template>
    <template #title="{ title }">
      <h6 class="min-w-0 truncate" :title="title">{{ title }}</h6>
      <el-tag v-if="tool.version" size="small" type="info" effect="plain">
        {{ tool.version }}
      </el-tag>
    </template>

    <template #tag>
      <el-tag v-if="shared" size="small" type="info">共享</el-tag>
      <UpdateVersionButton
        v-else-if="!selectable"
        v-model:loading="loading"
        :store-tools="storeTools"
        :tool="tool"
        @update="emit('update', $event)"
      />
    </template>

    <p class="line-clamp-2" :title="tool.desc ?? undefined">
      {{ tool.desc }}
    </p>

    <template #footer="{ Action, ActionDropdown }">
      <MkStatusLabel :active="tool.is_active" />
      <component :is="Action" v-if="!disabled">
        <!-- 修改启用禁用按钮 -->
        <div>
          <el-switch
            :model-value="tool.is_active"
            class="mr-3"
            size="small"
            :before-change="handleToolStatusChange"
          />
          <el-divider direction="vertical" />
        </div>
        <slot name="actions" />
        <component :is="ActionDropdown">
          <slot name="action-dropdown" />
        </component>
      </component>
    </template>
  </MkSourceCard>

  <InitParamDialog
    v-if="initParamDialogMounted"
    ref="initParamDialogRef"
    :api="api"
    @closed="handleInitParamDialogClosed"
    @update="emit('update', $event)"
  />
</template>
