<template>
  <el-dialog
    align-center
    :title="$t('views.application.applicationForm.dialogues.paramSettings')"
    class="param-dialog"
    v-model="dialogVisible"
    style="width: 550px"
    append-to-body
  >
    <div class="dialog-max-height">
      <el-scrollbar always>
        <div class="p-16">
          <el-form label-position="top" ref="paramFormRef" :model="form">
            <el-form-item
              :label="$t('views.application.applicationForm.dialogues.selectSearchMode')"
            >
              <el-radio-group v-model="form.search_mode" class="card__radio" @change="changeHandle">
                <el-card
                  shadow="never"
                  class="mb-16"
                  :class="form.search_mode === 'embedding' ? 'active' : ''"
                >
                  <el-radio value="embedding" size="large">
                    <p class="mb-4">
                      {{ $t('views.application.applicationForm.dialogues.vectorSearch') }}
                    </p>
                    <el-text type="info">{{
                      $t('views.application.applicationForm.dialogues.vectorSearchTooltip')
                    }}</el-text>
                  </el-radio>
                </el-card>
                <el-card
                  shadow="never"
                  class="mb-16"
                  :class="form.search_mode === 'keywords' ? 'active' : ''"
                >
                  <el-radio value="keywords" size="large">
                    <p class="mb-4">
                      {{ $t('views.application.applicationForm.dialogues.fullTextSearch') }}
                    </p>
                    <el-text type="info">{{
                      $t('views.application.applicationForm.dialogues.fullTextSearchTooltip')
                    }}</el-text>
                  </el-radio>
                </el-card>
                <el-card shadow="never" :class="form.search_mode === 'blend' ? 'active' : ''">
                  <el-radio value="blend" size="large">
                    <p class="mb-4">
                      {{ $t('views.application.applicationForm.dialogues.hybridSearch') }}
                    </p>
                    <el-text type="info">{{
                      $t('views.application.applicationForm.dialogues.hybridSearchTooltip')
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
                        $t('views.application.applicationForm.dialogues.similarityThreshold')
                      }}</span>
                      <el-tooltip effect="dark" content="相似度越高相关性越强。" placement="right">
                        <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                      </el-tooltip>
                    </div>
                  </template>
                  <el-input-number
                    v-model="form.similarity"
                    :min="0"
                    :max="form.search_mode === 'blend' ? 2 : 1"
                    :precision="3"
                    :step="0.1"
                    :value-on-clear="0"
                    controls-position="right"
                    class="w-full"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item
                  :label="$t('views.application.applicationForm.dialogues.topReferences')"
                >
                  <el-input-number
                    v-model="form.top_n"
                    :min="1"
                    :max="100"
                    :value-on-clear="1"
                    controls-position="right"
                    class="w-full"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item :label="$t('views.application.applicationForm.dialogues.maxCharacters')">
              <el-slider
                v-model="form.max_paragraph_char_number"
                show-input
                :show-input-controls="false"
                :min="500"
                :max="100000"
                class="custom-slider"
              />
            </el-form-item>
            <el-form-item
              v-if="!isWorkflowType"
              :label="$t('views.application.applicationForm.dialogues.noReferencesAction')"
            >
              <el-form
                label-position="top"
                ref="noReferencesformRef"
                :model="noReferencesform"
                :rules="noReferencesRules"
                class="w-full"
                :hide-required-asterisk="true"
              >
                <el-radio-group
                  v-model="form.no_references_setting.status"
                  class="radio-block mb-16"
                >
                  <div>
                    <el-radio value="ai_questioning">
                      <p>
                        {{ $t('views.application.applicationForm.dialogues.continueQuestioning') }}
                      </p>
                      <el-form-item
                        v-if="form.no_references_setting.status === 'ai_questioning'"
                        :label="$t('views.application.applicationForm.form.prompt.label')"
                        prop="ai_questioning"
                      >
                        <el-input
                          v-model="noReferencesform.ai_questioning"
                          :rows="2"
                          type="textarea"
                          maxlength="2048"
                          :placeholder="defaultValue['ai_questioning']"
                        />
                      </el-form-item>
                    </el-radio>
                  </div>
                  <div class="mt-8">
                    <el-radio value="designated_answer">
                      <p>{{ $t('views.application.applicationForm.dialogues.provideAnswer') }}</p>
                      <el-form-item
                        v-if="form.no_references_setting.status === 'designated_answer'"
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
                  </div>
                </el-radio-group>
              </el-form>
            </el-form-item>
          </el-form>
        </div>
      </el-scrollbar>
    </div>
    <template #footer>
      <span class="dialog-footer p-16">
        <el-button @click.prevent="dialogVisible = false">{{
          $t('views.application.applicationForm.buttons.cancel')
        }}</el-button>
        <el-button type="primary" @click="submit(noReferencesformRef)" :loading="loading">
          {{ $t('views.application.applicationForm.buttons.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import { isWorkFlow } from '@/utils/application'
import { t } from '@/locales'
const emit = defineEmits(['refresh'])

const paramFormRef = ref()
const noReferencesformRef = ref()

const defaultValue = {
  ai_questioning: '{question}',
  // @ts-ignore
  designated_answer: t('views.application.applicationForm.dialogues.designated_answer')
}

const form = ref<any>({
  search_mode: 'embedding',
  top_n: 3,
  similarity: 0.6,
  max_paragraph_char_number: 5000,
  no_references_setting: {
    status: 'ai_questioning',
    value: '{question}'
  }
})

const noReferencesform = ref<any>({
  ai_questioning: defaultValue['ai_questioning'],
  designated_answer: defaultValue['designated_answer']
})

const noReferencesRules = reactive<FormRules<any>>({
  ai_questioning: [
    {
      required: true,
      message: t('views.application.applicationForm.dialogues.promptPlaceholder'),
      trigger: 'blur'
    }
  ],
  designated_answer: [
    {
      required: true,
      message: t('views.application.applicationForm.dialogues.concentPlaceholder'),
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
      search_mode: 'embedding',
      top_n: 3,
      similarity: 0.6,
      max_paragraph_char_number: 5000,
      no_references_setting: {
        status: 'ai_questioning',
        value: ''
      }
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
  form.value = { ...form.value, ...cloneDeep(data) }
  noReferencesform.value[form.value.no_references_setting.status] =
    form.value.no_references_setting.value
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
        form.value.no_references_setting.value =
          noReferencesform.value[form.value.no_references_setting.status]
        emit('refresh', form.value)
        dialogVisible.value = false
      }
    })
  }
}

function changeHandle(val: string) {
  if (val === 'keywords') {
    form.value.similarity = 0
  } else {
    form.value.similarity = 0.6
  }
}

defineExpose({ open })
</script>
<style lang="scss" scope>
.param-dialog {
  padding: 8px 8px 24px 8px;
  .el-dialog__header {
    padding: 16px 16px 0 16px;
  }
  .el-dialog__body {
    padding: 0 !important;
  }
  .dialog-max-height {
    height: 550px;
  }
  .custom-slider {
    .el-input-number.is-without-controls .el-input__wrapper {
      padding: 0 !important;
    }
  }
}
</style>
