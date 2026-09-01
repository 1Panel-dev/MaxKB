<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import ApplicationApi from '@/api/admin/workspace/application/application'
import { APPLICATION_TYPE } from '@/api/enums'
import type { ApplicationFormPayload } from '@/api/types'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'SimpleCreateDialog' })

const DEFAULT_PROLOGUE = '您好，我是 XXX 小助手，您可以向我提出 XXX 使用问题。\n- XXX 主要功能有什么？\n- XXX 如何收费？\n- 需要转人工服务'
const DEFAULT_PROMPT = `已知信息：{data}
用户问题：{question}
回答要求：
- 请使用中文回答用户问题`
const DEFAULT_OPTIMIZATION_PROMPT = '()里面是用户问题,根据上下文回答揣测用户问题({question}) 要求: 输出一个补全问题,并且放在<data></data>标签中'

interface SimpleApplicationDraft {
  desc: string
  name: string
}

const { auth } = useStore()
const route = useRoute()
const router = useRouter()

const props = defineProps<{ folderId: string }>()

const dialogVisible = ref(false)
const loading = ref(false)
const applicationFormRef = ref<FormInstance>()
const applicationForm = reactive<SimpleApplicationDraft>({ desc: '', name: '' })
const applicationFormRules: FormRules<SimpleApplicationDraft> = {
  name: [{ required: true, message: '请输入智能体名称', trigger: 'blur' }],
}
const createDisabled = computed(() => !applicationForm.name.trim())

function submit() {
  applicationFormRef.value?.validate((valid) => {
    if (!valid) return

    const payload: ApplicationFormPayload = {
      desc: applicationForm.desc.trim(),
      dialogue_number: 1,
      folder_id: props.folderId,
      knowledge_id_list: [],
      knowledge_setting: {
        max_paragraph_char_number: 5000,
        no_references_setting: { status: 'ai_questioning', value: '{question}' },
        search_mode: 'embedding',
        similarity: 0.6,
        top_n: 3,
      },
      model_params_setting: {},
      model_setting: { no_references_prompt: '{question}', prompt: DEFAULT_PROMPT, system: '' },
      name: applicationForm.name.trim(),
      problem_optimization: false,
      problem_optimization_prompt: DEFAULT_OPTIMIZATION_PROMPT,
      prologue: DEFAULT_PROLOGUE,
      stt_model_enable: false,
      tts_model_enable: false,
      tts_type: 'BROWSER',
      type: APPLICATION_TYPE.SIMPLE,
    }

    loading.value = true
    ApplicationApi.postApplication(payload)
      .then((application) => {
        return auth.loadAuthBaseProfile().then(() => {
          MsgSuccess('创建成功')
          dialogVisible.value = false
          return router.push({
            name: 'workspace-application-simple-setting',
            params: { applicationId: application.id, type: application.type, workspaceId: route.params.workspaceId },
          })
        })
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function open() {
  dialogVisible.value = true
}

function resetData() {
  Object.assign(applicationForm, { desc: '', name: '' })
  loading.value = false
  applicationFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" title="创建简易智能体" align-center @closed="resetData">
    <el-form
      ref="applicationFormRef"
      :model="applicationForm"
      :rules="applicationFormRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent="submit"
    >
      <el-form-item label="名称" prop="name">
        <el-input
          v-model="applicationForm.name"
          maxlength="64"
          placeholder="请输入智能体名称"
          show-word-limit
          @blur="applicationForm.name = applicationForm.name.trim()"
        />
      </el-form-item>

      <el-form-item label="描述">
        <el-input
          v-model="applicationForm.desc"
          maxlength="256"
          placeholder="描述该智能体的应用场景及用途，如：XXX 小助手回答用户提出的 XXX 产品使用问题"
          :rows="4"
          show-word-limit
          type="textarea"
          @blur="applicationForm.desc = applicationForm.desc.trim()"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button class="w-20!" plain :disabled="loading" @click="dialogVisible = false">取消</el-button>
      <el-button class="w-20!" type="primary" :disabled="createDisabled" :loading="loading" @click="submit">创建</el-button>
    </template>
  </MkDialog>
</template>
