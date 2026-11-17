<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ToolItem, ToolStoreItem } from '@/api/types'
import type { FormInstance, FormRules } from 'element-plus'
import { TOOL_TYPE } from '@/api/enums'
import SystemSharedToolStoreApi from '@/api/admin/system/shared-resources/tool/store'
import SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import WorkspaceToolStoreApi from '@/api/admin/workspace/tool/store'
import ToolApi from '@/api/admin/workspace/tool/tool'
import { FOLDER_ENTRY_ID } from '@/constants/folder'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import { isSystemSharedResource } from '@/utils/resource-context'

defineOptions({ name: 'StoreToolFormDialog' })

const { t } = useI18n({ useScope: 'global' })
const props = withDefaults(
  defineProps<{
    folderId: string
  }>(),
  { folderId: () => FOLDER_ENTRY_ID.ALL },
)

const { auth } = useStore()

const emit = defineEmits<{ closed: []; refresh: []; update: [tool: ToolItem] }>()

interface StoreToolForm {
  name: string
}

const formRef = ref<FormInstance>()
const visible = ref(false)
const loading = ref(false)
const currentTool = ref<ToolStoreItem>()
const storeToolForm = reactive<StoreToolForm>({ name: '' })
const formRules = computed<FormRules<StoreToolForm>>(() => ({
  name: [{ whitespace: true, required: true, message: t('tool.fields.name.requiredMessage'), trigger: 'blur' }],
}))

function handleSubmit() {
  formRef.value?.validate((valid) => {
    if (!valid || !currentTool.value) return

    const tool = currentTool.value
    const name = storeToolForm.name
    loading.value = true

    const commonPayload = { folder_id: props.folderId || FOLDER_ENTRY_ID.ALL, name }
    const isSharedResource = isSystemSharedResource()
    let request: Promise<ToolItem>

    if (tool.label === 'workflow_template') {
      const requestApi = isSharedResource ? SystemSharedToolApi : ToolApi
      request = requestApi.postTool({ ...commonPayload, code: '{}', tool_type: TOOL_TYPE.WORKFLOW, work_flow_template: tool })
    } else {
      const requestApi = isSharedResource ? SystemSharedToolStoreApi : WorkspaceToolStoreApi
      request = requestApi.postStoreTool(tool.id, {
        ...commonPayload,
        download_callback_url: tool.downloadCallbackUrl ?? '',
        download_url: tool.downloadUrl ?? '',
        icon: tool.icon ?? '',
        label: tool.label ?? '',
        versions: tool.versions ?? [],
      })
    }

    request
      .then(async () => {
        await auth.loadAuthBaseProfile()
      })
      .then(() => {
        MsgSuccess(t('common.messages.addSuccess'))
        visible.value = false
        emit('refresh')
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function open(tool: ToolStoreItem) {
  currentTool.value = tool
  storeToolForm.name = tool.name
  visible.value = true
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="t('tool.store.addTitle')" @closed="emit('closed')">
    <el-form
      ref="formRef"
      :model="storeToolForm"
      :rules="formRules"
      :validate-on-rule-change="false"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item :label="t('common.name.label')" prop="name">
        <el-input
          v-model="storeToolForm.name"
          maxlength="64"
          :placeholder="t('tool.fields.name.placeholder')"
          show-word-limit
          @blur="storeToolForm.name = storeToolForm.name.trim()"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button :disabled="loading" plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">{{ t('common.actions.add') }}</el-button>
    </template>
  </MkDialog>
</template>
