<template>
  <el-dialog
    :title="isEdit ? '编辑变量' : '添加变量'"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    append-to-body
  >
    <el-form
      label-position="top"
      ref="fieldFormRef"
      :rules="rules"
      :model="form"
      require-asterisk-position="right"
    >
      <el-form-item label="变量名" prop="name">
        <el-input
          v-model="form.name"
          placeholder="请输入变量名"
          maxlength="64"
          show-word-limit
          @blur="form.name = form.name.trim()"
        />
      </el-form-item>
      <el-form-item label="变量" prop="variable">
        <el-input
          v-model="form.variable"
          placeholder="请输入变量"
          maxlength="64"
          show-word-limit
          @blur="form.variable = form.variable.trim()"
        />
      </el-form-item>
      <el-form-item label="输入类型">
        <el-select v-model="form.type" @change="changeType">
          <el-option label="文本框" value="input" />
          <el-option label="日期" value="date" />
          <el-option label="下拉选项" value="select" />
        </el-select>
      </el-form-item>
      <el-form-item v-if="form.type === 'select'">
        <template #label>
          <div class="flex-between">
            选项值
            <el-button link type="primary" @click.stop="addOption()">
              <el-icon class="mr-4"><Plus /></el-icon> 添加
            </el-button>
          </div>
        </template>

        <div
          class="w-full flex-between mb-8"
          v-for="(option, $index) in form.optionList"
          :key="$index"
        >
          <el-input v-model="form.optionList[$index]" placeholder="请输入选项值" />
          <el-button link class="ml-8" @click.stop="delOption($index)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </el-form-item>
      <el-form-item label="是否必填" @click.prevent>
        <el-switch size="small" v-model="form.is_required"></el-switch>
      </el-form-item>
      <el-form-item
        label="默认值"
        prop="default_value"
        :rules="{
          required: form.is_required,
          message: '请输入默认值',
          trigger: 'blur'
        }"
      >
        <el-input
          v-if="form.type === 'input'"
          v-model="form.default_value"
          placeholder="请输入默认值"
          @blur="form.name = form.name.trim()"
        />
        <el-date-picker
          v-else-if="form.type === 'date'"
          v-model="form.default_value"
          type="datetime"
          placeholder="选择日期"
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DD HH:mm:ss"
        />
        <el-select
          v-else-if="form.type === 'select'"
          v-model="form.default_value"
          placeholder="请选择"
        >
          <el-option
            v-for="(option, index) in form.optionList"
            :key="index"
            :label="option"
            :value="option"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="赋值方式">
        <el-radio-group v-model="form.assignment_method">
          <el-radio value="user_input">用户输入</el-radio>
          <el-radio value="api_input">接口传参</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submit(fieldFormRef)" :loading="loading">
          {{ isEdit ? '保存' : '添加' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import { cloneDeep, debounce } from 'lodash'
import { MsgError } from '@/utils/message'

const emit = defineEmits(['refresh'])

const fieldFormRef = ref()
const loading = ref<boolean>(false)
const isEdit = ref(false)

const form = ref<any>({
  name: '',
  variable: '',
  type: 'input',
  is_required: true,
  assignment_method: 'user_input',
  optionList: [''],
  default_value: ''
})

const rules = reactive({
  name: [{ required: true, message: '请输入变量名', trigger: 'blur' }],
  variable: [
    { required: true, message: '请输入变量', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '只能输入字母数字和下划线', trigger: 'blur' }
  ]
})

const dialogVisible = ref<boolean>(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      name: '',
      variable: '',
      type: 'input',
      is_required: true,
      assignment_method: 'user_input',
      optionList: [''],
      default_value: ''
    }
    isEdit.value = false
  }
})

const open = (row: any) => {
  if (row) {
    form.value = cloneDeep(row)
    isEdit.value = true
  }

  dialogVisible.value = true
}

const close = () => {
  dialogVisible.value = false
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  if (form.value.type === 'select' && form.value.optionList.length === 0) {
    return MsgError('请添加选项值')
  }
  await formEl.validate((valid) => {
    if (valid) {
      emit('refresh', form.value)
    }
  })
}

const addOption = () => {
  form.value.optionList.push('')
}

const delOption = (index: number) => {
  form.value.optionList.splice(index, 1)
}

const changeType = () => {
  form.value.optionList = ['']
  form.value.default_value = ''
}

defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
