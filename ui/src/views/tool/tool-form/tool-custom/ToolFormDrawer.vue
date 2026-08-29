<script setup lang="ts">
import { reactive, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import type { DynamicFormField, ToolInputField, ToolItem, ToolPayload } from '@/api/types'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import { useStore } from '@/stores'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import ToolDebugDrawer from './ToolDebugDrawer.vue'
import InitFieldTable from '../../components/init-field/InitFieldTable.vue'
import InputFieldTable from '../../components/input-field/InputFieldTable.vue'
import ToolCodeSetting from '../../components/python-code/CodeSetting.vue'

defineOptions({ name: 'ToolFormDrawer' })

const { auth } = useStore()

const props = defineProps<{
  api: typeof ToolApi
  title: string
  folderId: string
}>()

const emit = defineEmits<{
  closed: []
  refresh: []
  update: [tool: ToolItem]
}>()

interface ToolFormModel {
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

const toolForm = reactive<ToolFormModel>({
  name: '',
  desc: '',
  code: '',
  icon: '',
  init_field_list: [],
  input_field_list: [],
})
const formRules: FormRules<ToolFormModel> = {
  code: [{ required: true, message: '请输入工具内容', trigger: 'blur' }],
  name: [{ required: true, message: '请输入工具名称', trigger: 'blur' }],
}

function handleSubmit() {
  formRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    const payload: ToolPayload = cloneDeep(toolForm)
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

// 调试

const debugDrawerRef = ref<InstanceType<typeof ToolDebugDrawer>>()
function handleOpenDebug() {
  debugDrawerRef.value?.open(toolForm)
}

function fillToolForm(tool: ToolItem) {
  Object.assign(toolForm, {
    code: tool.code ?? '',
    desc: tool.desc ?? '',
    icon: tool.icon ?? '',
    init_field_list: cloneDeep(tool.init_field_list ?? []),
    input_field_list: cloneDeep(tool.input_field_list ?? []),
    name: tool.name,
  })
}

function open(tool?: ToolItem, asCopy = false) {
  resetData()
  originalForm.value = JSON.stringify(toolForm)
  if (tool) {
    if (asCopy) {
      fillToolForm(tool)
      originalForm.value = JSON.stringify(toolForm)
      visible.value = true
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
  if (JSON.stringify(toolForm) === originalForm.value) {
    visible.value = false
    return
  }
  MsgConfirm('提示？', '当前的更改尚未保存，确认退出吗？', {
    confirmButtonText: '确认',
    confirmButtonType: 'primary',
  })
    .then(() => {
      visible.value = false
    })
    .catch(() => {})
}

function resetData() {
  Object.assign(toolForm, {
    name: '',
    desc: '',
    code: '',
    icon: '',
    init_field_list: [],
    input_field_list: [],
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
      :model="toolForm"
      :rules="formRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <h4 class="mk-title-decoration mb-4">基本信息</h4>
      <el-form-item label="名称" prop="name">
        <div class="flex w-full items-center gap-3">
          <!-- // TODO 头像 统一修改组件-->
          <ToolIcon :size="32" />
          <el-input
            v-model="toolForm.name"
            maxlength="64"
            placeholder="请输入工具名称"
            show-word-limit
            @blur="toolForm.name = toolForm.name.trim()"
          />
        </div>
      </el-form-item>
      <el-form-item label="描述">
        <el-input
          v-model="toolForm.desc"
          :autosize="{ minRows: 3 }"
          maxlength="128"
          placeholder="请输入"
          show-word-limit
          type="textarea"
          @blur="toolForm.desc = toolForm.desc.trim()"
        />
      </el-form-item>

      <!-- 启动参数 -->
      <InitFieldTable v-model="toolForm.init_field_list" class="mb-6" />
      <!-- 输入参数 -->
      <InputFieldTable v-model="toolForm.input_field_list" class="mb-6" />

      <ToolCodeSetting v-model="toolForm.code" class="mb-6" show-generate />
      <section>
        <div class="mb-4 flex items-center gap-2">
          <h4 class="mk-title-decoration">输出参数</h4>
          <span class="text-N600">使用工具时显示</span>
        </div>
        <div class="rounded-md bg-N100! px-3 py-2">结果 {result}</div>
      </section>
    </el-form>

    <template #footer>
      <el-button plain :disabled="loading || formLoading" @click="handleBeforeClose"
        >取消</el-button
      >
      <el-button plain :disabled="loading || formLoading" @click="handleOpenDebug">调试</el-button>
      <el-button type="primary" :disabled="formLoading" :loading="loading" @click="handleSubmit">
        {{ editId ? '保存' : '创建' }}
      </el-button>
    </template>

    <ToolDebugDrawer ref="debugDrawerRef" :api="api" />
  </MkDrawer>
</template>
