<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { useApplicationDetailContext } from '../../context'
import ApiKeyDialog from './ApiKeyDialog.vue'

defineOptions({ name: 'ButtonApiKey' })

const dialogRef = useTemplateRef<InstanceType<typeof ApiKeyDialog>>('dialogRef')
const { applicationId, resourceApi } = useApplicationDetailContext()

function handleOpenApiKey() {
  dialogRef.value?.open()
}
</script>

<template>
  <!-- 管理 API Key -->
  <el-button plain @click="handleOpenApiKey">
    <MkIcon name="icon_passkeys_outlined" />
    <span>API Key</span>
  </el-button>
  <ApiKeyDialog ref="dialogRef" :api="resourceApi.apiKey" :application-id="applicationId" />
</template>
