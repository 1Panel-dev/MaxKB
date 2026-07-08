<template>
  <el-card shadow="never" class="layout-bg mt-8" style="--el-card-padding: 8px 12px">
    <div class="flex-between cursor" @click="showContent = !showContent">
      <div class="flex align-center" style="line-height: 20px">
        <el-avatar
          v-if="toolCallsContent.icon"
          shape="square"
          :size="24"
          style="background: none"
          class="mr-4"
        >
          <img :src="toolCallsContent.icon" alt="" />
        </el-avatar>
        <ToolIcon v-else :size="24" class="mr-4" />
        <span class="ml-4">{{ toolCallsContent.title || '-' }}</span>
      </div>
      <div>
        <el-icon class="arrow-icon" :class="showContent ? 'rotate-180' : ''">
          <ArrowDown />
        </el-icon>
      </div>
    </div>
    <el-collapse-transition>
      <div v-show="showContent">
        <Content :content="toolCallsContent"></Content>
      </div>
    </el-collapse-transition>
  </el-card>
</template>
<script lang="ts" setup>
import Content from './content/index.vue'
import { ref, computed } from 'vue'
import { type ToolCalls } from './index'
import defaultIcon from '@/assets/workflow/icon_robot.svg'
const props = defineProps<{ content?: string }>()

const toolCallsContent = computed<ToolCalls>(() => {
  try {
    return JSON.parse(props.content ? props.content : '{}')
  } catch (error) {
    return { type: 'simple-tool-calls', icon: '', title: '', content: {} }
  }
})

const showContent = ref<boolean>(false)
</script>
<style lang="scss" scoped></style>
