<template>
  <el-collapse>
    <el-collapse-item title="Consistency">
      <template #title>
        <div class="flex" style="flex-wrap: nowrap; align-items: center">
          <el-avatar class="avatar-gradient mr-8" style="height: 20px; width: 20px" shape="square">
            <img :src="toolCallsContent.icon || defaultIcon" /> </el-avatar
          >{{ toolCallsContent.title || '工具执行' }}
        </div>
      </template>
      <Content :content="toolCallsContent"></Content>
    </el-collapse-item>
  </el-collapse>
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
</script>
<style lang="scss" scoped></style>
