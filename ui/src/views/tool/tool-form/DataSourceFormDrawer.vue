<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type SystemResourceToolApi from '@/api/admin/system/resource-management/tool/tool'
import type SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { DynamicFormField, ToolInputField, ToolItem, ToolPayload } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { FILE_SOURCE_TYPE, TOOL_TYPE } from '@/api/enums'
import FileApi from '@/api/admin/file'
import MkEditAvatar from '@/components/mk-edit-avatar/index.vue'
import InitFieldTable from './component/init-field/InitFieldTable.vue'
import InputFieldTable from './component/input-field/InputFieldTable.vue'
import ToolCodeGenerate from './component/python-code/CodeGenerate.vue'
import { useStore } from '@/stores'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DataSourceFormDrawer' })

const { t } = useI18n({ useScope: 'global' })
const { auth } = useStore()

const props = defineProps<{ api: typeof ToolApi | typeof SystemSharedToolApi | typeof SystemResourceToolApi; folderId: string; title: string }>()

const emit = defineEmits<{ closed: []; refresh: []; update: [tool: ToolItem] }>()

interface DataSourceFormModel {
  code: string
  desc: string
  icon: string
  init_field_list: DynamicFormField[]
  input_field_list: ToolInputField[]
  name: string
}

const codeTemplate = `def get_form_list(node, **kwargs):
    """返回数据源的表单字段。"""
    return []


def get_file_list(**kwargs):
    """返回可选择的文件列表。"""
    pass


def download(**kwargs):
    """下载选中的文件。"""
    pass
`
const formRef = ref<FormInstance>()
const visible = ref(false)
const loading = ref(false)
const formLoading = ref(false)
const editId = ref<string>()
const originalForm = ref('')
const dataSourceForm = reactive<DataSourceFormModel>({ code: codeTemplate, desc: '', icon: '', init_field_list: [], input_field_list: [], name: '' })
const formRules = computed<FormRules<DataSourceFormModel>>(() => ({
  code: [{ whitespace: true, required: true, message: t('tool.dataSource.code.requiredMessage'), trigger: 'blur' }],
  name: [{ whitespace: true, required: true, message: t('tool.dataSource.name.requiredMessage'), trigger: 'blur' }],
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
          dataSourceForm.icon = icon
          iconFile.value = null
        })
      : Promise.resolve()

    return uploadIcon
      .then(() => {
        const payload: ToolPayload = { ...cloneDeep(dataSourceForm), tool_type: TOOL_TYPE.DATA_SOURCE }
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

function fillDataSourceForm(tool: ToolItem) {
  Object.assign(dataSourceForm, {
    code: tool.code ?? codeTemplate,
    desc: tool.desc ?? '',
    icon: tool.icon ?? '',
    init_field_list: cloneDeep(tool.init_field_list ?? []),
    input_field_list: cloneDeep(tool.input_field_list ?? []),
    name: tool.name,
  })
}

function open(tool?: ToolItem, asCopy = false) {
  visible.value = true
  originalForm.value = JSON.stringify(dataSourceForm)
  if (!tool) return

  if (asCopy) {
    fillDataSourceForm(tool)
    originalForm.value = JSON.stringify(dataSourceForm)
    return
  }

  editId.value = tool.id
  formLoading.value = true
  props.api
    .getToolDetail(tool.id)
    .then((toolDetail) => {
      fillDataSourceForm(toolDetail)
      originalForm.value = JSON.stringify(dataSourceForm)
    })

    .finally(() => {
      formLoading.value = false
    })
}

function handleBeforeClose() {
  if (loading.value) return
  if (JSON.stringify(dataSourceForm) === originalForm.value) {
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
  Object.assign(dataSourceForm, { code: codeTemplate, desc: '', icon: '', init_field_list: [], input_field_list: [], name: '' })
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
      :model="dataSourceForm"
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
          <MkEditAvatar v-model="dataSourceForm.icon" @change="handleIconChange">
            <template #default="{ icon }">
              <ToolIcon :icon="icon" :type="TOOL_TYPE.DATA_SOURCE" />
            </template>
          </MkEditAvatar>
          <el-input
            v-model="dataSourceForm.name"
            maxlength="64"
            :placeholder="t('tool.dataSource.name.placeholder')"
            show-word-limit
            @blur="dataSourceForm.name = dataSourceForm.name.trim()"
          />
        </div>
      </el-form-item>
      <el-form-item :label="t('common.description.label')">
        <el-input
          v-model="dataSourceForm.desc"
          :autosize="{ minRows: 3 }"
          maxlength="128"
          :placeholder="t('common.placeholders.input')"
          show-word-limit
          type="textarea"
          @blur="dataSourceForm.desc = dataSourceForm.desc.trim()"
        />
      </el-form-item>

      <InitFieldTable v-model="dataSourceForm.init_field_list" class="mb-6" />
      <InputFieldTable v-model="dataSourceForm.input_field_list" class="mb-6" />
      <ToolCodeGenerate v-model="dataSourceForm.code" />
    </el-form>

    <template #footer>
      <el-button plain :disabled="loading || formLoading" @click="handleBeforeClose">{{ t('common.actions.cancel') }}</el-button>
      <el-button type="primary" :disabled="formLoading" :loading="loading" @click="handleSubmit">
        {{ editId ? t('common.actions.save') : t('common.actions.create') }}
      </el-button>
    </template>
  </MkDrawer>
</template>
