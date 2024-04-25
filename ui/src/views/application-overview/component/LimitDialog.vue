<template>
  <el-dialog title="访问限制" v-model="dialogVisible">
    <el-form label-position="top" ref="limitFormRef" :model="form">
      <el-form-item label="显示知识来源" @click.prevent>
        <el-switch size="small" v-model="form.show_source"></el-switch>
      </el-form-item>
      <el-form-item label="客户端提问限制">
        <el-input-number
          v-model="form.access_num"
          :min="0"
          :step="1"
          controls-position="right"
          step-strictly
        />
        <span class="ml-4">次 / 天</span>
      </el-form-item>
      <el-form-item label="白名单" @click.prevent>
        <el-switch size="small" v-model="form.white_active"></el-switch>
      </el-form-item>
      <el-form-item>
        <el-input
          v-model="form.white_list"
          placeholder="请输入允许嵌入第三方的源地址，一行一个，如：
http://127.0.0.1:5678
https://dataease.io"
          :rows="10"
          type="textarea"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submit(limitFormRef)" :loading="loading">
          保存
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import applicationApi from '@/api/application'
import { MsgSuccess, MsgConfirm } from '@/utils/message'

const route = useRoute()
const {
  params: { id }
} = route

const emit = defineEmits(['refresh'])

const limitFormRef = ref()
const form = ref<any>({
  show_source: false,
  access_num: 0,
  white_active: true,
  white_list: ''
})

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      show_source: false,
      access_num: 0,
      white_active: true,
      white_list: ''
    }
  }
})

const open = (data: any) => {
  form.value.show_source = data.show_source
  form.value.access_num = data.access_num
  form.value.white_active = data.white_active
  form.value.white_list = data.white_list?.length ? data.white_list?.join('\n') : ''
  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      const obj = {
        show_source: form.value.show_source,
        white_list: form.value.white_list ? form.value.white_list.split('\n') : [],
        white_active: form.value.white_active,
        access_num: form.value.access_num
      }
      applicationApi.putAccessToken(id as string, obj, loading).then((res) => {
        emit('refresh')
        MsgSuccess('设置成功')
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope>
.embed-dialog {
  .code {
    color: var(--app-text-color) !important;
    background: var(--app-layout-bg-color);
    font-weight: 400;
    font-size: 13px;
    white-space: pre;
    height: 180px;
  }
}
</style>
