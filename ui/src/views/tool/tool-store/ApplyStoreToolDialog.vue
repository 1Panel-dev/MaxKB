<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import ToolApi from '@/api/admin/workspace/tool/tool'
import WorkspaceToolStoreApi from '@/api/admin/workspace/tool/store'
import SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import SystemSharedToolStoreApi from '@/api/admin/system/shared-resources/tool/store'
import { TOOL_TYPE } from '@/api/enums'
import type { ToolItem, ToolStoreItem } from '@/api/types'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import { isSystemSharedResource } from '@/utils/resource-context'

defineOptions({ name: 'StoreToolFormDialog' })

const props = withDefaults(
  defineProps<{
    folderId: string
  }>(),
  { folderId: 'default' },
)

const { auth } = useStore()

const emit = defineEmits<{ closed: []; refresh: []; update: [tool: ToolItem] }>()

interface StoreToolForm {
  name: string
}

const formRef = ref<FormInstance>()
const visible = ref(false)
const loading = ref(false)
const currentTool = ref<ToolStoreItem>()
const storeToolForm = reactive<StoreToolForm>({ name: '' })
const formRules: FormRules<StoreToolForm> = { name: [{ whitespace: true, required: true, message: '请输入工具名称', trigger: 'blur' }] }

function handleSubmit() {
  formRef.value?.validate((valid) => {
    if (!valid || !currentTool.value) return

    const tool = currentTool.value
    const name = storeToolForm.name
    loading.value = true

    const commonPayload = { folder_id: props.folderId || 'default', name }
    const isSharedResource = isSystemSharedResource()
    let request: Promise<ToolItem>

    if (tool.label === 'workflow_template') {
      const requestApi = isSharedResource ? SystemSharedToolApi : ToolApi
      request = requestApi.postTool({ ...commonPayload, code: '{}', tool_type: TOOL_TYPE.WORKFLOW, work_flow_template: tool })
    } else {
      const requestApi = isSharedResource ? SystemSharedToolStoreApi : WorkspaceToolStoreApi
      request = requestApi.postStoreTool(tool.id, {
        ...commonPayload,
        download_callback_url: tool.downloadCallbackUrl ?? '',
        download_url: tool.downloadUrl ?? '',
        icon: tool.icon ?? '',
        label: tool.label ?? '',
        versions: tool.versions ?? [],
      })
    }

    request
      .then(async () => {
        await auth.loadAuthBaseProfile()
      })
      .then(() => {
        MsgSuccess('添加成功')
        visible.value = false
        emit('refresh')
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function open(tool: ToolStoreItem) {
  currentTool.value = tool
  storeToolForm.name = tool.name
  visible.value = true
}

function handleClosed() {
  currentTool.value = undefined
  loading.value = false
  storeToolForm.name = ''
  formRef.value?.clearValidate()
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :show-close="!loading" title="添加工具" @closed="handleClosed">
    <el-form ref="formRef" :model="storeToolForm" :rules="formRules" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="名称" prop="name">
        <el-input
          v-model="storeToolForm.name"
          maxlength="64"
          placeholder="请输入工具名称"
          show-word-limit
          @blur="storeToolForm.name = storeToolForm.name.trim()"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button :disabled="loading" plain @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit"> 添加 </el-button>
    </template>
  </MkDialog>
</template>
