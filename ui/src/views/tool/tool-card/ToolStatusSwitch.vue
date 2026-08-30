<script setup lang="ts">
import { useTemplateRef } from 'vue'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import { TOOL_TYPE } from '@/api/enums'
import type { ToolItem } from '@/api/types'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'
import InitParamDialog from './InitParamDialog.vue'

defineOptions({ name: 'ToolStatusSwitch' })

const props = defineProps<{ api: typeof ToolApi; tool: ToolItem }>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ update: [tool: ToolItem] }>()

const initParamDialogRef = useTemplateRef<InstanceType<typeof InitParamDialog>>('initParamDialogRef')

function handleToolStatusChange() {
  if (props.tool.is_active) {
    return MsgConfirm(`是否禁用工具：${props.tool.name}？`, '禁用后，引用了该工具的资源执行会报错 ，请谨慎操作。', { confirmButtonText: '禁用' })
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
        initParamDialogRef.value?.open(toolDetail, true, true)
        return false
      }

      return updateToolStatus(true)
    })
    .catch(() => false)
}

function hasMissingInitParams(tool: ToolItem) {
  const initFields = tool.init_field_list ?? []
  const initParams = typeof tool.init_params === 'object' && tool.init_params ? tool.init_params : {}
  const configuredByDefault = initFields.every(
    (field) => field.show_default_value && field.default_value !== undefined && field.default_value !== null && field.default_value !== '',
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
</script>

<template>
  <div>
    <el-switch :model-value="tool.is_active" class="mr-3" size="small" :before-change="handleToolStatusChange" />
    <el-divider direction="vertical" />
  </div>

  <InitParamDialog ref="initParamDialogRef" :api="api" @update="emit('update', $event)" />
</template>
