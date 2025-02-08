<template>
  <div class="reasoning">
    <el-button link>
      {{ $t('views.applicationWorkflow.nodes.aiChatNode.think') }}
    </el-button>
    <div class="border-l">
      <MdPreview
        noIconfont
        ref="editorRef"
        editorId="preview-only"
        :modelValue="content"
        class="reasoning-md"
      />
    </div>
  </div>
</template>
<script lang="ts" setup>
const props = defineProps<{ content?: string }>()
</script>
<style lang="scss" scoped>
.reasoning {
  padding-left: 8px;
  .reasoning-md {
    --md-color: var(--app-text-color-secondary) !important;
  }
}
</style>
