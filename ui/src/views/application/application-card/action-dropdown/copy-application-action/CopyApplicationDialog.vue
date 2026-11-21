<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { cloneDeep, omit } from 'lodash'
import { useI18n } from 'vue-i18n'
import type ApplicationApi from '@/api/admin/workspace/application/application'
import type { ApplicationDetail, ApplicationFormPayload } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { useStore } from '@/stores'
import { isWorkFlow } from '@/utils/common'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'CopyApplicationDialog' })
const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ api: typeof ApplicationApi }>()
const emit = defineEmits<{ closed: []; refresh: [] }>()
const route = useRoute()
const router = useRouter()
const { user } = useStore()

// 独立副本保留完整配置，名称和描述由用户调整。
const visible = ref(false)
const submitting = ref(false)
const applicationFormRef = ref<FormInstance>()
const applicationForm = reactive({ name: '', desc: '' })
const applicationPayload = ref<ApplicationFormPayload>({})
const rules = computed<FormRules<typeof applicationForm>>(() => ({
  name: [{ required: true, whitespace: true, message: t('application.fields.name.requiredMessage'), trigger: 'blur' }],
}))

function open(application: ApplicationDetail, folderId: string) {
  applicationPayload.value = {
    ...omit(cloneDeep(application), [
      'id',
      'create_time',
      'update_time',
      'publish_time',
      'is_publish',
      'user_id',
      'nick_name',
      'resource_count',
      'resource_type',
      'is_portal',
      'folder',
    ]),
    desc: application.desc ?? '',
    model_id: application.model ?? application.model_id,
    folder_id: folderId,
  }
  const copySuffix = t('common.name.copySuffix')
  applicationForm.name = `${application.name.slice(0, 64 - copySuffix.length - 1)} ${copySuffix}`
  applicationForm.desc = application.desc ?? ''
  visible.value = true
}

// 新建成功后刷新权限，再进入副本对应的配置页面。
function submit() {
  if (submitting.value) return
  applicationFormRef.value?.validate((valid) => {
    if (!valid || submitting.value) return
    submitting.value = true
    return props.api
      .postApplication({
        ...applicationPayload.value,
        name: applicationForm.name.trim(),
        desc: applicationForm.desc.trim(),
      })
      .then((application) => {
        visible.value = false
        MsgSuccess(t('common.messages.copySuccess'))
        emit('refresh')
        return user.loadCurrentUser().then(() =>
          router
            .push({
              name: isWorkFlow(application.type) ? 'workflow-application' : 'workspace-application-simple-setting',
              params: {
                workspaceId: route.params.workspaceId,
                applicationId: application.id,
                ...(!isWorkFlow(application.type) ? { type: application.type } : {}),
              },
            })
            .then(() => undefined),
        )
      })
      .finally(() => {
        submitting.value = false
      })
  })
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="t('application.copy.title')" @closed="emit('closed')">
    <el-form
      ref="applicationFormRef"
      :model="applicationForm"
      :rules="rules"
      :validate-on-rule-change="false"
      v-loading="submitting"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('common.name.label')" prop="name">
        <el-input v-model="applicationForm.name" maxlength="64" :placeholder="t('application.fields.name.placeholder')" show-word-limit />
      </el-form-item>
      <el-form-item :label="t('common.description.label')">
        <el-input
          v-model="applicationForm.desc"
          type="textarea"
          :rows="3"
          maxlength="256"
          :placeholder="t('application.fields.description.placeholder')"
          show-word-limit
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消复制 -->
      <el-button plain :disabled="submitting" @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 创建智能体副本 -->
      <el-button type="primary" :loading="submitting" @click="submit">{{ t('common.actions.copy') }}</el-button>
    </template>
  </MkDialog>
</template>
