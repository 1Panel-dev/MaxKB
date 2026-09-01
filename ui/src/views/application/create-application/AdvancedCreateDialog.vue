<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
import ApplicationApi from '@/api/admin/workspace/application/application'
import { APPLICATION_TYPE } from '@/api/enums'
import type { ApplicationFormPayload } from '@/api/types'
import MkSourceCard from '@/components/mk-source-card/index.vue'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import { applicationTemplate } from './template'

defineOptions({ name: 'AdvancedCreateDialog' })

type ApplicationTemplateType = 'blank' | 'assistant'

interface AdvancedApplicationDraft {
  desc: string
  name: string
}

const { auth } = useStore()
const route = useRoute()
const router = useRouter()

const props = defineProps<{ folderId: string }>()

const dialogVisible = ref(false)
const loading = ref(false)
const selectedTemplate = ref<ApplicationTemplateType>('blank')
const applicationFormRef = ref<FormInstance>()
const applicationForm = reactive<AdvancedApplicationDraft>({ desc: '', name: '' })
const applicationFormRules: FormRules<typeof applicationForm> = {
  name: [{ required: true, message: '请输入智能体名称', trigger: 'blur' }],
}
const createDisabled = computed(() => !applicationForm.name.trim())

function handleTemplateSelect(template: ApplicationTemplateType) {
  selectedTemplate.value = template
}

function submit() {
  applicationFormRef.value?.validate((valid) => {
    if (!valid) return

    const workflow = cloneDeep(applicationTemplate[selectedTemplate.value])
    const baseNode = workflow.nodes?.find(({ id }) => id === 'base-node')
    const prologue = (baseNode?.properties as { node_data?: { prologue?: string } } | undefined)?.node_data?.prologue
    const payload: ApplicationFormPayload = {
      desc: applicationForm.desc.trim(),
      folder_id: props.folderId,
      name: applicationForm.name.trim(),
      prologue,
      type: APPLICATION_TYPE.WORK_FLOW,
      work_flow: workflow,
    }

    loading.value = true
    ApplicationApi.postApplication(payload)
      .then((application) => {
        return auth.loadAuthBaseProfile().then(() => {
          MsgSuccess('创建成功')
          dialogVisible.value = false
          return router.push({
            name: 'workflow-application',
            params: { applicationId: application.id, workspaceId: route.params.workspaceId },
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
  selectedTemplate.value = 'blank'
  loading.value = false
  applicationFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" title="创建高级智能体" align-center @closed="resetData">
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

      <el-form-item label="模板">
        <div class="grid w-full grid-cols-2 gap-4">
          <el-card
            :class="selectedTemplate === 'blank' ? 'border-primary! bg-primary/10!' : ''"
            shadow="hover"
            @click="handleTemplateSelect('blank')"
          >
            <div class="flex h-full items-center justify-center gap-2">
              <MkIcon name="icon_add_outlined" :size="16" />
              <span>空白创建</span>
            </div>
          </el-card>

          <MkSourceCard
            class="min-h-0!"
            :class="selectedTemplate === 'assistant' ? 'active' : ''"
            title="知识库问答助手"
            @click="handleTemplateSelect('assistant')"
          >
            <template #icon>
              <ApplicationIcon />
            </template>
            <p>将从知识库中检索到的知识作为已知信息，回答用户提出的问题。</p>
          </MkSourceCard>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain :disabled="loading" @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :disabled="createDisabled" :loading="loading" @click="submit">创建</el-button>
    </template>
  </MkDialog>
</template>
