<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
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
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'McpFormDrawer' })

const { t } = useI18n({ useScope: 'global' })
const { auth } = useStore()

const props = defineProps<{ api: typeof ToolApi | typeof SystemSharedToolApi | typeof SystemResourceToolApi; folderId: string; title: string }>()

const emit = defineEmits<{ closed: []; refresh: []; update: [tool: ToolItem] }>()

interface McpFormModel {
  code: string
  desc: string
  icon: string
  name: string
}

const mcpServerExample = `{
  "math": {
    "url": "your_server",
    "transport": "sse"
  }
}`
const formRef = ref<FormInstance>()
const visible = ref(false)
const loading = ref(false)
const formLoading = ref(false)
const editId = ref<string>()
const originalForm = ref('')
const mcpForm = reactive<McpFormModel>({ code: '', desc: '', icon: '', name: '' })
const formRules = computed<FormRules<McpFormModel>>(() => ({
  code: [{ whitespace: true, required: true, message: t('tool.mcp.config.requiredMessage'), trigger: 'blur' }],
  name: [{ whitespace: true, required: true, message: t('tool.mcp.name.requiredMessage'), trigger: 'blur' }],
}))

// 暂存确认后的头像文件，恢复默认时清空。
const iconFile = ref<File | null>(null)
function handleIconChange(file: File | null) {
  iconFile.value = file
}

function isValidConfig() {
  try {
    const config: unknown = JSON.parse(mcpForm.code)
    if (!config || typeof config !== 'object' || Array.isArray(config)) throw new Error()
    return true
  } catch {
    MsgError(t('tool.mcp.config.invalidMessage'))
    return false
  }
}

function handleSubmit() {
  return formRef.value?.validate((valid) => {
    if (!valid || loading.value || !isValidConfig()) return

    loading.value = true
    const currentEditId = editId.value
    const isEdit = Boolean(currentEditId)
    // 新头像先上传并替换预览地址，再提交完整工具表单。
    const uploadIcon = iconFile.value
      ? FileApi.postUploadFile(iconFile.value, currentEditId, FILE_SOURCE_TYPE.TOOL).request.then((icon) => {
          mcpForm.icon = icon
          iconFile.value = null
        })
      : Promise.resolve()

    return uploadIcon
      .then(() => {
        const payload: ToolPayload = { ...cloneDeep(mcpForm), tool_type: TOOL_TYPE.MCP }
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
            if (isEdit) emit('update', savedTool)
            else emit('refresh')
          })
        })
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function handleTestConnection() {
  formRef.value?.validateField('code', (valid) => {
    if (!valid || !isValidConfig()) return

    loading.value = true
    props.api
      .postToolTestConnection({ code: mcpForm.code })
      .then(() => MsgSuccess(t('common.messages.connectionSuccess')))
      .finally(() => {
        loading.value = false
      })
  })
}

function fillMcpForm(tool: ToolItem) {
  Object.assign(mcpForm, { code: tool.code ?? '', desc: tool.desc ?? '', icon: tool.icon ?? '', name: tool.name })
}

function open(tool?: ToolItem, asCopy = false) {
  visible.value = true
  originalForm.value = JSON.stringify(mcpForm)
  if (!tool) return

  if (asCopy) {
    fillMcpForm(tool)
    originalForm.value = JSON.stringify(mcpForm)
    return
  }

  editId.value = tool.id
  formLoading.value = true
  props.api
    .getToolDetail(tool.id)
    .then((toolDetail) => {
      fillMcpForm(toolDetail)
      originalForm.value = JSON.stringify(mcpForm)
    })

    .finally(() => {
      formLoading.value = false
    })
}

function handleBeforeClose() {
  if (loading.value) return
  if (JSON.stringify(mcpForm) === originalForm.value) {
    visible.value = false
    return
  }
  MsgConfirm(t('common.dialogs.notice'), `${t('common.dialogs.unsavedChanges')}?`, {
    confirmButtonText: t('common.actions.comfirm'),
    confirmButtonType: 'primary',
  })
    .then(() => {
      visible.value = false
    })
    .catch(() => {})
}

function resetData() {
  Object.assign(mcpForm, { code: '', desc: '', icon: '', name: '' })
  iconFile.value = null
  editId.value = undefined
  originalForm.value = ''
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
  <MkDrawer v-model="visible" :before-close="handleBeforeClose" :title="title" size="60%" @closed="handleClosed">
    <el-form
      ref="formRef"
      v-loading="formLoading || loading"
      :model="mcpForm"
      :rules="formRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <h4 class="mk-title-decoration mb-4">{{ t('common.labels.basicInfo') }}</h4>
      <el-form-item class="mk-form-item-with-avatar" :label="t('common.name.label')" prop="name">
        <div class="flex-align-center w-full gap-3">
          <!-- 设置工具头像 -->
          <MkEditAvatar v-model="mcpForm.icon" @change="handleIconChange">
            <template #default="{ icon }">
              <ToolIcon :icon="icon" :type="TOOL_TYPE.MCP" />
            </template>
          </MkEditAvatar>
          <el-input
            v-model="mcpForm.name"
            maxlength="64"
            :placeholder="t('tool.mcp.name.placeholder')"
            show-word-limit
            @blur="mcpForm.name = mcpForm.name.trim()"
          />
        </div>
      </el-form-item>
      <el-form-item :label="t('common.description.label')">
        <el-input
          v-model="mcpForm.desc"
          :autosize="{ minRows: 3 }"
          maxlength="128"
          :placeholder="t('common.placeholders.input')"
          show-word-limit
          type="textarea"
          @blur="mcpForm.desc = mcpForm.desc.trim()"
        />
      </el-form-item>

      <h4 class="mk-title-decoration mb-4">{{ t('tool.mcp.serviceTitle') }}</h4>
      <el-form-item prop="code" class="mk-hide-asterisk">
        <template #label>
          <span class="mk-required">{{ t('resource.mcpConfig.title') }}</span>
          <span class="ml-1 text-N600">{{ t('tool.mcp.config.description') }}</span>
        </template>
        <el-input v-model="mcpForm.code" :autosize="{ minRows: 8 }" :placeholder="mcpServerExample" type="textarea" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain :disabled="loading || formLoading" @click="handleBeforeClose">{{ t('common.actions.cancel') }}</el-button>
      <el-button plain :disabled="loading || formLoading" @click="handleTestConnection">{{ t('common.actions.testConnection') }}</el-button>
      <el-button type="primary" :disabled="formLoading" :loading="loading" @click="handleSubmit">
        {{ editId ? t('common.actions.save') : t('common.actions.create') }}
      </el-button>
    </template>
  </MkDrawer>
</template>
