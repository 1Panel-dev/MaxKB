<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { dynamicFormTypeOptions, type FormField } from '@/components/mk-dynamics-form'
import { MsgError } from '@/utils/message'
import type { ApiInputField, UserInputSetting } from '../../types'
import UserInputFieldDialog from './UserInputFieldDialog.vue'
import UserInputSettingDialog from './UserInputSettingDialog.vue'
import { exposedInputTypes } from './constant'

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

// 用户输入与接口传参共用参数命名空间。
function saveField(data: FormField, index?: number) {
  if (
    inputFields.value.some((field, fieldIndex) => field.field === data.field && fieldIndex !== index) ||
    props.apiFields.some(({ variable }) => variable === data.field)
  ) {
    MsgError(`参数已存在：${data.field}`)
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
      <span>用户输入</span>
      <div class="flex items-center">
        <el-button text type="primary" title="用户输入设置" @click="settingDialogRef?.open(setting)">
          <MkIcon name="icon-setting" />
        </el-button>
        <el-button text type="primary" @click="openFieldDialog()">
          <MkIcon name="icon_add_outlined" />
        </el-button>
      </div>
    </div>
    <MkTable class="mt-2 border" v-if="inputFields.length" v-model:data="inputFields" sortable size="small" row-key="field" :max-height="undefined">
      <el-table-column prop="field" label="参数">
        <template #default="{ row }">
          <span :title="row.field" class="block truncate">{{ row.field }}</span>
        </template>
      </el-table-column>
      <el-table-column label="显示名称">
        <template #default="{ row }">
          <span class="block truncate" :title="row.label.label" v-if="row.label && row.label.input_type === 'TooltipLabel'">{{
            row.label.label
          }}</span>
          <span class="block truncate" :title="row.label" v-else>{{ row.label }}</span>
        </template>
      </el-table-column>
      <el-table-column label="组件类型" width="110">
        <template #default="{ row }"
          ><el-tag size="small" type="info">{{
            dynamicFormTypeOptions.find(({ value }) => value === row.input_type)?.label ?? row.input_type
          }}</el-tag></template
        >
      </el-table-column>
      <el-table-column label="默认值">
        <template #default="{ row }">
          <span :title="formatDefaultValue(row)" class="block truncate">{{ formatDefaultValue(row) }}</span></template
        >
      </el-table-column>
      <el-table-column label="必填" width="55">
        <template #default="{ row }"><el-switch :model-value="Boolean(row.required)" disabled size="small" /></template>
      </el-table-column>
      <el-table-column label="操作" width="80">
        <template #default="{ row, $index }">
          <el-button text type="primary" @click="openFieldDialog(row, $index)"><MkIcon name="icon_edit_outlined" /></el-button>
          <el-button text type="primary" @click="deleteField($index)"><MkIcon name="icon_delete-trash_outlined" /></el-button>
        </template>
      </el-table-column>
    </MkTable>
  </div>

  <UserInputFieldDialog ref="fieldDialogRef" :form-fields="inputFields" :node-id="props.nodeId" @submit="saveField" />
  <UserInputSettingDialog ref="settingDialogRef" :fields="inputFields" @submit="setting = $event" />
</template>
