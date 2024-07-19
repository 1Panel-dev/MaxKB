<template>
  <el-dialog
    :title="$t('views.application.applicationForm.title.create')"
    v-model="dialogVisible"
    width="650"
    append-to-body
  >
    <el-form
      ref="applicationFormRef"
      :model="applicationForm"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
    >
      <el-form-item :label="$t('views.application.applicationForm.form.appName.label')" prop="name">
        <el-input
          v-model="applicationForm.name"
          maxlength="64"
          :placeholder="$t('views.application.applicationForm.form.appName.placeholder')"
          show-word-limit
        />
      </el-form-item>
      <el-form-item :label="$t('views.application.applicationForm.form.appDescription.label')">
        <el-input
          v-model="applicationForm.desc"
          type="textarea"
          :placeholder="$t('views.application.applicationForm.form.appDescription.placeholder')"
          :rows="3"
          maxlength="256"
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="选择应用类型">
        <el-radio-group v-model="applicationForm.type" class="card__radio">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-card
                shadow="never"
                class="mb-16"
                :class="applicationForm.type === 'SIMPLE' ? 'active' : ''"
              >
                <el-radio value="SIMPLE" size="large">
                  <p class="mb-4">简单配置</p>
                  <el-text type="info">适合新手创建小助手</el-text>
                </el-radio>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card
                shadow="never"
                class="mb-16"
                :class="isWorkFlow(applicationForm.type) ? 'active' : ''"
              >
                <el-radio value="WORK_FLOW" size="large">
                  <p class="mb-4">高级编排</p>
                  <el-text type="info">适合高级用户自定义小助手的工作流</el-text>
                </el-radio>
              </el-card>
            </el-col>
          </el-row>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false" :loading="loading">
          {{ $t('views.application.applicationForm.buttons.cancel') }}
        </el-button>
        <el-button type="primary" @click="submitValid(applicationFormRef)" :loading="loading">
          {{ $t('views.application.applicationForm.buttons.create') }}
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
import applicationApi from '@/api/application'
import { MsgSuccess, MsgAlert } from '@/utils/message'
import { isWorkFlow } from '@/utils/application'
import { t } from '@/locales'
import useStore from '@/stores'
import { ValidType, ValidCount } from '@/enums/common'

const { common, user } = useStore()
const router = useRouter()
const emit = defineEmits(['refresh'])

// @ts-ignore
const defaultPrompt = t('views.application.prompt.defaultPrompt', {
  data: '{data}',
  question: '{question}'
})
const applicationFormRef = ref()

const loading = ref(false)
const dialogVisible = ref<boolean>(false)

const applicationForm = ref<ApplicationFormType>({
  name: '',
  desc: '',
  model_id: '',
  multiple_rounds_dialogue: false,
  prologue: t('views.application.prompt.defaultPrologue'),
  dataset_id_list: [],
  dataset_setting: {
    top_n: 3,
    similarity: 0.6,
    max_paragraph_char_number: 5000,
    search_mode: 'embedding',
    no_references_setting: {
      status: 'ai_questioning',
      value: '{question}'
    }
  },
  model_setting: {
    prompt: defaultPrompt
  },
  problem_optimization: false,
  type: 'SIMPLE'
})

const rules = reactive<FormRules<ApplicationFormType>>({
  name: [
    {
      required: true,
      message: t('views.application.applicationForm.form.appName.placeholder'),
      trigger: 'blur'
    }
  ],
  model_id: [
    {
      required: false,
      message: t('views.application.applicationForm.form.aiModel.placeholder'),
      trigger: 'change'
    }
  ]
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    applicationForm.value = {
      name: '',
      desc: '',
      model_id: '',
      multiple_rounds_dialogue: false,
      prologue: t('views.application.prompt.defaultPrologue'),
      dataset_id_list: [],
      dataset_setting: {
        top_n: 3,
        similarity: 0.6,
        max_paragraph_char_number: 5000,
        search_mode: 'embedding',
        no_references_setting: {
          status: 'ai_questioning',
          value: '{question}'
        }
      },
      model_setting: {
        prompt: defaultPrompt
      },
      problem_optimization: false,
      type: 'SIMPLE'
    }
    applicationFormRef.value?.clearValidate()
  }
})

const open = () => {
  dialogVisible.value = true
}

const submitValid = (formEl: FormInstance | undefined) => {
  if (user.isEnterprise()) {
    submitHandle(formEl)
  } else {
    common
      .asyncGetValid(ValidType.Application, ValidCount.Application, loading)
      .then(async (res: any) => {
        if (res?.data) {
          submitHandle(formEl)
        } else {
          MsgAlert('提示', '社区版最多支持 5 个应用，如需拥有更多应用，请升级为专业版。')
        }
      })
  }
}
const submitHandle = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      applicationApi.postApplication(applicationForm.value, loading).then((res) => {
        MsgSuccess(t('views.application.applicationForm.buttons.createSuccess'))
        if (isWorkFlow(applicationForm.value.type)) {
          router.push({ path: `/application/${res.data.id}/workflow` })
        } else {
          router.push({ path: `/application/${res.data.id}/${res.data.type}/setting` })
        }
        emit('refresh')
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
