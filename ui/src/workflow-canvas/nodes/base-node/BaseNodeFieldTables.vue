<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import { Delete, Edit, Setting } from '@element-plus/icons-vue'
import { MkDynamicsFormConstructor, dynamicFormTypeOptions, type FormField, type VisibilityFieldOption } from '@/components/mk-dynamics-form'
import { MsgError } from '@/utils/message'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { ApiInputField, ChatInputField, UserInputField } from './types'

defineOptions({ name: 'BaseNodeFieldTables' })

const props = defineProps<{ nodeModel: WorkflowNodeModel }>()
const nodeModel = props.nodeModel

const userDialogVisible = ref(false)
const apiDialogVisible = ref(false)
const chatDialogVisible = ref(false)
const settingsDialogVisible = ref(false)
const editingIndex = ref<number>()
const userConstructorRef = useTemplateRef<InstanceType<typeof MkDynamicsFormConstructor>>('userConstructorRef')
const apiFormRef = useTemplateRef<FormInstance>('apiFormRef')
const chatFormRef = useTemplateRef<FormInstance>('chatFormRef')

const userFields = computed<UserInputField[]>({
  get: () => (nodeModel.properties.user_input_field_list ?? []) as UserInputField[],
  set: (fields) => (nodeModel.properties.user_input_field_list = fields),
})
const apiFields = computed<ApiInputField[]>({
  get: () => (nodeModel.properties.api_input_field_list ?? []) as ApiInputField[],
  set: (fields) => (nodeModel.properties.api_input_field_list = fields),
})
const chatFields = computed<ChatInputField[]>({
  get: () => (nodeModel.properties.chat_input_field_list ?? []) as ChatInputField[],
  set: (fields) => (nodeModel.properties.chat_input_field_list = fields),
})

const currentUserField = ref<Partial<FormField>>({ input_type: 'TextInput', required: false, show_default_value: true })
const currentApiField = ref<ApiInputField>(createApiField())
const currentChatField = ref<ChatInputField>({ field: '', label: '' })
const userInputSetting = ref({ exposed_fields: [] as string[], menu_title: '更多设置' })

const exposedInputTypes = ['TextInput', 'TextareaInput', 'PasswordInput', 'SingleSelect', 'MultiSelect', 'DatePicker', 'SwitchInput']
const exposedFieldOptions = computed(() => userFields.value.filter(({ input_type }) => exposedInputTypes.includes(input_type)))
const visibilityOptions = computed<VisibilityFieldOption[]>(() => [
  {
    children: userFields.value
      .filter((_field, index) => index !== editingIndex.value)
      .map((field) => ({
        attrs: field.attrs,
        input_type: field.input_type,
        label: formatLabel(field.label, field.field),
        option_list: field.option_list,
        value: field.field,
      })),
    label: '当前表单',
    self: true,
    value: nodeModel.id,
  },
])

function createApiField(): ApiInputField {
  return { assignment_method: 'api_input', default_value: '', desc: '', is_required: true, type: 'input', variable: '' }
}

function formatLabel(label: FormField['label'], fallback = '') {
  return typeof label === 'string' ? label : (label?.label ?? fallback)
}

function formatDefaultValue(field: UserInputField) {
  if (field.input_type === 'PasswordInput' && field.default_value) return '******'
  if (Array.isArray(field.default_value)) return field.default_value.join('、')
  return String(field.default_value ?? '')
}

function notifyFieldsChanged(eventName = 'refreshFieldList') {
  nodeModel.graphModel.eventCenter.emit(eventName, undefined)
}

function openUserDialog(field?: UserInputField, index?: number) {
  editingIndex.value = index
  currentUserField.value = cloneDeep(field ?? { input_type: 'TextInput', required: false, show_default_value: true })
  userDialogVisible.value = true
}

function submitUserField() {
  userConstructorRef.value?.validate().then(() => {
    const field = userConstructorRef.value?.getData()
    if (!field?.field || !/^[a-zA-Z0-9_]+$/.test(field.field)) {
      MsgError('参数仅支持字母、数字和下划线')
      return
    }
    const duplicated =
      userFields.value.some((item, index) => item.field === field.field && index !== editingIndex.value) ||
      apiFields.value.some(({ variable }) => variable === field.field)
    if (duplicated) {
      MsgError(`参数已存在：${field.field}`)
      return
    }
    const fields = [...userFields.value]
    if (editingIndex.value === undefined) fields.push(field)
    else fields.splice(editingIndex.value, 1, field)
    userFields.value = fields
    if (!exposedInputTypes.includes(field.input_type)) removeExposedField(field.field)
    notifyFieldsChanged()
    userDialogVisible.value = false
  })
}

function deleteUserField(index: number) {
  const fields = [...userFields.value]
  const [removed] = fields.splice(index, 1)
  userFields.value = fields
  if (removed) removeExposedField(removed.field)
  notifyFieldsChanged()
}

function removeExposedField(field: string) {
  const savedSetting = nodeModel.properties.user_input_field_list_setting as typeof userInputSetting.value | undefined
  userInputSetting.value = cloneDeep(savedSetting ?? userInputSetting.value)
  userInputSetting.value.exposed_fields = userInputSetting.value.exposed_fields.filter((item) => item !== field)
  nodeModel.properties.user_input_field_list_setting = cloneDeep(userInputSetting.value)
}

function openSettingsDialog() {
  const savedSetting = nodeModel.properties.user_input_field_list_setting as typeof userInputSetting.value | undefined
  userInputSetting.value = cloneDeep(savedSetting ?? { exposed_fields: [], menu_title: '更多设置' })
  settingsDialogVisible.value = true
}

function submitUserInputSetting() {
  nodeModel.properties.user_input_field_list_setting = cloneDeep(userInputSetting.value)
  settingsDialogVisible.value = false
}

function openApiDialog(field?: ApiInputField, index?: number) {
  editingIndex.value = index
  currentApiField.value = cloneDeep(field ?? createApiField())
  apiDialogVisible.value = true
}

function submitApiField() {
  apiFormRef.value?.validate().then(() => {
    const field = cloneDeep(currentApiField.value)
    const duplicated =
      apiFields.value.some((item, index) => item.variable === field.variable && index !== editingIndex.value) ||
      userFields.value.some(({ field: userField }) => userField === field.variable)
    if (duplicated) {
      MsgError(`参数已存在：${field.variable}`)
      return
    }
    const fields = [...apiFields.value]
    if (editingIndex.value === undefined) fields.push(field)
    else fields.splice(editingIndex.value, 1, field)
    apiFields.value = fields
    notifyFieldsChanged()
    apiDialogVisible.value = false
  })
}

function deleteApiField(index: number) {
  apiFields.value = apiFields.value.filter((_field, fieldIndex) => fieldIndex !== index)
  notifyFieldsChanged()
}

function openChatDialog(field?: ChatInputField, index?: number) {
  editingIndex.value = index
  currentChatField.value = cloneDeep(field ?? { field: '', label: '' })
  chatDialogVisible.value = true
}

function submitChatField() {
  chatFormRef.value?.validate().then(() => {
    const field = cloneDeep(currentChatField.value)
    const duplicated = chatFields.value.some((item, index) => item.field === field.field && index !== editingIndex.value)
    if (duplicated) {
      MsgError(`参数已存在：${field.field}`)
      return
    }
    const fields = [...chatFields.value]
    if (editingIndex.value === undefined) fields.push(field)
    else fields.splice(editingIndex.value, 1, field)
    chatFields.value = fields
    notifyFieldsChanged('chatFieldList')
    chatDialogVisible.value = false
  })
}

function deleteChatField(index: number) {
  chatFields.value = chatFields.value.filter((_field, fieldIndex) => fieldIndex !== index)
  notifyFieldsChanged('chatFieldList')
}
</script>

<template>
  <section>
    <div class="flex-between mb-3">
      <h6>用户输入</h6>
      <div class="flex items-center gap-1">
        <el-button link type="primary" title="用户输入设置" @click="openSettingsDialog">
          <MkIcon :icon="Setting" />
        </el-button>
        <el-button link type="primary" @click="openUserDialog()">
          <MkIcon name="icon_add_outlined" />
          添加
        </el-button>
      </div>
    </div>
    <el-table v-if="userFields.length" :data="userFields" class="mb-4" table-layout="fixed">
      <el-table-column label="参数" prop="field" min-width="110" show-overflow-tooltip />
      <el-table-column label="显示名称" min-width="110" show-overflow-tooltip>
        <template #default="{ row }">{{ formatLabel(row.label, row.field) }}</template>
      </el-table-column>
      <el-table-column label="类型" prop="input_type" min-width="100">
        <template #default="{ row }">{{ dynamicFormTypeOptions.find(({ value }) => value === row.input_type)?.label ?? row.input_type }}</template>
      </el-table-column>
      <el-table-column label="默认值" min-width="90" show-overflow-tooltip>
        <template #default="{ row }">{{ formatDefaultValue(row) }}</template>
      </el-table-column>
      <el-table-column label="必填" width="64">
        <template #default="{ row }"><el-switch v-model="row.required" disabled size="small" /></template>
      </el-table-column>
      <el-table-column label="操作" width="88">
        <template #default="{ row, $index }">
          <el-button link type="primary" title="编辑" @click="openUserDialog(row, $index)"><MkIcon :icon="Edit" /></el-button>
          <el-button link type="danger" title="删除" @click="deleteUserField($index)"><MkIcon :icon="Delete" /></el-button>
        </template>
      </el-table-column>
    </el-table>
  </section>

  <section>
    <div class="flex-between mb-3">
      <h6>API 参数</h6>
      <el-button link type="primary" @click="openApiDialog()"><MkIcon name="icon_add_outlined" />添加</el-button>
    </div>
    <el-table v-if="apiFields.length" :data="apiFields" class="mb-4" table-layout="fixed">
      <el-table-column label="参数" prop="variable" min-width="120" show-overflow-tooltip />
      <el-table-column label="描述" prop="desc" min-width="120" show-overflow-tooltip />
      <el-table-column label="默认值" prop="default_value" min-width="100" show-overflow-tooltip />
      <el-table-column label="必填" width="64">
        <template #default="{ row }"><el-switch v-model="row.is_required" disabled size="small" /></template>
      </el-table-column>
      <el-table-column label="操作" width="88">
        <template #default="{ row, $index }">
          <el-button link type="primary" title="编辑" @click="openApiDialog(row, $index)"><MkIcon :icon="Edit" /></el-button>
          <el-button link type="danger" title="删除" @click="deleteApiField($index)"><MkIcon :icon="Delete" /></el-button>
        </template>
      </el-table-column>
    </el-table>
  </section>

  <section>
    <div class="flex-between mb-3">
      <h6>会话变量</h6>
      <el-button link type="primary" @click="openChatDialog()"><MkIcon name="icon_add_outlined" />添加</el-button>
    </div>
    <el-table v-if="chatFields.length" :data="chatFields" class="mb-4" table-layout="fixed">
      <el-table-column label="参数" prop="field" show-overflow-tooltip />
      <el-table-column label="显示名称" prop="label" show-overflow-tooltip />
      <el-table-column label="操作" width="88">
        <template #default="{ row, $index }">
          <el-button link type="primary" title="编辑" @click="openChatDialog(row, $index)"><MkIcon :icon="Edit" /></el-button>
          <el-button link type="danger" title="删除" @click="deleteChatField($index)"><MkIcon :icon="Delete" /></el-button>
        </template>
      </el-table-column>
    </el-table>
  </section>

  <MkDialog v-model="userDialogVisible" :title="editingIndex === undefined ? '添加用户输入参数' : '编辑用户输入参数'" width="700">
    <MkDynamicsFormConstructor
      ref="userConstructorRef"
      v-model="currentUserField"
      enable-visibility
      :left-options="visibilityOptions"
      label-position="top"
      require-asterisk-position="right"
    />
    <template #footer>
      <el-button @click="userDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitUserField">{{ editingIndex === undefined ? '添加' : '保存' }}</el-button>
    </template>
  </MkDialog>

  <MkDialog v-model="settingsDialogVisible" title="用户输入设置" width="520">
    <el-form :model="userInputSetting" label-position="top" @submit.prevent>
      <el-form-item label="直接展示的参数">
        <el-select v-model="userInputSetting.exposed_fields" class="w-full" multiple :multiple-limit="3" placeholder="最多选择 3 个参数">
          <el-option v-for="field in exposedFieldOptions" :key="field.field" :label="formatLabel(field.label, field.field)" :value="field.field" />
        </el-select>
      </el-form-item>
      <el-form-item label="其余参数菜单标题">
        <el-input v-model="userInputSetting.menu_title" maxlength="64" show-word-limit />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="settingsDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitUserInputSetting">保存</el-button>
    </template>
  </MkDialog>

  <MkDialog v-model="apiDialogVisible" :title="editingIndex === undefined ? '添加 API 参数' : '编辑 API 参数'" width="560">
    <el-form ref="apiFormRef" :model="currentApiField" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item
        label="参数"
        prop="variable"
        :rules="[
          { required: true, message: '请输入参数', trigger: 'blur' },
          { pattern: /^[a-zA-Z0-9_]+$/, message: '仅支持字母、数字和下划线', trigger: 'blur' },
        ]"
      >
        <el-input
          v-model="currentApiField.variable"
          maxlength="64"
          show-word-limit
          @blur="currentApiField.variable = currentApiField.variable.trim()"
        />
      </el-form-item>
      <el-form-item label="描述"><el-input v-model="currentApiField.desc" maxlength="64" show-word-limit /></el-form-item>
      <el-form-item label="是否必填"><el-switch v-model="currentApiField.is_required" size="small" /></el-form-item>
      <el-form-item label="默认值" prop="default_value" :rules="{ required: currentApiField.is_required, message: '请输入默认值', trigger: 'blur' }">
        <el-input v-model="currentApiField.default_value" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="apiDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitApiField">{{ editingIndex === undefined ? '添加' : '保存' }}</el-button>
    </template>
  </MkDialog>

  <MkDialog v-model="chatDialogVisible" :title="editingIndex === undefined ? '添加会话变量' : '编辑会话变量'" width="560">
    <el-form ref="chatFormRef" :model="currentChatField" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item
        label="参数"
        prop="field"
        :rules="[
          { required: true, message: '请输入参数', trigger: 'blur' },
          { pattern: /^[a-zA-Z0-9_]+$/, message: '仅支持字母、数字和下划线', trigger: 'blur' },
        ]"
      >
        <el-input v-model="currentChatField.field" maxlength="64" show-word-limit @blur="currentChatField.field = currentChatField.field.trim()" />
      </el-form-item>
      <el-form-item label="显示名称" prop="label" :rules="{ required: true, message: '请输入显示名称', trigger: 'blur' }">
        <el-input v-model="currentChatField.label" maxlength="64" show-word-limit />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="chatDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitChatField">{{ editingIndex === undefined ? '添加' : '保存' }}</el-button>
    </template>
  </MkDialog>
</template>
