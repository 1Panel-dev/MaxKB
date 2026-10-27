<script setup lang="ts">
import { ref, useId } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'

defineOptions({ name: 'MarkdownReasoningRender' })

defineProps<{ content?: string }>()

const editorId = `markdown-reasoning-${useId()}`
const showThink = ref(true)
</script>

<template>
  <el-card shadow="never" class="reasoning mt-2" style="--el-card-padding: 12px">
    <!-- 展开或收起思考过程 -->
    <div class="flex-between cursor-pointer" @click="showThink = !showThink">
      <div class="flex-align-center" style="line-height: 20px">
        <MkIcon name="icon_two-ellipses_outlined" />
        <span class="ml-1">思考过程</span>
      </div>
      <el-icon class="transition-transform" :class="{ 'rotate-180': showThink }">
        <ArrowDown />
      </el-icon>
    </div>
    <el-collapse-transition>
      <div v-show="showThink">
        <MdPreview :editor-id="editorId" :model-value="content ?? ''" class="reasoning-md" />
      </div>
    </el-collapse-transition>
  </el-card>
</template>

<style lang="scss" scoped>
.reasoning-md {
  --md-color: var(--color-N500) !important;
}
</style>
