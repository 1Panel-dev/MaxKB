<script setup lang="ts">
import { reactive, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import { TOOL_TYPE } from '@/api/enums'
import type { DynamicFormField, ToolInputField, ToolItem, ToolPayload } from '@/api/types'
import { useStore } from '@/stores'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import InitFieldTable from '../components/init-field/InitFieldTable.vue'
import InputFieldTable from '../components/input-field/InputFieldTable.vue'
import ToolCodeSetting from '../components/python-code/CodeSetting.vue'

defineOptions({ name: 'DataSourceFormDrawer' })

const { auth } = useStore()

const props = defineProps<{
  api: typeof ToolApi
  folderId: string
  title: string
}>()

const emit = defineEmits<{
  closed: []
  refresh: []
  update: [tool: ToolItem]
}>()

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
const dataSourceForm = reactive<DataSourceFormModel>({
  code: codeTemplate,
  desc: '',
  icon: '',
  init_field_list: [],
  input_field_list: [],
  name: '',
})
const formRules: FormRules<DataSourceFormModel> = {
  code: [{ required: true, message: '请输入数据源内容', trigger: 'blur' }],
  name: [{ required: true, message: '请输入数据源名称', trigger: 'blur' }],
}

function handleSubmit() {
  formRef.value?.validate((valid) => {
    if (!valid) return

    const payload: ToolPayload = {
      ...cloneDeep(dataSourceForm),
      tool_type: TOOL_TYPE.DATA_SOURCE,
    }
    loading.value = true
    const currentEditId = editId.value
    const isEdit = Boolean(currentEditId)
    const request = currentEditId
      ? props.api.putTool(currentEditId, payload)
      : props.api.postTool({ ...payload, folder_id: props.folderId || null })

    request
      .then((savedTool) => {
        const refreshCurrentUser = isEdit ? Promise.resolve() : auth.loadAuthBaseProfile()
        return refreshCurrentUser.then(() => {
          MsgSuccess(isEdit ? '保存成功' : '创建成功')
          visible.value = false
          if (isEdit) emit('update', savedTool)
          else emit('refresh')
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
  resetData()
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
  if (JSON.stringify(dataSourceForm) === originalForm.value) {
    visible.value = false
    return
  }
  MsgConfirm('提示', '当前的更改尚未保存，确认退出吗？', {
    confirmButtonText: '确认',
    confirmButtonType: 'primary',
  })
    .then(() => {
      visible.value = false
    })
    .catch(() => {})
}

function resetData() {
  Object.assign(dataSourceForm, {
    code: codeTemplate,
    desc: '',
    icon: '',
    init_field_list: [],
    input_field_list: [],
    name: '',
  })
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
  <MkDrawer
    v-model="visible"
    :before-close="handleBeforeClose"
    :title="title"
    size="60%"
    @closed="handleClosed"
  >
    <el-form
      ref="formRef"
      v-loading="formLoading"
      :model="dataSourceForm"
      :rules="formRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <h4 class="mk-title-decoration mb-4">基本信息</h4>
      <el-form-item label="名称" prop="name">
        <div class="flex w-full items-center gap-3">
          <!-- // TODO 修改头像 -->
          <ToolIcon :icon="dataSourceForm.icon" :size="32" :type="TOOL_TYPE.DATA_SOURCE" />
          <el-input
            v-model="dataSourceForm.name"
            maxlength="64"
            placeholder="请输入数据源名称"
            show-word-limit
            @blur="dataSourceForm.name = dataSourceForm.name.trim()"
          />
        </div>
      </el-form-item>
      <el-form-item label="描述">
        <el-input
          v-model="dataSourceForm.desc"
          :autosize="{ minRows: 3 }"
          maxlength="128"
          placeholder="请输入"
          show-word-limit
          type="textarea"
          @blur="dataSourceForm.desc = dataSourceForm.desc.trim()"
        />
      </el-form-item>

      <InitFieldTable v-model="dataSourceForm.init_field_list" class="mb-6" />
      <InputFieldTable v-model="dataSourceForm.input_field_list" class="mb-6" />
      <ToolCodeSetting v-model="dataSourceForm.code" />
    </el-form>

    <template #footer>
      <el-button plain :disabled="loading" @click="handleBeforeClose">取消</el-button>
      <el-button type="primary" :disabled="formLoading" :loading="loading" @click="handleSubmit">
        {{ editId ? '保存' : '创建' }}
      </el-button>
    </template>
  </MkDrawer>
</template>
