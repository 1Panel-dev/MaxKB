<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import UploadImageDrawer from './UploadImageDrawer.vue'

defineOptions({ name: 'ButtonUploadImage' })
const { t } = useI18n({ useScope: 'global' })
defineProps<{
  api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['image']
  knowledgeId: string
  fileCountLimit?: number
  fileSizeLimit?: number
}>()
const emit = defineEmits<{ refresh: [] }>()

/* 上传入口与抽屉生命周期 */
const drawerMounted = ref(false)
const drawerRef = useTemplateRef<InstanceType<typeof UploadImageDrawer>>('drawerRef')
function handleOpenUpload() {
  drawerMounted.value = true
  nextTick(() => drawerRef.value?.open())
}
</script>

<template>
  <!-- 上传图片 -->
  <el-button type="primary" @click="handleOpenUpload">
    <MkIcon name="icon_upload_outlined" />
    <span>{{ t('knowledge.image.upload.title') }}</span>
  </el-button>
  <UploadImageDrawer
    v-if="drawerMounted"
    ref="drawerRef"
    :api="api"
    :knowledge-id="knowledgeId"
    :file-count-limit="fileCountLimit"
    :file-size-limit="fileSizeLimit"
    @refresh="emit('refresh')"
    @closed="drawerMounted = false"
  />
</template>
