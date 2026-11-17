<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type SystemResourceToolApi from '@/api/admin/system/resource-management/tool/tool'
import type SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { DynamicFormField, ToolInputField, ToolItem } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { FILE_SOURCE_TYPE } from '@/api/enums'
import FileApi from '@/api/admin/file'
import MkEditAvatar from '@/components/mk-edit-avatar/index.vue'
import InitFieldTable from '../component/init-field/InitFieldTable.vue'
import InputFieldTable from '../component/input-field/InputFieldTable.vue'
import ToolCodeGenerate from '../component/python-code/CodeGenerate.vue'
import ToolDebugDrawer from './ToolDebugDrawer.vue'
import { useStore } from '@/stores'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'ToolFormDrawer' })

const { t } = useI18n({ useScope: 'global' })
const { auth } = useStore()

const props = withDefaults(
  defineProps<{
    api: typeof ToolApi | typeof SystemSharedToolApi | typeof SystemResourceToolApi
    title: string
    folderId: string
    canEdit?: boolean
  }>(),
  { canEdit: true },
)

const emit = defineEmits<{ closed: []; refresh: []; update: [tool: ToolItem] }>()

interface ToolFormModel {
  workspace_id?: string
  desc: string
  code: string
  icon: string
  init_field_list: DynamicFormField[]
  input_field_list: ToolInputField[]
  name: string
}

const formRef = ref<FormInstance>()

const visible = ref(false)
const loading = ref(false)
const formLoading = ref(false)
const editId = ref<string>()
const originalForm = ref('')

const toolForm = reactive<ToolFormModel>({ name: '', desc: '', code: '', icon: '', init_field_list: [], input_field_list: [] })
const formRules = computed<FormRules<ToolFormModel>>(() => ({
  code: [{ whitespace: true, required: true, message: t('tool.fields.code.requiredMessage'), trigger: 'blur' }],
  name: [{ whitespace: true, required: true, message: t('tool.fields.name.requiredMessage'), trigger: 'blur' }],
}))

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
          toolForm.icon = icon
          iconFile.value = null
        })
      : Promise.resolve()

    return uploadIcon
      .then(() => {
        const payload = cloneDeep(toolForm)
        delete payload.workspace_id
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

// 调试

const debugDrawerRef = ref<InstanceType<typeof ToolDebugDrawer>>()
function handleOpenDebug() {
  debugDrawerRef.value?.open(toolForm)
}

function fillToolForm(tool: ToolItem) {
  Object.assign(toolForm, {
    workspace_id: tool.workspace_id,
    code: tool.code ?? '',
    desc: tool.desc ?? '',
    icon: tool.icon ?? '',
    init_field_list: cloneDeep(tool.init_field_list ?? []),
    input_field_list: cloneDeep(tool.input_field_list ?? []),
    name: tool.name,
  })
}

function open(tool?: ToolItem, asCopy = false) {
  visible.value = true
  originalForm.value = JSON.stringify(toolForm)
  if (tool) {
    if (asCopy) {
      fillToolForm(tool)
      originalForm.value = JSON.stringify(toolForm)
      return
    }

    editId.value = tool.id
    formLoading.value = true
    props.api
      .getToolDetail(tool.id)
      .then((toolDetail) => {
        fillToolForm(toolDetail)
        originalForm.value = JSON.stringify(toolForm)
      })
      .finally(() => {
        formLoading.value = false
      })
  }

  visible.value = true
}

function handleBeforeClose() {
  if (loading.value) return
  if (JSON.stringify(toolForm) === originalForm.value) {
    visible.value = false
    return
  }
  MsgConfirm(t('common.dialogs.notice'), t('common.dialogs.unsavedChanges'), {
    confirmButtonText: t('common.actions.confirm'),
    confirmButtonType: 'primary',
  })
    .then(() => {
      visible.value = false
    })
    .catch(() => {})
}

function resetData() {
  Object.assign(toolForm, { name: '', desc: '', code: '', icon: '', init_field_list: [], input_field_list: [], workspace_id: undefined })
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
      :model="toolForm"
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
          <MkEditAvatar v-model="toolForm.icon" @change="handleIconChange">
            <template #default="{ icon }">
              <ToolIcon :icon="icon" />
            </template>
          </MkEditAvatar>
          <el-input
            v-model="toolForm.name"
            maxlength="64"
            :placeholder="t('tool.fields.name.placeholder')"
            show-word-limit
            @blur="toolForm.name = toolForm.name.trim()"
          />
        </div>
      </el-form-item>
      <el-form-item :label="t('common.description.label')">
        <el-input
          v-model="toolForm.desc"
          :autosize="{ minRows: 3 }"
          maxlength="128"
          :placeholder="t('common.placeholders.input')"
          show-word-limit
          type="textarea"
          @blur="toolForm.desc = toolForm.desc.trim()"
        />
      </el-form-item>

      <!-- 启动参数 -->
      <InitFieldTable v-model="toolForm.init_field_list" class="mb-6" />
      <!-- 输入参数 -->
      <InputFieldTable v-model="toolForm.input_field_list" class="mb-6" />

      <ToolCodeGenerate v-model="toolForm.code" :tool-form="toolForm" class="mb-6" show-generate />
      <section>
        <div class="mb-4 flex-align-center gap-2">
          <h4 class="mk-title-decoration">{{ t('tool.outputParams.title') }}</h4>
          <span class="text-N600">{{ t('tool.parameters.shownWhenUsed') }}</span>
        </div>
        <div class="mk-gray-card-sm rounded-md!">{{ t('tool.outputParams.result', { variable: '{result}' }) }}</div>
      </section>
    </el-form>

    <template #footer>
      <!-- 取消编辑 -->
      <el-button plain :disabled="loading || formLoading" @click="handleBeforeClose">{{ t('common.actions.cancel') }}</el-button>
      <!-- 调试工具 -->
      <el-button v-if="canEdit" plain :disabled="loading || formLoading" @click="handleOpenDebug">{{ t('tool.debug.title') }}</el-button>
      <!-- 保存或创建工具 -->
      <el-button v-if="canEdit" type="primary" :disabled="formLoading" :loading="loading" @click="handleSubmit">
        {{ editId ? t('common.actions.save') : t('common.actions.create') }}
      </el-button>
    </template>

    <ToolDebugDrawer ref="debugDrawerRef" :api="api" />
  </MkDrawer>
</template>
