<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type SystemApiKeyApi from '@/api/admin/system/api-key'
import type SystemResourceApiKeyApi from '@/api/admin/system/resource-management/application/api-key'
import type ApplicationApiKeyApi from '@/api/admin/workspace/application/api-key'
import { copyText } from '@/utils/clipboard'

defineOptions({ name: 'ButtonCreateApiKey' })

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{
  api: typeof ApplicationApiKeyApi | typeof SystemResourceApiKeyApi | typeof SystemApiKeyApi
  applicationId?: string
  refresh: () => Promise<void>
}>()
const loading = defineModel<boolean>('loading', { required: true })

/* 创建 API Key 与结果弹窗 */
const createdApiKey = ref('')
const createdDialogVisible = ref(false)

function handleCreate() {
  if (loading.value) return
  loading.value = true
  const request =
    props.applicationId !== undefined
      ? (props.api as typeof ApplicationApiKeyApi | typeof SystemResourceApiKeyApi).postApiKey(props.applicationId)
      : (props.api as typeof SystemApiKeyApi).postApiKey()
  return request
    .then((record) => {
      createdApiKey.value = record.secret_key
      createdDialogVisible.value = true
      return props.refresh()
    })
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <!-- 创建 API Key -->
  <el-button type="primary" @click="handleCreate">
    <MkIcon name="icon_add_outlined" />
    <span>{{ t('common.actions.create') }}</span>
  </el-button>
  <MkDialog v-model="createdDialogVisible" title="API Key" @closed="createdApiKey = ''">
    <template #subtitle>{{ t('apiKey.safetyHint') }}</template>
    <el-input :model-value="createdApiKey" readonly>
      <template #suffix>
        <!-- 复制新建的完整 API Key -->
        <el-button text @click="copyText(createdApiKey, t('common.messages.copied'))" class="-mr-1">
          <MkIcon name="icon_copy_outlined" />
        </el-button>
      </template>
    </el-input>
    <template #footer>
      <!-- 关闭创建结果弹窗 -->
      <el-button plain @click="createdDialogVisible = false">{{ t('apiKey.gotIt') }}</el-button>
    </template>
  </MkDialog>
</template>
