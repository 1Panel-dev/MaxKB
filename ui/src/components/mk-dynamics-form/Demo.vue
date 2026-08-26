<template>
  <div class="p-16" style="height: calc(100vh - 120px)">
    <el-row :gutter="16" style="height: 100%">
      <el-col :span="12">
        <el-card shadow="never" style="height: 100%">
        <template #header>
          <div class="flex-between">
            <span class="font-bold">表单字段列表</span>
            <el-button type="primary" link @click="openAddDialog">
              <MkIcon name="icon_add_outlined" class="mr-4" />
              添加
            </el-button>
          </div>
        </template>
        <el-table :data="formItemList" style="width: 100%" row-key="field" v-if="formItemList.length > 0">
          <el-table-column prop="field" label="参数" width="120">
            <template #default="{ row }">
              <span :title="row.field" class="ellipsis-1">{{ row.field }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="label" label="显示名称">
            <template #default="{ row }">
              <span :title="getLabel(row)" class="ellipsis-1">{{ getLabel(row) }}</span>
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
        <DynamicsForm
          v-if="formItemList.length > 0"
          label-position="top"
          require-asterisk-position="right"
          v-model="formData"
          :model="formData"
          :render_data="formItemList"
          ref="dynamicsFormRef"
        />
        <el-empty v-else description="请先添加表单字段" />
      </el-card>
    </el-col>
  </el-row>
  </div>

  <!-- 添加/编辑字段弹窗 -->
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑字段' : '添加字段'"
    width="600px"
    append-to-body
    destroy-on-close
  >
    <DynamicsFormConstructor
      v-model="currentField"
      label-position="top"
      require-asterisk-position="right"
      :enableVisibility="true"
      :leftOptions="leftOptions"
      ref="constructorRef"
    />
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitField">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import DynamicsFormConstructor from '@/components/mk-dynamics-form/constructor/index.vue'
import DynamicsForm from '@/components/mk-dynamics-form/index.vue'
import type { LeftOptions } from '@/components/mk-dynamics-form/constructor/type'
import { input_type_list } from '@/components/mk-dynamics-form/constructor/data'

const constructorRef = ref<InstanceType<typeof DynamicsFormConstructor>>()
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()

const formItemList = ref<Array<any>>([])
const formData = ref<any>({})
const dialogVisible = ref(false)
const isEdit = ref(false)
const editIndex = ref(-1)
const currentField = ref<any>({})

// 「当前表单」作用域的可引用字段，根据已配置字段动态生成
const leftOptions = computed<Array<LeftOptions>>(() => [
  {
    label: '当前表单',
    value: 'self-form',
    self: true,
    children: formItemList.value
      .filter((_, index) => index !== editIndex.value) // 排除正在编辑的字段，避免自引用
      .map((item) => ({
        label: getLabel(item),
        value: item.field,
        input_type: item.input_type,
        option_list: item.option_list,
        attrs: item.attrs,
      })),
  },
])

const getLabel = (row: any) => {
  if (row.label && row.label.input_type === 'TooltipLabel') {
    return row.label.label
  }
  return row.label || ''
}

const getTypeLabel = (inputType: string) => {
  const item = input_type_list.find((i) => i.value === inputType)
  return item ? item.label : inputType
}

const openAddDialog = () => {
  isEdit.value = false
  editIndex.value = -1
  currentField.value = {}
  dialogVisible.value = true
}

const openEditDialog = (row: any, index: number) => {
  isEdit.value = true
  editIndex.value = index
  currentField.value = { ...row }
  dialogVisible.value = true
}

const deleteField = (index: number) => {
  formItemList.value.splice(index, 1)
}

const submitField = async () => {
  try {
    await constructorRef.value?.validate()
    const data = constructorRef.value?.getData()
    if (!data) return

    // 检查字段名是否重复
    const isDuplicate = formItemList.value.some(
      (item, index) => item.field === data.field && index !== editIndex.value
    )
    if (isDuplicate) {
      ElMessage.error(`参数 "${data.field}" 已存在`)
      return
    }

    if (isEdit.value && editIndex.value >= 0) {
      formItemList.value.splice(editIndex.value, 1, data)
    } else {
      formItemList.value.push(data)
    }
    dialogVisible.value = false
  } catch (e) {
    // 验证失败
  }
}

const validateForm = async () => {
  try {
    await dynamicsFormRef.value?.validate()
    ElMessage.success('校验通过')
  } catch (e) {
    ElMessage.error('校验失败')
  }
}
</script>

<style lang="scss" scoped>
.ellipsis-1 {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
