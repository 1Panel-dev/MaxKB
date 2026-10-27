<script setup lang="ts">
import { computed, ref } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import Content from './content/index.vue'
import { type ToolCalls } from './index'

defineOptions({ name: 'MarkdownToolCallsRender' })

const props = defineProps<{ content?: string }>()

const toolCallsContent = computed<ToolCalls>(() => {
  try {
    return JSON.parse(props.content || '{}')
  } catch {
    return { type: 'simple-tool-calls', icon: '', title: '', content: {} }
  }
})

const showContent = ref(false)
</script>

<template>
  <el-card shadow="never" class="mt-2 bg-N100!" style="--el-card-padding: 8px 12px">
    <!-- 展开或收起工具调用详情 -->
    <div class="flex-between cursor-pointer" @click="showContent = !showContent">
      <div class="flex-align-center" style="line-height: 20px">
        <ToolIcon :icon="toolCallsContent.icon" :size="24" class="mr-1" />
        <span class="ml-1">{{ toolCallsContent.title || '-' }}</span>
      </div>
      <el-icon class="transition-transform" :class="{ 'rotate-180': showContent }">
        <ArrowDown />
      </el-icon>
    </div>
    <el-collapse-transition>
      <div v-show="showContent">
        <Content :content="toolCallsContent" />
      </div>
    </el-collapse-transition>
  </el-card>
</template>
