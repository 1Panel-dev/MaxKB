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
        <el-text>
          <el-icon>
            <Document />
          </el-icon>
          {{ data?.document_name }}
        </el-text>
        <div class="flex align-center" style="line-height: 32px">
          <AppAvatar class="mr-8 avatar-blue" shape="square" :size="18">
            <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
          </AppAvatar>

          <span class="ellipsis"> {{ data?.dataset_name }}</span>
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
