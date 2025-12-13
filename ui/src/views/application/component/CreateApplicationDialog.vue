<template>
  <el-dialog
    :title="
      isWorkFlow(applicationForm.type)
        ? $t('views.application.createWorkFlowApplication')
        : $t('views.application.createApplication')
    "
    v-model="dialogVisible"
    width="650"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form
      ref="applicationFormRef"
      :model="applicationForm"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="$t('common.name')" prop="name">
        <el-input
          v-model="applicationForm.name"
          maxlength="64"
          :placeholder="$t('views.application.form.appName.placeholder')"
          show-word-limit
          @blur="applicationForm.name = applicationForm.name?.trim()"
        />
      </el-form-item>
      <el-form-item :label="$t('common.desc')">
        <el-input
          v-model="applicationForm.desc"
          type="textarea"
          :placeholder="$t('views.application.form.appDescription.placeholder')"
          :rows="3"
          maxlength="256"
          show-word-limit
        />
      </el-form-item>

      <el-form-item
        :label="$t('views.document.upload.template')"
        v-if="applicationForm.type === 'WORK_FLOW'"
      >
        <div class="w-full">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-card
                class="template-radio-card cursor text-center flex-center"
                shadow="never"
                @click="selectedType('blank')"
                :class="appTemplate === 'blank' ? 'active' : ''"
              >
                <div class="flex-center p-24">
                  <AppIcon iconName="app-add-outlined" class="mr-12"></AppIcon>
                  {{ $t('views.application.form.appTemplate.blankApp.title') }}
                </div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <CardBox
                :title="$t('views.application.form.appTemplate.assistantApp.title')"
                :description="$t('views.application.form.appTemplate.assistantApp.description')"
                shadow="never"
                class="template-radio-card cursor"
                :class="appTemplate === 'assistant' ? 'active' : ''"
                @click="selectedType('assistant')"
              >
                <template #icon>
                  <LogoIcon height="32px" />
                </template>
              </CardBox>
            </el-col>
          </el-row>
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false" :loading="loading">
          {{ $t('common.cancel') }}
        </el-button>
        <el-button type="primary" @click="submitHandle(applicationFormRef)" :loading="loading">
          {{ $t('common.create') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { ApplicationFormType } from '@/api/type/application'
import type { FormInstance, FormRules } from 'element-plus'
import applicationApi from '@/api/application/application'
import { MsgSuccess, MsgAlert } from '@/utils/message'
import { isWorkFlow } from '@/utils/application'
import { baseNodes } from '@/workflow/common/data'
import { applicationTemplate } from '@/workflow/common/template'
import { t } from '@/locales'
import useStore from '@/stores'
const { user } = useStore()
const router = useRouter()
const emit = defineEmits(['refresh'])

const defaultPrompt = t('views.application.form.prompt.defaultPrompt', {
  data: '{data}',
  question: '{question}',
})

const optimizationPrompt =
  t('views.application.dialog.defaultPrompt1', {
    question: '{question}',
  }) +
  '<data></data>' +
  t('views.application.dialog.defaultPrompt2')

const workflowDefault = ref<any>({
  edges: [],
  nodes: baseNodes,
})
const appTemplate = ref('blank')

const applicationFormRef = ref()

const loading = ref(false)
const dialogVisible = ref<boolean>(false)

const applicationForm = ref<ApplicationFormType>({
  name: '',
  desc: '',
  model_id: undefined,
  dialogue_number: 1,
  prologue: t('views.application.form.defaultPrologue'),
  knowledge_id_list: [],
  knowledge_setting: {
    top_n: 3,
    similarity: 0.6,
    max_paragraph_char_number: 5000,
    search_mode: 'embedding',
    no_references_setting: {
      status: 'ai_questioning',
      value: '{question}',
    },
  },
  model_setting: {
    prompt: defaultPrompt,
    system: '',
    no_references_prompt: '{question}',
  },
  model_params_setting: {},
  problem_optimization: false,
  problem_optimization_prompt: optimizationPrompt,
  stt_model_id: undefined,
  tts_model_id: undefined,
  stt_model_enable: false,
  tts_model_enable: false,
  tts_type: 'BROWSER',
  type: 'SIMPLE',
})

const rules = reactive<FormRules<ApplicationFormType>>({
  name: [
    {
      required: true,
      message: t('views.application.form.appName.placeholder'),
      trigger: 'blur',
    },
  ],
  model_id: [
    {
      required: false,
      message: t('views.application.form.aiModel.placeholder'),
      trigger: 'change',
    },
  ],
})

const currentFolder = ref('')

watch(dialogVisible, (bool) => {
  if (!bool) {
    applicationForm.value = {
      name: '',
      desc: '',
      model_id: undefined,
      dialogue_number: 1,
      prologue: t('views.application.form.defaultPrologue'),
      knowledge_id_list: [],
      knowledge_setting: {
        top_n: 3,
        similarity: 0.6,
        max_paragraph_char_number: 5000,
        search_mode: 'embedding',
        no_references_setting: {
          status: 'ai_questioning',
          value: '{question}',
        },
      },
      model_setting: {
        prompt: defaultPrompt,
        system: '',
        no_references_prompt: '{question}',
      },
      model_params_setting: {},
      problem_optimization: false,
      problem_optimization_prompt: optimizationPrompt,
      stt_model_id: undefined,
      tts_model_id: undefined,
      stt_model_enable: false,
      tts_model_enable: false,
      tts_type: 'BROWSER',
      type: 'SIMPLE',
    }
    applicationFormRef.value?.clearValidate()
  }
})

const open = (folder: string, type?: string) => {
  currentFolder.value = folder
  applicationForm.value.type = type || 'SIMPLE'
  dialogVisible.value = true
}

const submitHandle = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      if (isWorkFlow(applicationForm.value.type)) {
        workflowDefault.value.nodes[0].properties.node_data.desc = applicationForm.value.desc
        workflowDefault.value.nodes[0].properties.node_data.name = applicationForm.value.name
        applicationForm.value['work_flow'] = workflowDefault.value
      }
      loading.value = true
      applicationApi
        .postApplication({ ...applicationForm.value, folder_id: currentFolder.value })
        .then((res) => {
          return user.profile().then(() => {
            return res
          })
        })
        .then((res) => {
          MsgSuccess(t('common.createSuccess'))
          emit('refresh')
          if (isWorkFlow(applicationForm.value.type)) {
            router.push({ path: `/application/workspace/${res.data.id}/workflow` })
          } else {
            router.push({ path: `/application/workspace/${res.data.id}/${res.data.type}/setting` })
          }
          dialogVisible.value = false
        })
        .finally(() => {
          loading.value = false
        })
    }
  })
}

function selectedType(type: string) {
  appTemplate.value = type
  workflowDefault.value = applicationTemplate[type]
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
