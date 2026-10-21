<script setup lang="ts">
import { useTemplateRef } from 'vue'
import EmbedThirdPartyDialog from './EmbedThirdPartyDialog.vue'

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
    <MkIcon name="icon_keyboard_outlined1" />
    <span>嵌入第三方</span>
  </el-button>
  <EmbedThirdPartyDialog ref="dialogRef" :share-url="props.shareUrl" :access-token="props.accessToken" />
</template>
