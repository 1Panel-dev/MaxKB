<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { RerankerSetting } from '../types'
import type { FormInstance } from 'element-plus'

defineOptions({ name: 'RerankerSearchSetting' })
const { t } = useI18n({ useScope: 'global' })

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
  <!-- 配置重排参数 -->
  <el-button text type="primary" @click="open">
    <MkIcon name="icon_setting" />
  </el-button>
  <MkDialog v-model="visible" :title="t('common.parameters.settingsTitle')" @closed="resetData">
    <el-form ref="formRef" :model="formData" :validate-on-rule-change="false" label-position="top" @submit.prevent>
      <div class="grid grid-cols-2 gap-4">
        <el-form-item>
          <template #label>
            <span class="flex-align-center gap-1">
              {{ t('workflow.reranker.score.label') }}
              <MkTooltip :content="t('workflow.reranker.score.description')" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </MkTooltip>
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
        <el-form-item :label="t('knowledge.retrieval.topNumber')">
          <el-input-number v-model="formData.top_n" :min="1" :max="10000" :value-on-clear="1" controls-position="right" align="left" />
        </el-form-item>
      </div>
      <el-form-item :label="t('workflow.reranker.maxReferenceCharacters')">
        <MkSlider v-model="formData.max_paragraph_char_number" show-input :min="500" :max="100000" />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消编辑重排参数 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 保存重排参数 -->
      <el-button type="primary" @click="submit">{{ t('common.actions.save') }}</el-button>
    </template>
  </MkDialog>
</template>
