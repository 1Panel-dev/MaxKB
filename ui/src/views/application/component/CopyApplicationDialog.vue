<template>
  <el-dialog
    :title="$t('views.application.copyApplication')"
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
      <el-form-item :label="$t('views.application.form.appName.label')" prop="name">
        <el-input
          v-model="applicationForm.name"
          maxlength="64"
          :placeholder="$t('views.application.form.appName.placeholder')"
          show-word-limit
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
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false" :loading="loading">
          {{ $t('common.cancel') }}
        </el-button>
        <el-button type="primary" @click="submitHandle(applicationFormRef)" :loading="loading">
          {{ $t('common.copy') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { cloneDeep } from 'lodash'
import type { ApplicationFormType } from '@/api/type/application'
import type { FormInstance, FormRules } from 'element-plus'
import applicationApi from '@/api/application/application'
import { MsgSuccess, MsgAlert } from '@/utils/message'
import { isWorkFlow } from '@/utils/application'
import { t } from '@/locales'
import useStore from '@/stores'
const router = useRouter()
const { common, user } = useStore()

const defaultPrompt = t('views.application.form.prompt.defaultPrompt', {
  data: '{data}',
  question: '{question}',
})
const applicationFormRef = ref()

const loading = ref(false)
const dialogVisible = ref<boolean>(false)

const applicationForm = ref<ApplicationFormType>({
  name: '',
  desc: '',
  model_id: '',
  dialogue_number: 0,
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
  },
  problem_optimization: false,
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
})

const currentFolder = ref('')

watch(dialogVisible, (bool) => {
  if (!bool) {
    applicationForm.value = {
      name: '',
      desc: '',
      model_id: '',
      dialogue_number: 0,
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
      },
      problem_optimization: false,
      type: 'SIMPLE',
    }
    applicationFormRef.value?.clearValidate()
  }
})

const open = (data: any, folder: string) => {
  currentFolder.value = folder
  const obj = cloneDeep(data)
  delete obj['id']
  obj['name'] = obj['name'] + ` ${t('common.copyTitle')}`
  applicationForm.value = obj
  dialogVisible.value = true
}

const submitHandle = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      applicationApi
        .postApplication({ ...applicationForm.value, folder_id: currentFolder.value }, loading)
        .then((res) => {
          return user.profile().then(() => {
            return res
          })
        })
        .then((res) => {
          MsgSuccess(t('common.createSuccess'))
          if (isWorkFlow(applicationForm.value.type)) {
            router.push({ path: `/application/workspace/${res.data.id}/workflow` })
          } else {
            router.push({ path: `/application/workspace/${res.data.id}/${res.data.type}/setting` })
          }
          dialogVisible.value = false
        })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
