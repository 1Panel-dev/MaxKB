<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ApplicationFormPayload, ApplicationStoreTemplate } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { APPLICATION_TYPE } from '@/api/enums'
import ApplicationApi from '@/api/admin/workspace/application/application'
import { applicationTemplate } from './template'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'AdvancedCreateDialog' })

const { t } = useI18n({ useScope: 'global' })

type ApplicationTemplateType = 'blank' | 'assistant'

interface AdvancedApplicationDraft {
  desc: string
  name: string
}

const { auth } = useStore()
const route = useRoute()
const router = useRouter()

const props = defineProps<{ folderId: string }>()
const emit = defineEmits<{ refresh: []; closed: [] }>()
const storeTemplate = ref<ApplicationStoreTemplate>()

const dialogVisible = ref(false)
const loading = ref(false)
const selectedTemplate = ref<ApplicationTemplateType>('blank')
const applicationFormRef = ref<FormInstance>()
const applicationForm = reactive<AdvancedApplicationDraft>({ desc: '', name: '' })
const applicationFormRules = computed<FormRules<typeof applicationForm>>(() => ({
  name: [{ required: true, whitespace: true, message: t('application.fields.name.requiredMessage'), trigger: 'blur' }],
}))
const createDisabled = computed(() => !applicationForm.name.trim())

function handleTemplateSelect(template: ApplicationTemplateType) {
  selectedTemplate.value = template
}

function submit() {
  if (loading.value) return
  applicationFormRef.value?.validate((valid) => {
    if (!valid || loading.value) return

    const payload: ApplicationFormPayload = {
      desc: applicationForm.desc.trim(),
      folder_id: props.folderId,
      name: applicationForm.name.trim(),
      type: APPLICATION_TYPE.WORK_FLOW,
    }

    if (storeTemplate.value) {
      payload.work_flow_template = cloneDeep(storeTemplate.value)
    } else {
      const workflow = cloneDeep(applicationTemplate[selectedTemplate.value])
      const baseNode = workflow.nodes?.find(({ id }) => id === 'base-node')
      payload.prologue = (baseNode?.properties as { node_data?: { prologue?: string } } | undefined)?.node_data?.prologue
      payload.work_flow = workflow
    }

    loading.value = true
    ApplicationApi.postApplication(payload)
      .then((application) => {
        return auth.loadAuthBaseProfile().then(() => {
          MsgSuccess(t('common.messages.createSuccess'))
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

function open(template?: ApplicationStoreTemplate) {
  if (template) {
    storeTemplate.value = cloneDeep(template)
    Object.assign(applicationForm, { name: template.name, desc: template.desc || '' })
  }
  dialogVisible.value = true
}

function handleClosed() {
  resetData()
  emit('closed')
}

function resetData() {
  Object.assign(applicationForm, { desc: '', name: '' })
  selectedTemplate.value = 'blank'
  storeTemplate.value = undefined
  loading.value = false
  applicationFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" :title="t('application.advanced.createTitle')" @closed="handleClosed">
    <el-form
      ref="applicationFormRef"
      :model="applicationForm"
      :rules="applicationFormRules"
      :validate-on-rule-change="false"
      v-loading="loading"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('common.name.label')" prop="name">
        <el-input
          v-model="applicationForm.name"
          maxlength="64"
          :placeholder="t('application.fields.name.placeholder')"
          show-word-limit
          @blur="applicationForm.name = applicationForm.name.trim()"
        />
      </el-form-item>

      <el-form-item :label="t('common.description.label')">
        <el-input
          v-model="applicationForm.desc"
          maxlength="256"
          :placeholder="t('application.fields.description.placeholder')"
          :rows="4"
          show-word-limit
          type="textarea"
          @blur="applicationForm.desc = applicationForm.desc.trim()"
        />
      </el-form-item>

      <el-form-item v-if="!storeTemplate" :label="t('application.template.label')">
        <div class="grid w-full grid-cols-2 gap-4">
          <el-card
            :class="selectedTemplate === 'blank' ? 'border-primary! bg-primary/10!' : ''"
            shadow="hover"
            @click="handleTemplateSelect('blank')"
          >
            <div class="flex-align-center h-full justify-center gap-2">
              <MkIcon name="icon_add_outlined" />
              <span>{{ t('application.template.blank') }}</span>
            </div>
          </el-card>

          <MkResourceCard
            class="min-h-0!"
            :class="selectedTemplate === 'assistant' ? 'active' : ''"
            :title="t('application.template.assistant.label')"
            @click="handleTemplateSelect('assistant')"
          >
            <template #icon>
              <ApplicationIcon />
            </template>
            <p>{{ t('application.template.assistant.description') }}</p>
          </MkResourceCard>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <!-- 取消创建 -->
      <el-button plain :disabled="loading" @click="dialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 创建高级智能体 -->
      <el-button type="primary" :disabled="createDisabled" :loading="loading" @click="submit">{{ t('common.actions.create') }}</el-button>
    </template>
  </MkDialog>
</template>
