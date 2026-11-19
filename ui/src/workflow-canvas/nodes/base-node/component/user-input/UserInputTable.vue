<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ApiInputField, UserInputSetting } from '../../types'
import type { FormField } from '@/components/mk-dynamics-form'
import { DYNAMIC_FORM_TYPES } from '@/components/mk-dynamics-form'
import UserInputFieldDialog from './UserInputFieldDialog.vue'
import UserInputSettingDialog from './UserInputSettingDialog.vue'
import { exposedInputTypes } from './constant'
import { MsgError } from '@/utils/message'

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ apiFields: ApiInputField[]; nodeId: string }>()
const inputFields = defineModel<FormField[]>({ required: true })
const setting = defineModel<UserInputSetting>('setting', { required: true })
const fieldDialogRef = useTemplateRef<InstanceType<typeof UserInputFieldDialog>>('fieldDialogRef')
const settingDialogRef = useTemplateRef<InstanceType<typeof UserInputSettingDialog>>('settingDialogRef')

function formatDefaultValue(field: FormField) {
  if (field.input_type === 'PasswordInput' && field.default_value) return '******'
  if (Array.isArray(field.default_value)) return field.default_value.join('、')
  return String(field.default_value ?? '')
}

function openFieldDialog(field?: FormField, index?: number) {
  fieldDialogRef.value?.open(field, index)
}

function getTypeLabel(inputType: string) {
  const definition = DYNAMIC_FORM_TYPES.find(({ value }) => value === inputType)
  return definition ? definition.label : inputType
}

// 用户输入与接口传参共用参数命名空间。
function saveField(data: FormField, index?: number) {
  if (
    inputFields.value.some((field, fieldIndex) => field.field === data.field && fieldIndex !== index) ||
    props.apiFields.some(({ variable }) => variable === data.field)
  ) {
    MsgError(`${t('workflow.parameters.duplicateMessage')}：${data.field}`)
    return
  }
  const fields = cloneDeep(inputFields.value)
  if (index === undefined) fields.push(cloneDeep(data))
  else fields.splice(index, 1, cloneDeep(data))
  inputFields.value = fields
  if (!exposedInputTypes.includes(data.input_type)) removeExposedField(data.field)
  fieldDialogRef.value?.close()
}

// 删除字段时同步移除直接展示设置。
function deleteField(index: number) {
  const fields = cloneDeep(inputFields.value)
  const [removed] = fields.splice(index, 1)
  inputFields.value = fields
  if (removed) removeExposedField(removed.field)
}

function removeExposedField(field: string) {
  const nextSetting = cloneDeep(setting.value)
  nextSetting.exposed_fields = nextSetting.exposed_fields.filter((exposedField) => exposedField !== field)
  setting.value = nextSetting
}
</script>

<template>
  <div class="w-full">
    <div class="flex-between">
      <span>{{ t('workflow.userInput.title') }}</span>
      <div class="flex-align-center">
        <!-- 配置用户输入展示 -->
        <el-button text type="primary" @click="settingDialogRef?.open(setting)">
          <MkIcon name="icon_setting" />
        </el-button>
        <!-- 添加用户输入参数 -->
        <el-button text type="primary" @click="openFieldDialog()">
          <MkIcon name="icon_add_outlined" />
        </el-button>
      </div>
    </div>
    <MkTable class="mt-2 border" v-if="inputFields.length" v-model:data="inputFields" sortable size="small" row-key="field" :max-height="undefined">
      <el-table-column prop="field" :label="t('dynamicForm.fields.parameter.label')">
        <template #default="{ row }">
          <span :title="row.field" class="block truncate">{{ row.field }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('dynamicForm.fields.displayName.label')">
        <template #default="{ row }">
          <span class="block truncate" :title="row.label.label" v-if="row.label && row.label.input_type === 'TooltipLabel'">
            {{ row.label.label }}
          </span>
          <span class="block truncate" :title="row.label" v-else>{{ row.label }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('dynamicForm.fields.inputType.label')" width="110">
        <template #default="{ row }">
          <el-tag size="small" type="info">{{ getTypeLabel(row.input_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('dynamicForm.fields.defaultValue.label')">
        <template #default="{ row }">
          <span :title="formatDefaultValue(row)" class="block truncate">{{ formatDefaultValue(row) }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('dynamicForm.fields.required.columnLabel')" width="90">
        <template #default="{ row }"><el-switch :model-value="Boolean(row.required)" disabled size="small" /></template>
      </el-table-column>
      <el-table-column :label="t('common.labels.operation')" width="80">
        <template #default="{ row, $index }">
          <!-- 编辑用户输入参数 -->
          <el-button text type="primary" @click="openFieldDialog(row, $index)"><MkIcon name="icon_edit_outlined" /></el-button>
          <!-- 删除用户输入参数 -->
          <el-button text type="primary" @click="deleteField($index)"><MkIcon name="icon_delete-trash_outlined" /></el-button>
        </template>
      </el-table-column>
    </MkTable>
  </div>

  <UserInputFieldDialog ref="fieldDialogRef" :form-fields="inputFields" :node-id="props.nodeId" @submit="saveField" />
  <UserInputSettingDialog ref="settingDialogRef" :fields="inputFields" @submit="setting = $event" />
</template>
