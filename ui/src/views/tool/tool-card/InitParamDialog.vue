<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { Dict, ToolItem } from '@/api/types'
import { MkDynamicsForm, type DynamicFormValue } from '@/components/mk-dynamics-form'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'InitParamDialog' })

const props = defineProps<{ api: typeof ToolApi }>()

const emit = defineEmits<{ closed: []; update: [tool: ToolItem] }>()

const dynamicsFormRef = useTemplateRef<InstanceType<typeof MkDynamicsForm>>('dynamicsFormRef')
const visible = ref(false)
const loading = ref(false)
const toolDetail = ref<ToolItem>()
const targetActive = ref(false)
const enableAfterSave = ref(false)
const initParams = ref<Dict<DynamicFormValue>>({})

function resetData() {
  toolDetail.value = undefined
  targetActive.value = false
  enableAfterSave.value = false
  initParams.value = {}
  loading.value = false
}

function open(tool: ToolItem, active = tool.is_active, shouldEnableAfterSave = false) {
  resetData()
  toolDetail.value = cloneDeep(tool)
  targetActive.value = active
  enableAfterSave.value = shouldEnableAfterSave
  initParams.value = typeof tool.init_params === 'object' && tool.init_params && !Array.isArray(tool.init_params) ? cloneDeep(tool.init_params) : {}
  visible.value = true
}

function handleSubmit() {
  const currentTool = toolDetail.value
  if (!currentTool) return

  dynamicsFormRef.value?.validate().then(() => {
    loading.value = true
    return props.api
      .putTool(currentTool.id, { init_params: cloneDeep(initParams.value), is_active: targetActive.value })
      .then((updatedTool) => {
        MsgSuccess(enableAfterSave.value ? '启用成功' : '保存成功')
        emit('update', updatedTool)
        visible.value = false
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function handleClosed() {
  resetData()
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="配置启动参数" @closed="handleClosed">
    <MkDynamicsForm v-if="toolDetail" ref="dynamicsFormRef" v-model="initParams" :render-data="toolDetail.init_field_list ?? []" />

    <template #footer>
      <el-button :disabled="loading" plain @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        {{ enableAfterSave ? '保存并启用' : '保存' }}
      </el-button>
    </template>
  </MkDialog>
</template>
