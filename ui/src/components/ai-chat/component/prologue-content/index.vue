<template>
  <!-- 开场白组件 -->
  <div class="item-content mb-16">
    <div class="avatar" v-if="prologue">
      <img v-if="application.avatar" :src="application.avatar" height="32px" width="32px" />
      <LogoIcon v-else height="32px" width="32px" />
    </div>
    <div class="content" v-if="prologue">
      <el-card shadow="always" class="dialog-card" style="--el-card-padding: 10px 16px 12px">
        <MdRenderer :source="prologue" :send-message="sendMessage"></MdRenderer>
      </el-card>
    </div>
  </div>
</template>
<script setup lang="ts">
import { type chatType } from '@/api/type/application'
import { computed } from 'vue'
import MdRenderer from '@/components/markdown/MdRenderer.vue'
const props = defineProps<{
  application: any
  available: boolean
  type: 'log' | 'ai-chat' | 'debug-ai-chat'
  sendMessage: (question: string, other_params_data?: any, chat?: chatType) => void
}>()
const toQuickQuestion = (match: string, offset: number, input: string) => {
  return `<quick_question>${match.replace('- ', '')}</quick_question>`
}
const prologue = computed(() => {
  const temp = props.available
    ? props.application?.prologue
    : '抱歉，当前正在维护，无法提供服务，请稍后再试！'
  return temp?.replace(/-\s.+/g, toQuickQuestion)
})
</script>
<style lang="scss" scoped></style>
