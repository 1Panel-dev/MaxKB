<template>
  <div class="reasoning">
    <el-button text @click="showThink = !showThink" class="reasoning-button">
      {{ $t('views.applicationWorkflow.nodes.aiChatNode.think') }}
      <el-icon class="ml-4" :class="showThink ? 'rotate-180' : ''"><ArrowDownBold /> </el-icon>
    </el-button>
    <el-collapse-transition>
      <div class="border-l mt-8" v-show="showThink">
        <MdPreview
          ref="editorRef"
          editorId="preview-only"
          :modelValue="content"
          class="reasoning-md"
        />
      </div>
    </el-collapse-transition>
  </div>
</template>
<script lang="ts" setup>
import { ref } from 'vue'
const props = defineProps<{ content?: string }>()
const showThink = ref<boolean>(true)
</script>
<style lang="scss" scoped>
.reasoning {
  .reasoning-button {
    font-size: 14px;
    color: var(--app-text-color-secondary) !important;
  }
  .reasoning-md {
    padding-left: 8px;
    --md-color: var(--app-input-color-placeholder) !important;
  }
}
</style>
