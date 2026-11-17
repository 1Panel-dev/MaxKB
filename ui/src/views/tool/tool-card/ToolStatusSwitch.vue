<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type SystemResourceToolApi from '@/api/admin/system/resource-management/tool/tool'
import type SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { ToolItem } from '@/api/types'
import { TOOL_TYPE } from '@/api/enums'
import InitParamDrawer from './InitParamDrawer.vue'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'ToolStatusSwitch', inheritAttrs: false })

const props = defineProps<{ api: typeof ToolApi | typeof SystemSharedToolApi | typeof SystemResourceToolApi; tool: ToolItem }>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ update: [tool: ToolItem] }>()

const initParamMounted = ref(false)
const initParamDrawerRef = useTemplateRef<InstanceType<typeof InitParamDrawer>>('initParamDrawerRef')

function handleToolStatusChange() {
  if (loading.value) return false
  if (props.tool.is_active) {
    return MsgConfirm(t('tool.disable.title', { name: props.tool.name }), t('tool.disable.description'), {
      cancelButtonText: t('common.actions.cancel'),
      confirmButtonText: t('common.actions.disable'),
    })
      .then(() => updateToolStatus(false))
      .catch(() => false)
  }

  loading.value = true
  return props.api
    .getToolDetail(props.tool.id)
    .then((toolDetail) => {
      if (props.tool.tool_type === TOOL_TYPE.WORKFLOW && !toolDetail.is_publish) {
        MsgError(t('tool.messages.publishBeforeEnabling'))
        return false
      }

      if (hasMissingInitParams(toolDetail)) {
        initParamMounted.value = true
        return nextTick(() => {
          initParamDrawerRef.value?.open(toolDetail, true, true)
          return false
        })
      }

      return updateToolStatus(true)
    })
    .catch(() => false)
    .finally(() => {
      loading.value = false
    })
}

function handleInitParamClosed() {
  initParamMounted.value = false
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
      MsgSuccess(active ? t('common.messages.enableSuccess') : t('common.messages.disableSuccess'))
      return true
    })
    .catch(() => false)
    .finally(() => (loading.value = false))
}
</script>

<template>
  <el-switch :disabled="loading" :model-value="tool.is_active" size="small" :before-change="handleToolStatusChange" v-bind="$attrs" />

  <InitParamDrawer v-if="initParamMounted" ref="initParamDrawerRef" :api="api" @closed="handleInitParamClosed" @update="emit('update', $event)" />
</template>
