<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type SystemResourceToolApi from '@/api/admin/system/resource-management/tool/tool'
import type SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import { FILE_SOURCE_TYPE, TOOL_TYPE } from '@/api/enums'
import FileApi from '@/api/admin/file'
import type { ToolItem, ToolPayload } from '@/api/types'
import MkEditAvatar from '@/components/mk-edit-avatar/index.vue'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import { isSystemSharedResource } from '@/utils/resource-context'

defineOptions({ name: 'WorkflowFormDialog' })

const { auth } = useStore()
const route = useRoute()
const router = useRouter()

const props = defineProps<{ api: typeof ToolApi | typeof SystemSharedToolApi | typeof SystemResourceToolApi; folderId: string; title: string }>()

const emit = defineEmits<{ closed: []; refresh: []; update: [tool: ToolItem] }>()

interface WorkflowFormModel {
  desc: string
  icon: string
  name: string
  work_flow: Record<string, unknown>
}

const formRef = ref<FormInstance>()
const visible = ref(false)
const loading = ref(false)
const formLoading = ref(false)
const editId = ref<string>()
const workflowForm = reactive<WorkflowFormModel>({ desc: '', icon: '', name: '', work_flow: {} })
const formRules: FormRules<WorkflowFormModel> = { name: [{ whitespace: true, required: true, message: '请输入工作流名称', trigger: 'blur' }] }

// 暂存确认后的头像文件，恢复默认时清空。
const iconFile = ref<File | null>(null)
function handleIconChange(file: File | null) {
  iconFile.value = file
}

function handleSubmit() {
  return formRef.value?.validate((valid) => {
    if (!valid || loading.value) return

    loading.value = true
    const currentEditId = editId.value
    const isEdit = Boolean(currentEditId)
    // 新头像先上传并替换预览地址，再提交完整工具表单。
    const uploadIcon = iconFile.value
      ? FileApi.postUploadFile(iconFile.value, currentEditId, FILE_SOURCE_TYPE.TOOL).request.then((icon) => {
          workflowForm.icon = icon
          iconFile.value = null
        })
      : Promise.resolve()

    return uploadIcon
      .then(() => {
        const payload: ToolPayload = { ...cloneDeep(workflowForm), code: 'None', tool_type: TOOL_TYPE.WORKFLOW }
        const request = currentEditId
          ? props.api.putTool(currentEditId, payload)
          : 'postTool' in props.api
            ? props.api.postTool({ ...payload, folder_id: props.folderId || null })
            : Promise.reject(new Error('资源管理不支持创建工具'))

        return request.then((savedTool) => {
          const refreshCurrentUser = isEdit ? Promise.resolve() : auth.loadAuthBaseProfile()
          return refreshCurrentUser.then(() => {
            MsgSuccess(isEdit ? '保存成功' : '创建成功')
            visible.value = false
            if (isEdit) {
              emit('update', savedTool)
              return
            }

            return router
              .push({
                name: isSystemSharedResource() ? 'system-shared-workflow-tool' : 'workflow-tool',
                params: isSystemSharedResource() ? { toolId: savedTool.id } : { toolId: savedTool.id, workspaceId: route.params.workspaceId },
              })
              .then(() => {})
          })
        })
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function fillWorkflowForm(tool: ToolItem) {
  Object.assign(workflowForm, { desc: tool.desc ?? '', icon: tool.icon ?? '', name: tool.name, work_flow: cloneDeep(tool.work_flow ?? {}) })
}

function open(tool?: ToolItem, asCopy = false) {
  visible.value = true
  if (!tool) return

  if (asCopy) {
    fillWorkflowForm(tool)
    return
  }

  editId.value = tool.id
  formLoading.value = true
  props.api
    .getToolDetail(tool.id)
    .then((toolDetail) => {
      fillWorkflowForm(toolDetail)
    })

    .finally(() => {
      formLoading.value = false
    })
}

function handleBeforeClose(done: () => void) {
  if (loading.value) return
  done()
}

function resetData() {
  Object.assign(workflowForm, { desc: '', icon: '', name: '', work_flow: {} })
  iconFile.value = null
  editId.value = undefined
  loading.value = false
  formLoading.value = false
  formRef.value?.clearValidate()
}

function handleClosed() {
  resetData()
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :before-close="handleBeforeClose" :title="title" @closed="handleClosed">
    <el-form
      ref="formRef"
      v-loading="formLoading || loading"
      :model="workflowForm"
      :rules="formRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="名称" prop="name">
        <div class="flex-align-center w-full gap-3">
          <!-- 设置工具头像 -->
          <MkEditAvatar v-model="workflowForm.icon" @change="handleIconChange">
            <template #default="{ icon }">
              <ToolIcon :icon="icon" :type="TOOL_TYPE.WORKFLOW" />
            </template>
          </MkEditAvatar>
          <el-input
            v-model="workflowForm.name"
            maxlength="64"
            placeholder="请输入工作流名称"
            show-word-limit
            @blur="workflowForm.name = workflowForm.name.trim()"
          />
        </div>
      </el-form-item>
      <el-form-item label="描述">
        <el-input
          v-model="workflowForm.desc"
          :autosize="{ minRows: 3 }"
          maxlength="128"
          placeholder="请输入"
          show-word-limit
          type="textarea"
          @blur="workflowForm.desc = workflowForm.desc.trim()"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain :disabled="loading || formLoading" @click="visible = false">取消</el-button>
      <el-button type="primary" :disabled="formLoading" :loading="loading" @click="handleSubmit">
        {{ editId ? '保存' : '创建' }}
      </el-button>
    </template>
  </MkDialog>
</template>
