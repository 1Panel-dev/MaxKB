<script setup lang="ts">
import { useTemplateRef } from 'vue'
import EmbedThirdPartyDialog from './EmbedThirdPartyDialog.vue'

defineOptions({ name: 'ButtonEmbedThirdParty' })

const dialogRef = useTemplateRef<InstanceType<typeof EmbedThirdPartyDialog>>('dialogRef')

function handleOpenEmbedThirdParty() {
  dialogRef.value?.open()
}
</script>

<template>
  <!-- 嵌入第三方 -->
  <el-button plain @click="handleOpenEmbedThirdParty">
    <MkIcon name="icon_keyboard_outlined1" />
    <span>嵌入第三方</span>
  </el-button>
  <EmbedThirdPartyDialog ref="dialogRef" />
</template>
