<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import ToolApi from '@/api/admin/workspace/tool/tool'
import WorkspaceToolStoreApi from '@/api/admin/workspace/tool/store'
import { TOOL_TYPE } from '@/api/enums'
import type { ToolItem, ToolStoreItem } from '@/api/types'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'StoreToolFormDialog' })

const props = defineProps<{ folderId?: string }>()

const { auth } = useStore()

const emit = defineEmits<{ closed: []; refresh: []; update: [tool: ToolItem] }>()

interface StoreToolForm {
  name: string
}

const formRef = ref<FormInstance>()
const visible = ref(false)
const isEdit = ref(false)
const loading = ref(false)
const currentTool = ref<ToolStoreItem>()
const storeToolForm = reactive<StoreToolForm>({ name: '' })
const formRules: FormRules<StoreToolForm> = { name: [{ required: true, message: '请输入工具名称', trigger: 'blur' }] }

function handleBeforeClose(done: () => void) {
  if (!loading.value) done()
}

function handleSubmit() {
  formRef.value?.validate((valid) => {
    if (!valid || !currentTool.value) return

    const tool = currentTool.value
    const name = storeToolForm.name
    loading.value = true

    if (isEdit.value) {
      ToolApi.putTool(tool.id, { name })
        .then((updatedTool) => {
          MsgSuccess('保存成功')
          visible.value = false
          emit('update', updatedTool)
        })
        .finally(() => {
          loading.value = false
        })
      return
    }

    const commonPayload = { folder_id: props.folderId || 'default', name }
    let request: Promise<ToolItem>
    let shouldRefreshCurrentUser = false

    if (tool.source === 'internal') {
      request = WorkspaceToolStoreApi.postInternalTool(tool.id, commonPayload)
    } else if (tool.tool_type === TOOL_TYPE.WORKFLOW) {
      shouldRefreshCurrentUser = true
      request = ToolApi.postTool({ ...commonPayload, code: '{}', tool_type: TOOL_TYPE.WORKFLOW, work_flow_template: tool })
    } else {
      request = WorkspaceToolStoreApi.postStoreTool(tool.id, {
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
        if (shouldRefreshCurrentUser) await auth.loadAuthBaseProfile()
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

function open(tool: ToolStoreItem, edit = false) {
  currentTool.value = tool
  isEdit.value = edit
  storeToolForm.name = tool.name
  visible.value = true
}

function handleClosed() {
  currentTool.value = undefined
  isEdit.value = false
  loading.value = false
  storeToolForm.name = ''
  formRef.value?.clearValidate()
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :before-close="handleBeforeClose" :show-close="!loading" :title="isEdit ? '编辑工具' : '添加工具'" @closed="handleClosed">
    <el-form ref="formRef" :model="storeToolForm" :rules="formRules" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="名称" prop="name">
        <el-input v-model="storeToolForm.name" maxlength="64" placeholder="请输入工具名称" show-word-limit @blur="storeToolForm.name = storeToolForm.name.trim()" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button :disabled="loading" plain @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        {{ isEdit ? '保存' : '添加' }}
      </el-button>
    </template>
  </MkDialog>
</template>
