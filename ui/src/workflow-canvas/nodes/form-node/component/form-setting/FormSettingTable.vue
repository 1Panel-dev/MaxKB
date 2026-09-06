<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { dynamicFormTypeOptions, type FormField, type VisibilityFieldOption } from '@/components/mk-dynamics-form'
import { MsgError } from '@/utils/message'
import FormFieldDialog from './FormFieldDialog.vue'

defineOptions({ name: 'WorkflowFormFieldTable' })

const props = defineProps<{ upstreamFieldOptions: VisibilityFieldOption[]; nodeId: string; nodeName: string }>()
const formFields = defineModel<FormField[]>({ required: true })
const formFieldDialogRef = useTemplateRef<InstanceType<typeof FormFieldDialog>>('formFieldDialogRef')

// 字段展示兼容复合标签与多选默认值。
function getTypeLabel(inputType: string) {
  return dynamicFormTypeOptions.find((option) => option.value === inputType)?.label ?? inputType
}

function getDefaultValue(field: FormField): string {
  const defaultValue: unknown = field.default_value
  if (defaultValue === undefined || defaultValue === null) return ''
  if (Array.isArray(defaultValue) && field.option_list) {
    return field.option_list
      .filter((option) => defaultValue.includes(option.value))
      .map((option) => option.label)
      .join(',')
  }
  return String(defaultValue)
}

// 添加与编辑共用提交入口，重名时保留弹窗内容。
function openFieldDialog(data?: FormField, index?: number) {
  formFieldDialogRef.value?.open(data, index)
}

function deleteField(index: number) {
  formFields.value = cloneDeep(formFields.value.filter((_, fieldIndex) => fieldIndex !== index))
}

function saveField(data: FormField, index?: number) {
  if (formFields.value.some((field, fieldIndex) => field.field === data.field && fieldIndex !== index)) {
    MsgError(`参数 "${data.field}" 已存在`)
    return
  }

  const fields = cloneDeep(formFields.value)
  if (index === undefined) {
    fields.push(cloneDeep(data))
  } else {
    fields.splice(index, 1, cloneDeep(data))
  }
  formFields.value = fields
  formFieldDialogRef.value?.close()
}
</script>

<template>
  <div class="w-full">
    <div class="flex-between mb-2">
      <span>表单配置</span>
      <el-button text type="primary" @click="openFieldDialog()">
        <MkIcon name="icon_add_outlined" />
      </el-button>
    </div>

    <MkTable v-model:data="formFields" sortable size="small" row-key="field" :max-height="undefined" class="border">
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
        <template #default="{ row }">
          <el-tag size="small" type="info">{{ getTypeLabel(row.input_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="默认值">
        <template #default="{ row }">
          <span :title="getDefaultValue(row)" class="block truncate">{{ getDefaultValue(row) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="必填" width="55">
        <template #default="{ row }">
          <div @click.stop>
            <el-switch disabled size="small" :model-value="Boolean(row.required)" />
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="80">
        <template #default="{ row, $index }">
          <el-button text type="primary" aria-label="编辑" @click="openFieldDialog(row, $index)">
            <MkIcon name="icon_edit_outlined" />
          </el-button>
          <el-button text type="primary" aria-label="删除" @click="deleteField($index)">
            <MkIcon name="icon_delete-trash_outlined" />
          </el-button>
        </template>
      </el-table-column>
    </MkTable>

    <FormFieldDialog
      ref="formFieldDialogRef"
      :form-fields="formFields"
      :upstream-field-options="props.upstreamFieldOptions"
      :node-id="props.nodeId"
      :node-name="props.nodeName"
      @submit="saveField"
    />
  </div>
</template>
