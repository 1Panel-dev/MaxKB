<template>
  <NodeContainer :node-model="model">
    <h6 class="mb-3">节点设置</h6>
    <el-card shadow="never" class="card-never">
      <el-form
        ref="formNodeFormRef"
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        hide-required-asterisk
        @submit.prevent
      >
        <el-form-item prop="form_content_format" :rules="{ required: true, message: '请填写表单内容', trigger: 'blur' }">
          <template #label>
            <div class="flex items-center">
              <span class="text-N900">表单内容<span class="text-danger">*</span></span>
              <el-tooltip effect="dark" placement="right">
                <template #content>表单内容中可使用 { form } 占位符来动态插入表单</template>
                <MkIcon name="icon_info_outlined" class="ml-1 cursor-pointer align-middle" />
              </el-tooltip>
            </div>
          </template>
          <el-input
            v-model="form_data.form_content_format"
            :rows="5"
            type="textarea"
            placeholder="请输入表单内容，如：你好，请先填写下面表单内容：
{{form}}"
          />
        </el-form-item>

        <el-form-item @click.prevent>
          <template #label>
            <div class="flex w-full items-center justify-between gap-3">
              <h6 class="font-medium">表单设置</h6>
              <el-button link type="primary" @click="openAddDialog">
                <MkIcon name="icon_add_outlined" class="mr-1" />
                添加
              </el-button>
            </div>
          </template>

          <el-table ref="tableRef" v-if="form_data.form_field_list.length > 0" :data="form_data.form_field_list" row-key="field" class="border">
            <el-table-column prop="field" :label="'参数'" width="100" show-overflow-tooltip>
              <template #default="{ row }">
                <span :title="row.field" class="ellipsis-1">{{ row.field }}</span>
              </template>
            </el-table-column>
            <el-table-column :label="'显示名称'">
              <template #default="{ row }">
                <span :title="getFieldLabel(row)" class="ellipsis-1">{{ getFieldLabel(row) }}</span>
              </template>
            </el-table-column>
            <el-table-column :label="'组件类型'" width="100">
              <template #default="{ row }">
                <el-tag size="small" type="info" class="info-tag">{{ getTypeLabel(row.input_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="'默认值'">
              <template #default="{ row }">
                <span :title="getDefaultValue(row)" class="ellipsis-1">{{ getDefaultValue(row) }}</span>
              </template>
            </el-table-column>
            <el-table-column :label="'必填'" width="55">
              <template #default="{ row }">
                <div @click.stop>
                  <el-switch size="small" :model-value="Boolean(row.required)" />
                </div>
              </template>
            </el-table-column>
            <el-table-column :label="'操作'" width="90">
              <template #default="{ row, $index }">
                <el-button link type="primary" @click="openEditDialog(row, $index)">
                  <MkIcon name="icon_edit_outlined" />
                </el-button>
                <el-button link type="info" @click="deleteField($index)">
                  <MkIcon name="icon_delete-trash_outlined" />
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
    </el-card>

    <MkDialog v-model="dialogVisible" :title="isEdit ? '编辑字段' : '添加字段'" width="600px" append-to-body destroy-on-close>
      <MkDynamicsFormConstructor
        ref="constructorRef"
        v-model="currentField"
        :enable-visibility="true"
        :left-options="visibilityFieldOptions"
        label-position="top"
        require-asterisk-position="right"
      />
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitField">确定</el-button>
      </template>
    </MkDialog>
  </NodeContainer>
</template>
<script setup lang="ts">
import { ref, inject, computed, onMounted, onBeforeUnmount, nextTick, useTemplateRef } from 'vue'
import { set, cloneDeep } from 'lodash'
import Sortable from 'sortablejs'
import type { FormInstance } from 'element-plus'

import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { MkDynamicsFormConstructor, dynamicFormTypeOptions, type FormField, type VisibilityFieldOption } from '@/components/mk-dynamics-form'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { BaseNodeModel } from '@logicflow/core'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'WorkflowFormNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel() as WorkflowNodeModel

const dialogVisible = ref(false)
const isEdit = ref(false)
const editIndex = ref(-1)
const currentField = ref<Partial<FormField>>({})

const getFieldLabel = (row: FormField) => {
  if (typeof row.label !== 'string') {
    return row.label?.label || ''
  }
  return row.label || ''
}

const getTypeLabel = (inputType: string) => {
  const item = dynamicFormTypeOptions.find((i) => i.value === inputType)
  return item ? item.label : inputType
}

const getDefaultValue = (row: FormField) => {
  if (row.default_value === undefined || row.default_value === null) return ''
  if (Array.isArray(row.default_value)) {
    if (!row.option_list) return String(row.default_value)
    return row.option_list
      .filter((v) => (row.default_value as Array<unknown>).includes(v.value))
      .map((v) => v.label)
      .join(',')
  }
  return String(row.default_value)
}

const visibilityFieldOptions = computed<VisibilityFieldOption[]>(() => {
  const selfChildren = form_data.value.form_field_list
    .filter((_, index) => (editIndex.value < 0 ? true : index < editIndex.value))
    .map((field) => ({
      label: getFieldLabel(field),
      value: field.field,
      input_type: field.input_type,
      option_list: field.option_list,
      attrs: field.attrs,
    }))
  return [
    ...model.getUpNodeFieldList(false, true).filter((field) => Boolean(field.children?.length)),
    ...(selfChildren.length
      ? [
          {
            label: String(model.properties.stepName || '表单收集'),
            value: 'self-form',
            self: true,
            children: selfChildren,
          },
        ]
      : []),
  ]
})

const form_data = computed<{ is_result: boolean; form_field_list: FormField[]; form_content_format: string }>({
  get: () => {
    if (!model.properties.node_data) {
      set(model.properties, 'node_data', { is_result: true, form_content_format: '', form_field_list: [] })
    }
    return model.properties.node_data as { is_result: boolean; form_field_list: FormField[]; form_content_format: string }
  },
  set: (value) => {
    set(model.properties, 'node_data', value)
  },
})

const formNodeFormRef = useTemplateRef<FormInstance>('formNodeFormRef')
const constructorRef = useTemplateRef<InstanceType<typeof MkDynamicsFormConstructor>>('constructorRef')
const tableRef = useTemplateRef<{ $el: HTMLElement }>('tableRef')

// 表单字段拖拽排序（对应 v2 的 tableRef + Sortable）
let sortableInstance: Sortable | undefined
function initFieldSortable() {
  destroyFieldSortable()
  const tableEl = tableRef.value?.$el as HTMLElement | undefined
  const tbody = tableEl?.querySelector('.el-table__body-wrapper tbody') as HTMLElement | undefined
  if (!tbody) return
  sortableInstance = Sortable.create(tbody, {
    animation: 150,
    ghostClass: 'ghost-row',
    onEnd: (evt: { oldIndex?: number; newIndex?: number }) => {
      if (evt.oldIndex === undefined || evt.newIndex === undefined) return
      if (evt.oldIndex === evt.newIndex) return
      const items = cloneDeep(form_data.value.form_field_list)
      const [movedItem] = items.splice(evt.oldIndex, 1)
      if (!movedItem) return
      items.splice(evt.newIndex, 0, movedItem)
      set(form_data.value, 'form_field_list', items)
      syncFieldList()
      nextTick(initFieldSortable)
    },
  })
}
function destroyFieldSortable() {
  sortableInstance?.destroy()
  sortableInstance = undefined
}

const openAddDialog = () => {
  isEdit.value = false
  editIndex.value = -1
  currentField.value = {}
  dialogVisible.value = true
}

const openEditDialog = (row: FormField, index: number) => {
  isEdit.value = true
  editIndex.value = index
  currentField.value = { ...cloneDeep(row) }
  dialogVisible.value = true
}

const deleteField = (index: number) => {
  const list = cloneDeep(form_data.value.form_field_list)
  list.splice(index, 1)
  set(form_data.value, 'form_field_list', list)
  syncFieldList()
}

const submitField = async () => {
  try {
    await constructorRef.value?.validate()
    const data = constructorRef.value?.getData()
    if (!data) return

    const isDuplicate = form_data.value.form_field_list.some((item, index) => item.field === data.field && index !== editIndex.value)
    if (isDuplicate) {
      MsgError(`参数 "${data.field}" 已存在`)
      return
    }

    const list = cloneDeep(form_data.value.form_field_list)
    if (isEdit.value && editIndex.value >= 0) {
      list.splice(editIndex.value, 1, data as FormField)
    } else {
      list.push(data as FormField)
    }
    set(form_data.value, 'form_field_list', list)
    syncFieldList()
    dialogVisible.value = false
  } catch {
    //
  }
}

const syncFieldList = () => {
  const fields = [
    { label: '表单全部内容', value: 'form_data' },
    ...form_data.value.form_field_list.map((item) => ({ value: item.field, label: getFieldLabel(item) })),
  ]
  if (!model.properties.config) {
    set(model.properties, 'config', {})
  }
  set(model.properties.config!, 'fields', fields)
  model.clearNextNodeField(true)
  nextTick(initFieldSortable)
}

const validate = () => {
  const vList: Array<Promise<unknown>> = []
  const formResult = formNodeFormRef.value?.validate()
  if (formResult) vList.push(formResult)

  const upstreamNodeFields = model.getUpNodeFieldList(true, true)
  for (const field of form_data.value.form_field_list) {
    for (const cond of field.visibility_rules?.conditions || []) {
      if (!cond.field || cond.field.length < 2 || !cond.field[0] || !cond.field[1]) continue
      if (cond.self) {
        if (!form_data.value.form_field_list.some((f) => f.field === cond.field[1])) {
          vList.push(Promise.reject('引用变量不存在'))
        }
      } else {
        const nodeEntry = upstreamNodeFields.find((n) => n.value === cond.field[0])
        if (!nodeEntry || !nodeEntry.children?.some((c) => c.value === cond.field[1])) {
          vList.push(Promise.reject('引用变量不存在'))
        }
      }
    }
  }
  return Promise.all(vList).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  set(model, 'validate', validate)
  nextTick(initFieldSortable)
})

onBeforeUnmount(() => {
  destroyFieldSortable()
})
</script>
