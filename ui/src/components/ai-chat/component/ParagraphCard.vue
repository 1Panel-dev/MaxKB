<template>
  <CardBox
    shadow="never"
    :title="data.title || '-'"
    class="paragraph-source-card cursor mb-8 paragraph-source-card-height"
    :class="data.is_active ? '' : 'disabled'"
    :showIcon="false"
  >
    <template #icon>
      <AppAvatar class="mr-12 avatar-light" :size="22"> {{ index + 1 + '' }}</AppAvatar>
    </template>
    <div class="active-button primary">{{ data.similarity?.toFixed(3) }}</div>
    <template #description>
      <el-scrollbar height="150">
        <MdPreview ref="editorRef" editorId="preview-only" :modelValue="data.content" />
      </el-scrollbar>
    </template>
    <template #footer>
      <div class="footer-content flex-between">
        <el-text class="flex align-center" style="width: 70%">
          <el-icon class="mr-4" :size="25">
            <img
              src="@/assets/doc-icon.svg"
              style="width: 90%"
              alt=""
              v-if="data?.document_name?.includes('doc')"
            />
            <img
              src="@/assets/docx-icon.svg"
              style="width: 90%"
              alt=""
              v-else-if="data?.document_name?.includes('docx')"
            />
            <img
              src="@/assets/pdf-icon.svg"
              style="width: 90%"
              alt=""
              v-else-if="data?.document_name?.includes('pdf')"
            />
            <img
              src="@/assets/md-icon.svg"
              style="width: 90%"
              alt=""
              v-else-if="data?.document_name?.includes('md')"
            />
            <img
              src="@/assets/xls-icon.svg"
              style="width: 90%"
              alt=""
              v-else-if="data?.document_name?.includes('xls')"
            />
            <img
              src="@/assets/txt-icon.svg"
              style="width: 90%"
              alt=""
              v-else-if="data?.document_name?.includes('txt')"
            />
            <img src="@/assets/doc-icon.svg" style="width: 90%" alt="" v-else />
          </el-icon>
          <span class="ellipsis" :title="data?.document_name?.trim()">
            {{ data?.document_name.trim() }}</span
          >
        </el-text>
        <div class="flex align-center" style="line-height: 32px">
          <AppAvatar class="mr-8 avatar-blue" shape="square" :size="18">
            <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
          </AppAvatar>

          <span class="ellipsis" :title="data?.dataset_name"> {{ data?.dataset_name }}</span>
        </div>
      </div>
    </template>
  </CardBox>
</template>
<script setup lang="ts">
const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  },
  index: {
    type: Number,
    default: 0
  }
})
const iconMap: { [key: string]: string } = {
  doc: '../../assets/doc-icon.svg',
  docx: '../../assets/docx-icon.svg',
  pdf: '../../assets/pdf-icon.svg',
  md: '../../assets/md-icon.svg',
  txt: '../../assets/txt-icon.svg',
  xls: '../../assets/xls-icon.svg',
  xlsx: '../../assets/xlsx-icon.svg'
}
function getIconPath(documentName: string) {
  const extension = documentName.split('.').pop()?.toLowerCase()
  if (!documentName || !extension) return new URL(`${iconMap['doc']}`, import.meta.url).href
  if (iconMap && extension && iconMap[extension]) {
    return new URL(`${iconMap[extension]}`, import.meta.url).href
  }
  return new URL(`${iconMap['doc']}`, import.meta.url).href
}
</script>
<style lang="scss" scoped>
.paragraph-source-card-height {
  height: 260px;
}
@media only screen and (max-width: 768px) {
  .paragraph-source-card-height {
    height: 285px;
  }
}
</style>
