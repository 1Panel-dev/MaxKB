<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import { KNOWLEDGE_SEARCH_MODE } from '@/api/enums'
import { defaultSearchSetting, searchModeOptions } from '../constant'
import type { KnowledgeSearchSetting } from '../types'

defineOptions({ name: 'SearchKnowledgeSetting' })

const setting = defineModel<KnowledgeSearchSetting>({ required: true })
const visible = ref(false)
const formData = ref<KnowledgeSearchSetting>(cloneDeep(defaultSearchSetting))
const formRef = useTemplateRef<FormInstance>('formRef')

function open() {
  resetData()
  formData.value = cloneDeep(setting.value)
  visible.value = true
}

// 与旧版保持一致：全文检索重置为 0，向量和混合检索重置为 0.6。
function changeSearchMode() {
  formData.value.similarity = formData.value.search_mode === KNOWLEDGE_SEARCH_MODE.KEYWORDS ? 0 : 0.6
}

function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    setting.value = cloneDeep(formData.value)
    visible.value = false
  })
}
function resetData() {
  formData.value = cloneDeep(defaultSearchSetting)
  formRef.value?.clearValidate()
}
</script>

<template>
  <el-button text type="primary" title="参数设置" @click="open"><MkIcon name="icon-setting" /></el-button>
  <MkDialog v-model="visible" title="参数设置" @closed="resetData">
    <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="检索模式">
        <el-radio-group v-model="formData.search_mode" class="space-y-2" @change="changeSearchMode">
          <template v-for="option in searchModeOptions" :key="option.value">
            <el-card shadow="hover" class="w-full" :class="{ 'border-primary!': formData.search_mode === option.value }">
              <el-radio :value="option.value" class="mk-card-radio">
                <h6>{{ option.label }}</h6>
                <span class="mt-1 block text-sm text-N600">{{ option.description }}</span>
              </el-radio>
            </el-card>
          </template>
        </el-radio-group>
      </el-form-item>
      <div class="grid grid-cols-2 gap-3">
        <el-form-item label="相似度高于">
          <el-input-number
            v-model="formData.similarity"
            :min="0"
            :max="formData.search_mode === KNOWLEDGE_SEARCH_MODE.BLEND ? 2 : 1"
            :precision="3"
            :step="0.1"
            :value-on-clear="0"
            controls-position="right"
            align="left"
          />
        </el-form-item>
        <el-form-item label="引用分段数 TOP">
          <el-input-number v-model="formData.top_n" :min="1" :max="10000" :precision="0" :value-on-clear="1" controls-position="right" align="left" />
        </el-form-item>
      </div>
      <el-form-item label="最多引用字符数">
        <MkSlider v-model="formData.max_paragraph_char_number" show-input :min="500" :max="100000" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button plain @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit">保存</el-button>
    </template>
  </MkDialog>
</template>
