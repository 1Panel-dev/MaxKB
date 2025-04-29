<template>
  <el-dialog
    align-center
    :title="$t('common.paramSetting')"
    class="param-dialog"
    v-model="dialogVisible"
    style="width: 550px"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-scrollbar max-height="550">
      <div class="p-16">
        <el-form label-position="top" ref="paramFormRef" :model="form">
          <el-form-item :label="$t('views.application.applicationForm.dialog.selectSearchMode')">
            <el-radio-group
              v-model="form.dataset_setting.search_mode"
              class="card__radio"
              @change="changeHandle"
            >
              <el-card
                shadow="never"
                class="mb-16"
                :class="form.search_mode === 'embedding' ? 'active' : ''"
              >
                <el-radio value="embedding" size="large">
                  <p class="mb-4">
                    {{ $t('views.application.applicationForm.dialog.vectorSearch') }}
                  </p>
                  <el-text type="info">{{
                    $t('views.application.applicationForm.dialog.vectorSearchTooltip')
                  }}</el-text>
                </el-radio>
              </el-card>
              <el-card
                shadow="never"
                class="mb-16"
                :class="form.dataset_setting.search_mode === 'keywords' ? 'active' : ''"
              >
                <el-radio value="keywords" size="large">
                  <p class="mb-4">
                    {{ $t('views.application.applicationForm.dialog.fullTextSearch') }}
                  </p>
                  <el-text type="info">{{
                    $t('views.application.applicationForm.dialog.fullTextSearchTooltip')
                  }}</el-text>
                </el-radio>
              </el-card>
              <el-card
                shadow="never"
                :class="form.dataset_setting.search_mode === 'blend' ? 'active' : ''"
              >
                <el-radio value="blend" size="large">
                  <p class="mb-4">
                    {{ $t('views.application.applicationForm.dialog.hybridSearch') }}
                  </p>
                  <el-text type="info">{{
                    $t('views.application.applicationForm.dialog.hybridSearchTooltip')
                  }}</el-text>
                </el-radio>
              </el-card>
            </el-radio-group>
          </el-form-item>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item>
                <template #label>
                  <div class="flex align-center">
                    <span class="mr-4">{{
                      $t('views.application.applicationForm.dialog.similarityThreshold')
                    }}</span>
                    <el-tooltip
                      effect="dark"
                      :content="$t('views.application.applicationForm.dialog.similarityTooltip')"
                      placement="right"
                    >
                      <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                    </el-tooltip>
                  </div>
                </template>
                <el-input-number
                  v-model="form.dataset_setting.similarity"
                  :min="0"
                  :max="form.dataset_setting.search_mode === 'blend' ? 2 : 1"
                  :precision="3"
                  :step="0.1"
                  :value-on-clear="0"
                  controls-position="right"
                  class="w-full"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('views.application.applicationForm.dialog.topReferences')">
                <el-input-number
                  v-model="form.dataset_setting.top_n"
                  :min="1"
                  :max="10000"
                  :value-on-clear="1"
                  controls-position="right"
                  class="w-full"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item :label="$t('views.application.applicationForm.dialog.maxCharacters')">
            <el-slider
              v-model="form.dataset_setting.max_paragraph_char_number"
              show-input
              :show-input-controls="false"
              :min="500"
              :max="100000"
              class="custom-slider"
            />
          </el-form-item>

          <el-form-item
            v-if="!isWorkflowType"
            :label="$t('views.application.applicationForm.dialog.noReferencesAction')"
          >
            <el-form
              label-position="top"
              ref="noReferencesformRef"
              :model="noReferencesform"
              :rules="noReferencesRules"
              :hide-required-asterisk="true"
              class="w-full"
            >
              <el-radio-group
                v-model="form.dataset_setting.no_references_setting.status"
                class="radio-block-avatar"
              >
                <el-radio value="ai_questioning">
                  <p>
                    {{ $t('views.application.applicationForm.dialog.continueQuestioning') }}
                  </p>
                </el-radio>

                <el-radio value="designated_answer">
                  <p>{{ $t('views.application.applicationForm.dialog.provideAnswer') }}</p>
                  <el-form-item
                    v-if="form.dataset_setting.no_references_setting.status === 'designated_answer'"
                    prop="designated_answer"
                  >
                    <el-input
                      v-model="noReferencesform.designated_answer"
                      :rows="2"
                      type="textarea"
                      maxlength="2048"
                      :placeholder="defaultValue['designated_answer']"
                    />
                  </el-form-item>
                </el-radio>
              </el-radio-group>
            </el-form>
          </el-form-item>

          <el-form-item @click.prevent v-if="!isWorkflowType">
            <template #label>
              <div class="flex align-center">
                <span class="mr-4">{{
                  $t('views.application.applicationForm.form.problemOptimization.label')
                }}</span>
              </div>
            </template>
            <el-switch size="small" v-model="form.problem_optimization"></el-switch>
          </el-form-item>
          <el-form-item
            v-if="form.problem_optimization"
            :label="$t('views.application.applicationForm.form.prompt.label')"
          >
            <el-input
              v-model="form.problem_optimization_prompt"
              :rows="6"
              type="textarea"
              maxlength="2048"
              :placeholder="defaultPrompt"
            />
          </el-form-item>
        </el-form>
      </div>
    </el-scrollbar>

    <template #footer>
      <span class="dialog-footer p-16">
        <el-button @click.prevent="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit(noReferencesformRef)" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { isWorkFlow } from '@/utils/application'
import { t } from '@/locales'
const emit = defineEmits(['refresh'])

const paramFormRef = ref()
const noReferencesformRef = ref()

const defaultValue = {
  ai_questioning: '{question}',
  // @ts-ignore
  designated_answer: t('views.application.applicationForm.dialog.designated_answer')
}

const defaultPrompt =
  t('views.application.applicationForm.dialog.defaultPrompt1', {
    question: '{question}'
  }) +
  '<data></data>' +
  t('views.application.applicationForm.dialog.defaultPrompt2')

const form = ref<any>({
  dataset_setting: {
    search_mode: 'embedding',
    top_n: 3,
    similarity: 0.6,
    max_paragraph_char_number: 5000,
    no_references_setting: {
      status: 'ai_questioning',
      value: '{question}'
    }
  },
  problem_optimization: false,
  problem_optimization_prompt: defaultPrompt
})

const noReferencesform = ref<any>({
  ai_questioning: defaultValue['ai_questioning'],
  designated_answer: defaultValue['designated_answer']
})

const noReferencesRules = reactive<FormRules<any>>({
  ai_questioning: [
    {
      required: true,
      message: t('views.application.applicationForm.form.aiModel.placeholder'),
      trigger: 'blur'
    }
  ],
  designated_answer: [
    {
      required: true,
      message: t('views.application.applicationForm.form.prompt.requiredMessage'),
      trigger: 'blur'
    }
  ]
})

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

const isWorkflowType = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      dataset_setting: {
        search_mode: 'embedding',
        top_n: 3,
        similarity: 0.6,
        max_paragraph_char_number: 5000,
        no_references_setting: {
          status: 'ai_questioning',
          value: '{question}'
        }
      },
      problem_optimization: false,
      problem_optimization_prompt: ''
    }
    noReferencesform.value = {
      ai_questioning: defaultValue['ai_questioning'],
      designated_answer: defaultValue['designated_answer']
    }
    noReferencesformRef.value?.clearValidate()
  }
})

const open = (data: any, type?: string) => {
  isWorkflowType.value = isWorkFlow(type)
  form.value = {
    dataset_setting: { ...data.dataset_setting },
    problem_optimization: data.problem_optimization,
    problem_optimization_prompt: data.problem_optimization_prompt
  }
  if (!isWorkflowType.value) {
    noReferencesform.value[form.value.dataset_setting.no_references_setting.status] =
      form.value.dataset_setting.no_references_setting.value
  }

  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (isWorkflowType.value) {
    delete form.value['no_references_setting']
    emit('refresh', form.value)
    dialogVisible.value = false
  } else {
    if (!formEl) return
    await formEl.validate((valid, fields) => {
      if (valid) {
        form.value.dataset_setting.no_references_setting.value =
          noReferencesform.value[form.value.dataset_setting.no_references_setting.status]
        emit('refresh', form.value)
        dialogVisible.value = false
      }
    })
  }
}

function changeHandle(val: string) {
  if (val === 'keywords') {
    form.value.dataset_setting.similarity = 0
  } else {
    form.value.dataset_setting.similarity = 0.6
  }
}

defineExpose({ open })
</script>
<style lang="scss"></style>
