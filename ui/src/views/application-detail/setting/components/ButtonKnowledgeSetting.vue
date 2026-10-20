<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import { KNOWLEDGE_SEARCH_MODE } from '@/api/enums'
import { KNOWLEDGE_SEARCH_MODE_OPTIONS } from '@/constants/knowledge'
import { createSettings, DEFAULT_DESIGNATED_ANSWER, DEFAULT_PROBLEM_OPTIMIZATION_PROMPT, type ApplicationSettings } from '../settings'

defineOptions({ name: 'ButtonKnowledgeSetting' })

const props = defineProps<{ setting: ApplicationSettings }>()
const emit = defineEmits<{ submit: [settings: Partial<ApplicationSettings>] }>()
const visible = ref(false)
const formData = ref(createSettings())
const noReferenceAnswers = ref<Record<string, string>>({ ai_questioning: '{question}', designated_answer: DEFAULT_DESIGNATED_ANSWER })
function changeNoReferenceStatus(status: string | number | boolean | undefined) {
  formData.value.knowledge_setting.no_references_setting.value = noReferenceAnswers.value[String(status)] ?? '{question}'
}
const formRef = useTemplateRef<FormInstance>('formRef')
function open() {
  formData.value = cloneDeep(props.setting)
  const responseSetting = props.setting.knowledge_setting.no_references_setting
  const answer = responseSetting.value || noReferenceAnswers.value[responseSetting.status] || '{question}'
  noReferenceAnswers.value[responseSetting.status] = answer
  formData.value.knowledge_setting.no_references_setting.value = answer
  visible.value = true
}
// 全文检索切换为 0，其余模式恢复为 0.6，与工作流参数设置保持一致。
function changeSearchMode() {
  formData.value.knowledge_setting.similarity = formData.value.knowledge_setting.search_mode === KNOWLEDGE_SEARCH_MODE.KEYWORDS ? 0 : 0.6
}
function submit() {
  formRef.value?.validate((valid) => {
    if (!valid) return
    const settings = formData.value
    emit(
      'submit',
      cloneDeep({
        knowledge_setting: settings.knowledge_setting,
        problem_optimization: settings.problem_optimization,
        problem_optimization_prompt: settings.problem_optimization_prompt,
      }),
    )
    visible.value = false
  })
}
function resetData() {
  formRef.value?.clearValidate()
  formData.value = createSettings()
  noReferenceAnswers.value = { ai_questioning: '{question}', designated_answer: DEFAULT_DESIGNATED_ANSWER }
}
</script>

<template>
  <!-- 配置知识库检索参数 -->
  <el-button text type="primary" @click.stop="open">
    <MkIcon name="icon_setting" />
  </el-button>
  <MkDialog v-model="visible" title="参数设置" @closed="resetData" align-center>
    <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="检索模式">
        <!-- 选择检索模式 -->
        <el-radio-group v-model="formData.knowledge_setting.search_mode" class="space-y-2" @change="changeSearchMode">
          <template v-for="mode in KNOWLEDGE_SEARCH_MODE_OPTIONS" :key="mode.value">
            <el-card shadow="hover" class="w-full" :class="{ 'border-primary!': formData.knowledge_setting.search_mode === mode.value }">
              <el-radio :value="mode.value" class="mk-card-radio">
                <h6>{{ mode.label }}</h6>
                <span class="block text-sm text-N600">{{ mode.description }}</span>
              </el-radio>
            </el-card>
          </template>
        </el-radio-group>
      </el-form-item>
      <div class="grid grid-cols-2 gap-3">
        <el-form-item>
          <template #label>
            <span class="flex-align-center gap-1">
              相似度高于
              <MkTooltip content="相似度越高相关性越强。" placement="right"><MkIcon name="icon_info_outlined" class="text-N600!" /></MkTooltip>
            </span>
          </template>
          <el-input-number
            v-model="formData.knowledge_setting.similarity"
            :min="0"
            :max="formData.knowledge_setting.search_mode === KNOWLEDGE_SEARCH_MODE.BLEND ? 2 : 1"
            :step="0.1"
            :precision="3"
            :value-on-clear="0"
            controls-position="right"
            align="left"
          />
        </el-form-item>
        <el-form-item label="召回分段数 TOP">
          <el-input-number
            v-model="formData.knowledge_setting.top_n"
            :min="1"
            :max="10000"
            :precision="0"
            :value-on-clear="1"
            controls-position="right"
            align="left"
          />
        </el-form-item>
      </div>
      <el-form-item label="最多引用字符数">
        <MkSlider v-model="formData.knowledge_setting.max_paragraph_char_number" :min="500" :max="100000" />
      </el-form-item>
      <el-form-item label="无引用知识库分段时">
        <el-radio-group
          :model-value="formData.knowledge_setting.no_references_setting.status"
          @change="changeNoReferenceStatus"
          @update:model-value="formData.knowledge_setting.no_references_setting.status = String($event)"
        >
          <el-radio value="ai_questioning">继续向 AI 提问</el-radio>
          <el-radio value="designated_answer">指定回答</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item
        class="-mt-2"
        v-if="formData.knowledge_setting.no_references_setting.status === 'designated_answer'"
        prop="knowledge_setting.no_references_setting.value"
        :rules="{ required: true, whitespace: true, message: '请输入回答内容', trigger: 'blur' }"
      >
        <el-input
          v-model="formData.knowledge_setting.no_references_setting.value"
          @input="noReferenceAnswers[formData.knowledge_setting.no_references_setting.status] = $event"
          type="textarea"
          :rows="3"
          maxlength="2048"
          :placeholder="DEFAULT_DESIGNATED_ANSWER"
        />
      </el-form-item>
      <el-form-item label="问题优化"><el-switch v-model="formData.problem_optimization" size="small" /></el-form-item>
      <el-form-item v-if="formData.problem_optimization" label="提示词">
        <el-input
          v-model="formData.problem_optimization_prompt"
          type="textarea"
          maxlength="2048"
          :rows="5"
          :placeholder="DEFAULT_PROBLEM_OPTIMIZATION_PROMPT"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消配置 -->
      <el-button plain @click="visible = false">取消</el-button>
      <!-- 确认配置，暂存到页面草稿 -->
      <el-button type="primary" @click="submit">保存</el-button>
    </template>
  </MkDialog>
</template>
