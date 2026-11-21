<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import EmbedThirdPartyDialog from './EmbedThirdPartyDialog.vue'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'ButtonEmbedThirdParty' })

const props = defineProps<{ shareUrl: string; accessToken: string }>()
const dialogRef = useTemplateRef<InstanceType<typeof EmbedThirdPartyDialog>>('dialogRef')

function handleOpenEmbedThirdParty() {
  if (!props.shareUrl || !props.accessToken) return
  dialogRef.value?.open()
}
</script>

<template>
  <!-- 嵌入第三方 -->
  <el-button plain :disabled="!props.shareUrl || !props.accessToken" @click="handleOpenEmbedThirdParty">
    <MkIcon name="icon_embedded_outlined" />
    <span>{{ t('application.overview.embed.title') }}</span>
  </el-button>
  <EmbedThirdPartyDialog ref="dialogRef" :share-url="props.shareUrl" :access-token="props.accessToken" />
</template>
