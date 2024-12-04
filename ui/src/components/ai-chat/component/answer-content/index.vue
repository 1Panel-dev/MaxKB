<template>
  <div class="item-content mb-16 lighter">
    <template v-for="(answer_text, index) in answer_text_list" :key="index">
      <div class="avatar">
        <img v-if="application.avatar" :src="application.avatar" height="32px" width="32px" />
        <LogoIcon v-else height="32px" width="32px" />
      </div>
      <div class="content">
        <el-card shadow="always" class="dialog-card mb-8">
          <MdRenderer
            v-if="
              (chatRecord.write_ed === undefined || chatRecord.write_ed === true) &&
              !answer_text.content
            "
            source=" 抱歉，没有查找到相关内容，请重新描述您的问题或提供更多信息。"
          ></MdRenderer>
          <MdRenderer
            :chat_record_id="answer_text.chat_record_id"
            :child_node="answer_text.child_node"
            :runtime_node_id="answer_text.runtime_node_id"
            :disabled="loading || type == 'log'"
            v-else-if="answer_text.content"
            :source="answer_text.content"
            :send-message="chatMessage"
          ></MdRenderer>
          <span v-else-if="chatRecord.is_stop" shadow="always" class="dialog-card">
            已停止回答
          </span>
          <span v-else shadow="always" class="dialog-card">
            回答中 <span class="dotting"></span>
          </span>
          <!-- 知识来源 -->
          <div v-if="showSource(chatRecord) && index === chatRecord.answer_text_list.length - 1">
            <KnowledgeSource :data="chatRecord" :type="application.type" />
          </div>
        </el-card>
      </div>
    </template>
    <div class="content">
      <OperationButton
        :type="type"
        :application="application"
        :chatRecord="chatRecord"
        @update:chatRecord="(event: any) => emit('update:chatRecord', event)"
        :loading="loading"
        :start-chat="startChat"
        :stop-chat="stopChat"
        :regenerationChart="regenerationChart"
      ></OperationButton>
    </div>
  </div>
</template>
<script setup lang="ts">
import KnowledgeSource from '@/components/ai-chat/KnowledgeSource.vue'
import MdRenderer from '@/components/markdown/MdRenderer.vue'
import OperationButton from '@/components/ai-chat/component/operation-button/index.vue'
import { type chatType } from '@/api/type/application'
import { computed } from 'vue'
const props = defineProps<{
  chatRecord: chatType
  application: any
  loading: boolean
  sendMessage: (question: string, other_params_data?: any, chat?: chatType) => void
  chatManagement: any
  type: 'log' | 'ai-chat' | 'debug-ai-chat'
}>()

const emit = defineEmits(['update:chatRecord'])

const chatMessage = (question: string, type: 'old' | 'new', other_params_data?: any) => {
  if (type === 'old') {
    add_answer_text_list(props.chatRecord.answer_text_list)
    props.sendMessage(question, other_params_data, props.chatRecord)
    props.chatManagement.write(props.chatRecord.id)
  } else {
    props.sendMessage(question, other_params_data)
  }
}
const add_answer_text_list = (answer_text_list: Array<any>) => {
  answer_text_list.push({ content: '' })
}
const answer_text_list = computed(() => {
  return props.chatRecord.answer_text_list.map((item) => {
    if (typeof item == 'string') {
      return { content: item }
    }
    return item
  })
})

function showSource(row: any) {
  if (props.type === 'log') {
    return true
  } else if (row.write_ed && 500 !== row.status) {
    if (props.type === 'debug-ai-chat' || props.application?.show_source) {
      return true
    }
  }
  return false
}
const regenerationChart = (chat: chatType) => {
  props.sendMessage(chat.problem_text, { rechat: true })
}
const stopChat = (chat: chatType) => {
  props.chatManagement.stop(chat.id)
}
const startChat = (chat: chatType) => {
  props.chatManagement.write(chat.id)
}
</script>
<style lang="scss" scoped></style>
