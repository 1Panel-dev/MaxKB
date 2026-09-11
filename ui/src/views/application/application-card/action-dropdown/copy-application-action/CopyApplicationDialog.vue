<script setup lang="ts">
import { reactive, ref } from 'vue'
import { cloneDeep, omit } from 'lodash'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import type ApplicationApi from '@/api/admin/workspace/application/application'
import type { ApplicationDetail, ApplicationFormPayload } from '@/api/types'
import { useStore } from '@/stores'
import { isWorkFlow } from '@/utils/application'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'CopyApplicationDialog' })
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
const rules: FormRules<typeof applicationForm> = {
  name: [{ required: true, whitespace: true, message: '请输入智能体名称', trigger: 'blur' }],
}

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
  applicationForm.name = `${application.name.slice(0, 61)} 副本`
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
        MsgSuccess('复制成功')
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

function resetData() {
  Object.assign(applicationForm, { name: '', desc: '' })
  applicationPayload.value = {}
  submitting.value = false
  applicationFormRef.value?.clearValidate()
}
function handleClosed() {
  resetData()
  emit('closed')
}
defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="复制智能体" :show-close="!submitting" @closed="handleClosed">
    <el-form
      ref="applicationFormRef"
      :model="applicationForm"
      :rules="rules"
      :disabled="submitting"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="名称" prop="name">
        <el-input v-model="applicationForm.name" maxlength="64" placeholder="请输入智能体名称" show-word-limit />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="applicationForm.desc" type="textarea" :rows="3" maxlength="256" placeholder="请输入智能体描述" show-word-limit />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消复制 -->
      <el-button plain :disabled="submitting" @click="visible = false">取消</el-button>
      <!-- 创建智能体副本 -->
      <el-button type="primary" :loading="submitting" @click="submit">复制</el-button>
    </template>
  </MkDialog>
</template>
