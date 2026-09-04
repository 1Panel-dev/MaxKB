<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { Delete, Edit, Setting } from '@element-plus/icons-vue'
import { MkDynamicsFormConstructor, dynamicFormTypeOptions, type FormField, type VisibilityFieldOption } from '@/components/mk-dynamics-form'
import { MsgError } from '@/utils/message'
import type { ApiInputField, UserInputSetting } from '../../types'

defineOptions({ name: 'BaseNodeUserInput' })

const props = defineProps<{
  apiFields: ApiInputField[]
  fields: FormField[]
  nodeId: string
  setting: UserInputSetting
}>()
const emit = defineEmits<{
  'update:fields': [fields: FormField[]]
  'update:setting': [setting: UserInputSetting]
}>()

const fieldDialogVisible = ref(false)
const settingDialogVisible = ref(false)
const editingIndex = ref<number>()
const constructorRef = useTemplateRef<InstanceType<typeof MkDynamicsFormConstructor>>('constructorRef')
const currentField = ref<Partial<FormField>>({ input_type: 'TextInput', required: false, show_default_value: true })
const currentSetting = ref<UserInputSetting>({ exposed_fields: [], menu_title: '更多设置' })

const exposedInputTypes = ['TextInput', 'TextareaInput', 'PasswordInput', 'SingleSelect', 'MultiSelect', 'DatePicker', 'SwitchInput']
const exposedFieldOptions = computed(() => props.fields.filter(({ input_type }) => exposedInputTypes.includes(input_type)))
const visibilityOptions = computed<VisibilityFieldOption[]>(() => [
  {
    children: props.fields
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
    value: props.nodeId,
  },
])

function formatLabel(label: FormField['label'], fallback = '') {
  return typeof label === 'string' ? label : (label?.label ?? fallback)
}

function formatDefaultValue(field: FormField) {
  if (field.input_type === 'PasswordInput' && field.default_value) return '******'
  if (Array.isArray(field.default_value)) return field.default_value.join('、')
  return String(field.default_value ?? '')
}

function openFieldDialog(field?: FormField, index?: number) {
  editingIndex.value = index
  currentField.value = cloneDeep(field ?? { input_type: 'TextInput', required: false, show_default_value: true })
  fieldDialogVisible.value = true
}

function submitField() {
  constructorRef.value?.validate().then(() => {
    const field = constructorRef.value?.getData()
    if (!field?.field || !/^[a-zA-Z0-9_]+$/.test(field.field)) {
      MsgError('参数仅支持字母、数字和下划线')
      return
    }
    const duplicated =
      props.fields.some((item, index) => item.field === field.field && index !== editingIndex.value) ||
      props.apiFields.some(({ variable }) => variable === field.field)
    if (duplicated) {
      MsgError(`参数已存在：${field.field}`)
      return
    }

    const fields = [...props.fields]
    if (editingIndex.value === undefined) fields.push(field)
    else fields.splice(editingIndex.value, 1, field)
    emit('update:fields', fields)
    if (!exposedInputTypes.includes(field.input_type)) removeExposedField(field.field)
    fieldDialogVisible.value = false
  })
}

function deleteField(index: number) {
  const fields = [...props.fields]
  const [removed] = fields.splice(index, 1)
  emit('update:fields', fields)
  if (removed) removeExposedField(removed.field)
}

function removeExposedField(field: string) {
  const setting = cloneDeep(props.setting)
  setting.exposed_fields = setting.exposed_fields.filter((exposedField) => exposedField !== field)
  emit('update:setting', setting)
}

function openSettingDialog() {
  currentSetting.value = cloneDeep(props.setting)
  settingDialogVisible.value = true
}

function submitSetting() {
  emit('update:setting', cloneDeep(currentSetting.value))
  settingDialogVisible.value = false
}
</script>

<template>
  <section>
    <div class="flex-between mb-3">
      <p>用户输入</p>
      <div class="flex items-center">
        <el-button text type="primary" title="用户输入设置" @click="openSettingDialog">
          <MkIcon :icon="Setting" />
        </el-button>
        <el-button text type="primary" @click="openFieldDialog()">
          <MkIcon name="icon_add_outlined" />
        </el-button>
      </div>
    </div>
    <el-table v-if="fields.length" :data="fields" class="mb-4" table-layout="fixed">
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
          <el-button link type="primary" title="编辑" @click="openFieldDialog(row, $index)"><MkIcon :icon="Edit" /></el-button>
          <el-button link type="danger" title="删除" @click="deleteField($index)"><MkIcon :icon="Delete" /></el-button>
        </template>
      </el-table-column>
    </el-table>
  </section>

  <MkDialog v-model="fieldDialogVisible" :title="editingIndex === undefined ? '添加用户输入参数' : '编辑用户输入参数'" width="700">
    <MkDynamicsFormConstructor
      ref="constructorRef"
      v-model="currentField"
      enable-visibility
      :left-options="visibilityOptions"
      label-position="top"
      require-asterisk-position="right"
    />
    <template #footer>
      <el-button @click="fieldDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitField">{{ editingIndex === undefined ? '添加' : '保存' }}</el-button>
    </template>
  </MkDialog>

  <MkDialog v-model="settingDialogVisible" title="用户输入设置" width="520">
    <el-form :model="currentSetting" label-position="top" @submit.prevent>
      <el-form-item label="直接展示的参数">
        <el-select v-model="currentSetting.exposed_fields" class="w-full" multiple :multiple-limit="3" placeholder="最多选择 3 个参数">
          <el-option v-for="field in exposedFieldOptions" :key="field.field" :label="formatLabel(field.label, field.field)" :value="field.field" />
        </el-select>
      </el-form-item>
      <el-form-item label="其余参数菜单标题">
        <el-input v-model="currentSetting.menu_title" maxlength="64" show-word-limit />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="settingDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitSetting">保存</el-button>
    </template>
  </MkDialog>
</template>
