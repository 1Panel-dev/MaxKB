<template>
  <el-drawer v-model="visible" size="60%" :append-to-body="true">
    <template #header>
      <div class="flex align-center" style="margin-left: -8px">
        <h4>XXX配置</h4>
      </div>
    </template>
    <div>
      <h4 class="title-decoration-1 mb-16">应用信息</h4>
    </div>
    <div>
      <h4 class="title-decoration-1 mb-16">回调地址</h4>
    </div>
    <template #footer>
      <div>
        <el-button>取消</el-button>
        <el-button>测试连接</el-button>
        <el-button type="primary">保存</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import functionLibApi from '@/api/function-lib'
import type { FormInstance } from 'element-plus'

const FormRef = ref()
const loading = ref(false)
const visible = ref(false)
const showResult = ref(false)
const isSuccess = ref(false)
const result = ref('')

const form = ref<any>({
  debug_field_list: [],
  code: ''
})

watch(visible, (bool) => {
  if (!bool) {
    showResult.value = false
    isSuccess.value = false
    result.value = ''
    form.value = {
      debug_field_list: [],
      code: '',
      input_field_list: []
    }
  }
})

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) {
    functionLibApi
      .postFunctionLibDebug(form.value, loading)
      .then((res) => {
        showResult.value = true
        isSuccess.value = true
        result.value = res.data
      })
      .catch((res) => {
        showResult.value = true
        isSuccess.value = false
        result.value = res.data
      })
  } else {
    await formEl.validate((valid: any) => {
      if (valid) {
        functionLibApi.postFunctionLibDebug(form.value, loading).then((res) => {
          if (res.code === 500) {
            showResult.value = true
            isSuccess.value = false
            result.value = res.message
          } else {
            showResult.value = true
            isSuccess.value = true
            result.value = res.data
          }
        })
      }
    })
  }
}

const open = (data: any) => {
  visible.value = true
}

defineExpose({
  open
})
</script>
<style lang="scss"></style>
