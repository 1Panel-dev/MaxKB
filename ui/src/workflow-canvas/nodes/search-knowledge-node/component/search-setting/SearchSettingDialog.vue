<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import { KNOWLEDGE_SEARCH_MODE } from '@/api/enums'
import { defaultSearchSetting, searchModeOptions } from '../../config'
import type { KnowledgeSearchSetting } from '../../types'

const emit = defineEmits<{ submit: [setting: KnowledgeSearchSetting] }>()
const visible = ref(false)
const formData = ref<KnowledgeSearchSetting>(cloneDeep(defaultSearchSetting))
const formRef = useTemplateRef<FormInstance>('formRef')
const maxSimilarity = computed(() => (formData.value.search_mode === KNOWLEDGE_SEARCH_MODE.BLEND ? 2 : 1))
const rules = computed<FormRules<KnowledgeSearchSetting>>(() => ({
  search_mode: [{ required: true, message: '请选择检索模式', trigger: 'change' }],
  similarity: [
    { required: true, type: 'number', min: 0, max: maxSimilarity.value, message: `相似度范围为 0–${maxSimilarity.value}`, trigger: 'change' },
  ],
  top_n: [{ required: true, type: 'integer', min: 1, max: 10000, message: '引用分段数范围为 1–10000', trigger: 'change' }],
  max_paragraph_char_number: [
    { required: true, type: 'integer', min: 500, max: 100000, message: '最多引用字符数范围为 500–100000', trigger: 'change' },
  ],
}))

function resetData() {
  formData.value = cloneDeep(defaultSearchSetting)
  formRef.value?.clearValidate()
}

function open(setting: KnowledgeSearchSetting) {
  resetData()
  formData.value = cloneDeep(setting)
  visible.value = true
}

// 与旧版保持一致：全文检索重置为 0，向量和混合检索重置为 0.6。
function changeSearchMode() {
  formData.value.similarity = formData.value.search_mode === KNOWLEDGE_SEARCH_MODE.KEYWORDS ? 0 : 0.6
}

function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    emit('submit', cloneDeep(formData.value))
    visible.value = false
  })
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="参数设置" width="550" @closed="resetData">
    <el-form ref="formRef" :model="formData" :rules="rules" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="检索模式" prop="search_mode">
        <el-radio-group v-model="formData.search_mode" class="w-full flex-col gap-3" @change="changeSearchMode">
          <el-radio
            v-for="option in searchModeOptions"
            :key="option.value"
            :value="option.value"
            class="m-0! h-auto! w-full rounded-md border p-3!"
            :class="{ 'border-primary': formData.search_mode === option.value }"
          >
            <span class="block">{{ option.label }}</span>
            <span class="mt-1 block whitespace-normal text-sm text-N600">{{ option.description }}</span>
          </el-radio>
        </el-radio-group>
      </el-form-item>
      <div class="grid grid-cols-2 gap-3">
        <el-form-item label="相似度高于" prop="similarity">
          <el-input-number
            v-model="formData.similarity"
            :min="0"
            :max="maxSimilarity"
            :precision="3"
            :step="0.1"
            :value-on-clear="0"
            controls-position="right"
            class="w-full!"
          />
        </el-form-item>
        <el-form-item label="引用分段数 TOP" prop="top_n">
          <el-input-number
            v-model="formData.top_n"
            :min="1"
            :max="10000"
            :precision="0"
            :value-on-clear="1"
            controls-position="right"
            class="w-full!"
          />
        </el-form-item>
      </div>
      <el-form-item label="最多引用字符数" prop="max_paragraph_char_number">
        <el-slider v-model="formData.max_paragraph_char_number" show-input :show-input-controls="false" :min="500" :max="100000" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit">保存</el-button>
    </template>
  </MkDialog>
</template>
