<script setup lang="ts">
import ToolApi from '@/api/admin/workspace/tool/tool'
import type { ToolItem, ExportError } from '@/api/types'
import { TOOL_TYPE } from '@/api/enums'
import MkSourceCard from '@/components/mk-source-card/index.vue'
import { MsgConfirm, MsgSuccess, MsgError } from '@/utils/message'

defineOptions({ name: 'ToolCard' })

const props = defineProps<{
  shared: boolean
  tool: ToolItem
}>()
const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{
  copy: [tool: ToolItem]
  delete: [toolId: string]
  update: [tool: ToolItem]
}>()

/* 工具状态 */
function handleStatusChange() {
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

  return ToolApi.getToolDetail(props.tool.id)
    .then((toolDetail) => {
      if (props.tool.tool_type === TOOL_TYPE.WORKFLOW && !toolDetail.is_publish) {
        MsgError('无法启用，请先发布工作流')
        return false
      }

      if (hasMissingInitParams(toolDetail)) {
        // TODO 打开参数配置
        //  InitParamDrawerRef.value.open(res.data, !row.is_active)
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
  return ToolApi.putTool(props.tool.id, { is_active: active })
    .then((res) => {
      emit('update', res)
      MsgSuccess(active ? '启用成功' : '禁用成功')
      return true
    })
    .catch(() => false)
    .finally(() => (loading.value = false))
}

/* 删除工具 */
function handleDeleteTool() {
  return MsgConfirm(`确认删除工具：${props.tool.name}？`)
    .then(() => {
      loading.value = true
      return ToolApi.deleteTool(props.tool.id)
        .then(() => {
          emit('delete', props.tool.id)
          MsgSuccess('删除成功')
        })
        .finally(() => (loading.value = false))
    })
    .catch(() => {})
}

/* 导出工具 */
function handleExportTool(tool: ToolItem) {
  loading.value = true
  return ToolApi.exportTool(tool.id, tool.name)
    .catch((error: ExportError) => {
      if (error.response.status !== 403) {
        return error.response.data.text().then((res: string) => {
          MsgError(`导出失败：${JSON.parse(res).message}`)
        })
      }
    })
    .finally(() => (loading.value = false))
}
</script>

<template>
  <MkSourceCard
    :create_time="tool.create_time"
    :nick_name="tool.nick_name || '-'"
    :title="tool.name"
  >
    <template #icon>
      <ToolIcon :type="tool?.tool_type" :icon="tool.icon" />
    </template>

    <template #tag>
      <el-tag v-if="shared" size="small" type="info">共享</el-tag>
    </template>

    <p class="line-clamp-2" :title="tool?.desc ?? undefined">
      {{ tool.desc }}
    </p>

    <template #footer="{ Action, ActionDropdown }">
      <MkStatusLabel :active="tool.is_active" />
      <component :is="Action" v-if="!shared">
        <el-switch
          :model-value="tool.is_active"
          class="mr-1"
          size="small"
          :before-change="handleStatusChange"
        />
        <el-divider direction="vertical" />
        <component :is="ActionDropdown">
          <MkDropdownItem v-if="tool.tool_type === TOOL_TYPE.CUSTOM">
            <template #icon><MkIcon name="icon_edit_outlined" /></template>
            <span>编辑</span>
          </MkDropdownItem>
          <MkDropdownItem>
            <template #icon><MkIcon name="icon_assigned_outlined" /></template>
            <span>资源授权</span>
          </MkDropdownItem>
          <MkDropdownItem @click="emit('copy', tool)">
            <template #icon><mk-icon name="icon_copy_outlined"></mk-icon></template>
            <span>复制</span>
          </MkDropdownItem>
          <MkDropdownItem>
            <template #icon><MkIcon name="icon_move2_outlined" /></template>
            <span>移动到</span>
          </MkDropdownItem>
          <MkDropdownItem divided @click="handleExportTool(tool)">
            <template #icon><MkIcon name="icon_export_outlined" /></template>
            <span>导出</span>
          </MkDropdownItem>
          <MkDropdownItem divided @click="handleDeleteTool">
            <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
            <span>删除</span>
          </MkDropdownItem>
        </component>
      </component>
    </template>
  </MkSourceCard>
</template>

<style lang="scss" scoped></style>
