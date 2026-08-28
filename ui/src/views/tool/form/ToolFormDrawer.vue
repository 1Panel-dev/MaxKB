<script setup lang="ts">
import { reactive, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import type { ToolInitField, ToolInputField, ToolItem } from '@/api/types'
import ToolApi from '@/api/admin/workspace/tool/tool'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import ToolDebugDrawer from '../ToolDebugDrawer.vue'
import InitFieldTable from './components/init-field/InitFieldTable.vue'
import InputFieldTable from './components/input-field/InputFieldTable.vue'
import ToolCodeSetting from './components/python-code/CodeSetting.vue'

defineOptions({ name: 'ToolFormDrawer' })

defineProps<{
  title: string
  folderId: string
}>()

const emit = defineEmits<{
  refresh: []
}>()

interface ToolFormModel {
  desc: string
  code: ''
  icon: ''
  init_field_list: ToolInitField[]
  input_field_list: ToolInputField[]
  name: string
}

const formRef = ref<FormInstance>()

const visible = ref(false)
const loading = ref(false)
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
    const request = editId.value
      ? ToolApi.putTool(editId.value, toolForm)
      : ToolApi.postTool(toolForm)

    request
      .then(() => {
        MsgSuccess(editId.value ? '保存成功' : '创建成功')
        visible.value = false
        emit('refresh')
      })
      .finally(() => {
        loading.value = false
      })
  })
}

// 调试

const debugDrawerRef = ref<InstanceType<typeof ToolDebugDrawer>>()
function handleOpenDebug() {
  formRef.value?.validate((valid) => {
    if (valid) {
      // TODO
    }
  })
}

function open(tool?: ToolItem) {
  if (tool) {
    editId.value = tool.id
    Object.assign(toolForm, cloneDeep(tool))
  }
  visible.value = true
  originalForm.value = JSON.stringify(toolForm)
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
  formRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDrawer
    v-model="visible"
    :before-close="handleBeforeClose"
    :title="title"
    size="60%"
    @closed="resetData"
  >
    <el-form
      ref="formRef"
      v-loading="loading"
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
          placeholder="请输入描述"
          show-word-limit
          type="textarea"
          @blur="toolForm.desc = toolForm.desc.trim()"
        />
      </el-form-item>

      <!-- 启动参数 -->
      <InitFieldTable v-model="toolForm.init_field_list" class="mb-6" />
      <!-- 输入参数 -->
      <InputFieldTable v-model="toolForm.input_field_list" class="mb-6" />

      <ToolCodeSetting v-model="toolForm.code" class="mb-6" />
      <section>
        <div class="mb-4 flex items-center gap-2">
          <h4 class="mk-title-decoration">输出参数</h4>
          <span class="text-N600">使用工具时显示</span>
        </div>
        <div class="rounded-md bg-N100! px-3 py-2">结果 {result}</div>
      </section>
    </el-form>

    <template #footer>
      <el-button :disabled="loading" @click="handleBeforeClose">取消</el-button>
      <el-button :disabled="loading" @click="handleOpenDebug">调试</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        {{ editId ? '保存' : '创建' }}
      </el-button>
    </template>

    <ToolDebugDrawer ref="debugDrawerRef" />
  </MkDrawer>
</template>
