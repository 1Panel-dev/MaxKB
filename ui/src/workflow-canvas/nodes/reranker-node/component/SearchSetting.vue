<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { RerankerSetting } from '../types'

defineOptions({ name: 'RerankerSearchSetting' })
const setting = defineModel<RerankerSetting>({ required: true })
const visible = ref(false)
const formRef = useTemplateRef<FormInstance>('formRef')
const defaultForm: RerankerSetting = { top_n: 3, similarity: 0, max_paragraph_char_number: 5000 }
const formData = ref<RerankerSetting>(cloneDeep(defaultForm))

function resetData() {
  formData.value = cloneDeep(defaultForm)
  formRef.value?.clearValidate()
}
function open() {
  resetData()
  formData.value = { ...cloneDeep(defaultForm), ...cloneDeep(setting.value) }
  visible.value = true
}
function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    setting.value = cloneDeep(formData.value)
    visible.value = false
  })
}
</script>

<template>
  <el-button text type="primary" title="参数设置" @click="open">
    <MkIcon name="icon_setting" :size="20" />
  </el-button>
  <MkDialog v-model="visible" align-center title="参数设置" width="550" @closed="resetData">
    <el-form ref="formRef" :model="formData" label-position="top" @submit.prevent>
      <div class="grid grid-cols-2 gap-4">
        <el-form-item>
          <template #label>
            <span class="flex items-center gap-1">
              Score 高于
              <el-tooltip content="Score 越高相关性越强。" placement="right"><MkIcon name="icon_info_outlined" class="text-N600!" /></el-tooltip>
            </span>
          </template>
          <el-input-number
            v-model="formData.similarity"
            :min="0"
            :max="formData.search_mode === 'blend' ? 2 : 1"
            :precision="3"
            :step="0.1"
            :value-on-clear="0"
            controls-position="right"
            align="left"
          />
        </el-form-item>
        <el-form-item label="引用分段数 TOP">
          <el-input-number
            v-model="formData.top_n"
            :min="1"
            :max="10000"
            :value-on-clear="1"
            controls-position="right"
            align="left"
          />
        </el-form-item>
      </div>
      <el-form-item label="最大引用字符数">
        <MkSlider v-model="formData.max_paragraph_char_number" show-input :min="500" :max="100000" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit">保存</el-button>
    </template>
  </MkDialog>
</template>
