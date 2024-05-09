<template>
  <el-dialog title="设置" v-model="dialogVisible">
    <el-form label-position="top" ref="settingFormRef" :model="form">
      <el-form-item label="允许跨域地址" @click.prevent>
        <el-switch size="small" v-model="form.allow_cross_domain"></el-switch>
      </el-form-item>
      <el-form-item>
        <el-input
          v-model="form.cross_domain_list"
          placeholder="请输入允许的跨域地址，开启后不输入跨域地址则不限制。
跨域地址一行一个，如：
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
        <el-button type="primary" @click="submit(settingFormRef)" :loading="loading">
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
import overviewApi from '@/api/application-overview'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
const route = useRoute()
const {
  params: { id }
} = route

const emit = defineEmits(['refresh'])

const settingFormRef = ref()
const form = ref<any>({
  allow_cross_domain: false,
  cross_domain_list: ''
})

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

const APIKeyId = ref('')

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      allow_cross_domain: false,
      cross_domain_list: ''
    }
  }
})

const open = (data: any) => {
  APIKeyId.value = data.id
  form.value.allow_cross_domain = data.allow_cross_domain
  form.value.cross_domain_list = data.cross_domain_list?.length
    ? data.cross_domain_list?.join('\n')
    : ''
  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      const obj = {
        allow_cross_domain: form.value.allow_cross_domain,
        cross_domain_list: form.value.cross_domain_list
          ? form.value.cross_domain_list.split('\n').filter(function (item: string) {
              return item !== ''
            })
          : []
      }
      overviewApi.putAPIKey(id as string, APIKeyId.value, obj, loading).then((res) => {
        emit('refresh')
        MsgSuccess('设置成功')
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
