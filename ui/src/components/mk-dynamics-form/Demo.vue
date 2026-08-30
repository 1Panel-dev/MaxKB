<script setup lang="ts">
import { ref, computed, provide } from 'vue'
import { ElMessage } from 'element-plus'
import type { Dict } from '@/api/types'
import { dynamicFormTypeOptions, MkDynamicsForm, MkDynamicsFormConstructor, type DynamicFormValue, type FormField, type VisibilityFieldOption } from '@/components/mk-dynamics-form'
import modelAPI from '@/api/admin/workspace/model/model'

defineOptions({ name: 'MkDynamicsFormDemo' })
provide('getSelectModelList', modelAPI.getModelList)
provide('getModelParamsForm', modelAPI.getModelParamsForm)
const constructorRef = ref<InstanceType<typeof MkDynamicsFormConstructor>>()
const dynamicsFormRef = ref<InstanceType<typeof MkDynamicsForm>>()

const formFieldList = ref<FormField[]>([])
const formData = ref<Dict<DynamicFormValue>>({})
const dialogVisible = ref(false)
const isEdit = ref(false)
const editIndex = ref(-1)
const currentField = ref<Partial<FormField>>({})

// 「当前表单」作用域的可引用字段，根据已配置字段动态生成
const visibilityFieldOptions = computed<VisibilityFieldOption[]>(() => [
  {
    label: '当前表单',
    value: 'self-form',
    self: true,
    children: formFieldList.value
      .filter((_, index) => index !== editIndex.value) // 排除正在编辑的字段，避免自引用
      .map((item) => ({ label: getFieldLabel(item), value: item.field, input_type: item.input_type, option_list: item.option_list, attrs: item.attrs })),
  },
])

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

const openAddDialog = () => {
  isEdit.value = false
  editIndex.value = -1
  currentField.value = {}
  dialogVisible.value = true
}

const openEditDialog = (row: FormField, index: number) => {
  isEdit.value = true
  editIndex.value = index
  currentField.value = { ...row }
  dialogVisible.value = true
}

const deleteField = (index: number) => {
  formFieldList.value.splice(index, 1)
}

const submitField = async () => {
  try {
    await constructorRef.value?.validate()
    const data = constructorRef.value?.getData()
    if (!data) return

    // 检查字段名是否重复
    const isDuplicate = formFieldList.value.some((item, index) => item.field === data.field && index !== editIndex.value)
    if (isDuplicate) {
      ElMessage.error(`参数 "${data.field}" 已存在`)
      return
    }

    if (isEdit.value && editIndex.value >= 0) {
      formFieldList.value.splice(editIndex.value, 1, data)
    } else {
      formFieldList.value.push(data)
    }
    dialogVisible.value = false
  } catch {
    // 验证失败
  }
}

const validateForm = async () => {
  try {
    await dynamicsFormRef.value?.validate()
    ElMessage.success('校验通过')
  } catch {
    ElMessage.error('校验失败')
  }
}
</script>
<template>
  <div class="p-16" style="height: calc(100vh - 120px)">
    <el-row :gutter="16" style="height: 100%">
      <el-col :span="12">
        <el-card shadow="never" style="height: 100%">
          <template #header>
            <div class="flex-between">
              <span class="font-bold">表单字段列表</span>
              <el-button type="primary" link @click="openAddDialog">
                <MkIcon name="icon_add_outlined" />
                <span>添加</span>
              </el-button>
            </div>
          </template>
          <el-table :data="formFieldList" row-key="field" v-if="formFieldList.length > 0">
            <el-table-column prop="field" label="参数" width="120" show-overflow-tooltip> </el-table-column>
            <el-table-column prop="label" label="显示名称" show-overflow-tooltip>
              <template #default="{ row }">
                <span>{{ getFieldLabel(row) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="input_type" label="组件类型" width="100">
              <template #default="{ row }">
                <el-tag size="small" type="info">{{ getTypeLabel(row.input_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="required" label="必填" width="70" align="center">
              <template #default="{ row }">
                <el-switch size="small" v-model="row.required" disabled />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row, $index }">
                <el-button type="primary" text @click="openEditDialog(row, $index)">
                  <MkIcon name="icon_edit_outlined" />
                </el-button>
                <el-button type="danger" text @click="deleteField($index)">
                  <MkIcon name="icon_delete-trash_outlined" />
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="暂无字段，请点击添加" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" style="height: 100%">
          <template #header>
            <div class="flex-between">
              <span class="font-bold">表单预览</span>
              <el-button type="primary" @click="validateForm">校验</el-button>
            </div>
          </template>
          <MkDynamicsForm
            v-if="formFieldList.length > 0"
            ref="dynamicsFormRef"
            v-model="formData"
            :render-data="formFieldList"
            label-position="top"
            require-asterisk-position="right"
          />
          <el-empty v-else description="请先添加表单字段" />
        </el-card>
      </el-col>
    </el-row>
  </div>

  <!-- 添加/编辑字段弹窗 -->
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
</template>
