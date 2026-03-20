<template>
  <el-card shadow="never" class="reasoning mt-8" style="--el-card-padding: 12px">
    <div class="flex-between cursor" @click="showThink = !showThink">
      <div class="flex align-center" style="line-height: 20px">
        <img src="@/assets/chat/icon_reasoning.svg" alt="" />
        <span class="ml-4">{{ $t('workflow.nodes.aiChatNode.think') }}</span>
      </div>
      <div>
        <el-icon class="arrow-icon" :class="showThink ? 'rotate-180' : ''">
          <ArrowDown />
        </el-icon>
      </div>
    </div>
    <el-collapse-transition>
      <div v-show="showThink">
        <MdPreview
          ref="editorRef"
          editorId="preview-only"
          :modelValue="content"
          class="reasoning-md"
        />
      </div>
    </el-collapse-transition>
  </el-card>
</template>
<script lang="ts" setup>
import { ref } from 'vue'
const props = defineProps<{ content?: string }>()
const showThink = ref<boolean>(true)
</script>
<style lang="scss" scoped>
.reasoning {
  .reasoning-md {
    --md-color: var(--app-input-color-placeholder) !important;
  }
}
</style>
