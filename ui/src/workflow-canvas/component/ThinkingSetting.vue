<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { ReasoningSettingData } from '@/workflow-canvas/types'

defineOptions({ name: 'ThinkingSetting' })

const setting = defineModel<ReasoningSettingData>({ required: true })

// 思考过程配置：打开时创建草稿，校验通过后写回。
const visible = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const formData = ref<ReasoningSettingData>({
  reasoning_content_enable: false,
  reasoning_content_end: '</think>',
  reasoning_content_start: '<think>',
})

function open() {
  resetData()
  formData.value = cloneDeep(setting.value)
  visible.value = true
}

function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    setting.value = cloneDeep(formData.value)
    visible.value = false
  })
}

function resetData() {
  formData.value = {
    reasoning_content_enable: false,
    reasoning_content_end: '</think>',
    reasoning_content_start: '<think>',
  }
  formRef.value?.clearValidate()
}
</script>

<template>
  <el-button text type="primary" @click="open">
    <MkIcon name="icon_setting" />
  </el-button>
  <MkDialog v-model="visible" title="设置" @closed="resetData">
    <template #subtitle> 请根据模型返回的思考标签设置，标签中间的内容将会认定为思考过程</template>
    <el-form ref="formRef" :model="formData" class="grid grid-cols-2 gap-4" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="开始">
        <el-input v-model="formData.reasoning_content_start" type="textarea" :rows="5" placeholder="<think>" />
      </el-form-item>
      <el-form-item label="结束">
        <el-input v-model="formData.reasoning_content_end" type="textarea" :rows="5" placeholder="</think>" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit">保存</el-button>
    </template>
  </MkDialog>
</template>
