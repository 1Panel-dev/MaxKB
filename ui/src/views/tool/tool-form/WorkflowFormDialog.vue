<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type SystemResourceToolApi from '@/api/admin/system/resource-management/tool/tool'
import type SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { ToolItem, ToolPayload } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { FILE_SOURCE_TYPE, TOOL_TYPE } from '@/api/enums'
import FileApi from '@/api/admin/file'
import MkEditAvatar from '@/components/mk-edit-avatar/index.vue'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import { isSystemSharedResource } from '@/utils/resource-context'

defineOptions({ name: 'WorkflowFormDialog' })

const { t } = useI18n({ useScope: 'global' })
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
const formRules = computed<FormRules<WorkflowFormModel>>(() => ({
  name: [{ whitespace: true, required: true, message: t('tool.workflow.name.requiredMessage'), trigger: 'blur' }],
}))

// 暂存确定后的头像文件，恢复默认时清空。
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
            : Promise.reject(new Error(t('tool.messages.createUnsupported')))

        return request.then((savedTool) => {
          const refreshCurrentUser = isEdit ? Promise.resolve() : auth.loadAuthBaseProfile()
          return refreshCurrentUser.then(() => {
            MsgSuccess(isEdit ? t('common.messages.saveSuccess') : t('common.messages.createSuccess'))
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
  <MkDialog v-model="visible" :title="title" @closed="handleClosed">
    <el-form
      ref="formRef"
      v-loading="formLoading || loading"
      :model="workflowForm"
      :rules="formRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item class="mk-form-item-with-avatar" :label="t('common.name.label')" prop="name">
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
            :placeholder="t('tool.workflow.name.placeholder')"
            show-word-limit
            @blur="workflowForm.name = workflowForm.name.trim()"
          />
        </div>
      </el-form-item>
      <el-form-item :label="t('common.description.label')">
        <el-input
          v-model="workflowForm.desc"
          :autosize="{ minRows: 3 }"
          maxlength="128"
          :placeholder="t('common.placeholders.input')"
          show-word-limit
          type="textarea"
          @blur="workflowForm.desc = workflowForm.desc.trim()"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain :disabled="loading || formLoading" @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <el-button type="primary" :disabled="formLoading" :loading="loading" @click="handleSubmit">
        {{ editId ? t('common.actions.save') : t('common.actions.create') }}
      </el-button>
    </template>
  </MkDialog>
</template>
