<template>
  <el-drawer v-model="dubugVisible" size="60%" :append-to-body="true">
    <template #header>
      <div class="flex align-center" style="margin-left: -8px">
        <el-button class="cursor mr-4" link @click.prevent="dubugVisible = false">
          <el-icon :size="20">
            <Back />
          </el-icon>
        </el-button>
        <h4>调试</h4>
      </div>
    </template>
    <div>
      <h4 class="title-decoration-1 mb-16">输入变量</h4>
      <el-form
        ref="FormRef"
        :model="form"
        :rules="rules"
        label-position="top"
        require-asterisk-position="right"
        v-loading="loading"
      >
        <el-form-item label="函数名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入函数名称"
            maxlength="64"
            show-word-limit
            @blur="form.name = form.name.trim()"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="form.desc"
            type="textarea"
            placeholder="请输入函数的描述"
            maxlength="128"
            show-word-limit
            :autosize="{ minRows: 3 }"
            @blur="form.desc = form.desc.trim()"
          />
        </el-form-item>
      </el-form>

      <h4 class="title-decoration-1 mb-16 mt-16">
        输出变量 <el-text type="info" class="color-secondary"> 使用函数时显示 </el-text>
      </h4>
      <div class="flex-between border-r-4 p-8-12 mb-8 layout-bg lighter">
        <span>结果 {result}</span>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'

import type { functionLibData } from '@/api/type/function-lib'
import functionLibApi from '@/api/function-lib'
import type { FormInstance } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import { cloneDeep } from 'lodash'

const emit = defineEmits(['refresh'])
const FieldFormDialogRef = ref()

const FormRef = ref()

const isEdit = ref(false)
const loading = ref(false)
const dubugVisible = ref(false)
const showEditor = ref(false)
const currentIndex = ref<any>(null)

const form = ref<functionLibData>({
  name: '',
  desc: '',
  code: '',
  input_field_list: []
})

watch(dubugVisible, (bool) => {
  if (!bool) {
    isEdit.value = false
    showEditor.value = true
    currentIndex.value = null
    form.value = {
      name: '',
      desc: '',
      code: '',
      input_field_list: []
    }
  }
})

const rules = reactive({
  name: [{ required: true, message: '请输入函数名称', trigger: 'blur' }]
})

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid: any) => {
    if (valid) {
      if (isEdit.value) {
        functionLibApi.putFunctionLib(form.value?.id as string, form.value, loading).then((res) => {
          MsgSuccess('编辑成功')
          emit('refresh', res.data)
          dubugVisible.value = false
        })
      } else {
        functionLibApi.postFunctionLib(form.value, loading).then((res) => {
          MsgSuccess('创建成功')
          emit('refresh')
          dubugVisible.value = false
        })
      }
    }
  })
}

const open = (data: any) => {
  if (data) {
    isEdit.value = true
    form.value = cloneDeep(data)
  }
  dubugVisible.value = true
}

defineExpose({
  open
})
</script>
<style lang="scss"></style>
