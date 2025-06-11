<template>
  <div class="item-content mb-16 lighter">
    <template v-for="(answer_text, index) in answer_text_list" :key="index">
      <div class="avatar mr-8" v-if="showAvatar">
        <img v-if="application.avatar" :src="application.avatar" height="28px" width="28px" />
        <LogoIcon v-else height="28px" width="28px" />
      </div>
      <div
        class="content"
        @mouseup="openControl"
        :style="{
          'padding-right': showUserAvatar ? 'var(--padding-left)' : '0'
        }"
      >
        <el-card shadow="always" class="mb-8 border-r-8" style="--el-card-padding: 6px 16px">
          <MdRenderer
            v-if="
              (chatRecord.write_ed === undefined || chatRecord.write_ed === true) &&
              answer_text.length == 0
            "
            :source="$t('chat.tip.answerMessage')"
          ></MdRenderer>
          <template v-else-if="answer_text.length > 0">
            <MdRenderer
              v-for="(answer, index) in answer_text"
              :key="index"
              :chat_record_id="answer.chat_record_id"
              :child_node="answer.child_node"
              :runtime_node_id="answer.runtime_node_id"
              :reasoning_content="answer.reasoning_content"
              :disabled="loading || type == 'log'"
              :source="answer.content"
              :send-message="chatMessage"
            ></MdRenderer>
          </template>
          <p v-else-if="chatRecord.is_stop" shadow="always" style="margin: 0.5rem 0">
            {{ $t('chat.tip.stopAnswer') }}
          </p>
          <p v-else shadow="always" style="margin: 0.5rem 0">
            {{ $t('chat.tip.answerLoading') }} <span class="dotting"></span>
          </p>
          <!-- 知识来源 -->
          <KnowledgeSource
            :data="chatRecord"
            :type="application.type"
            v-if="showSource(chatRecord) && index === chatRecord.answer_text_list.length - 1"
          />
        </el-card>
      </div>
    </template>
    <div
      class="content"
      :style="{
        'padding-left': showAvatar ? 'var(--padding-left)' : '0',
        'padding-right': showUserAvatar ? 'var(--padding-left)' : '0'
      }"
    >
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
import bus from '@/bus'
import useStore from '@/stores'
const props = defineProps<{
  chatRecord: chatType
  application: any
  loading: boolean
  sendMessage: (question: string, other_params_data?: any, chat?: chatType) => Promise<boolean>
  chatManagement: any
  type: 'log' | 'ai-chat' | 'debug-ai-chat'
}>()

const { user } = useStore()

const emit = defineEmits(['update:chatRecord'])

const showAvatar = computed(() => {
  return user.isEnterprise() ? props.application.show_avatar : true
})
const showUserAvatar = computed(() => {
  return user.isEnterprise() ? props.application.show_user_avatar : true
})
const chatMessage = (question: string, type: 'old' | 'new', other_params_data?: any) => {
  if (type === 'old') {
    add_answer_text_list(props.chatRecord.answer_text_list)
    props.sendMessage(question, other_params_data, props.chatRecord).then(() => {
      props.chatManagement.open(props.chatRecord.id)
      props.chatManagement.write(props.chatRecord.id)
    })
  } else {
    props.sendMessage(question, other_params_data)
  }
}
const add_answer_text_list = (answer_text_list: Array<any>) => {
  answer_text_list.push([])
}

const openControl = (event: any) => {
  if (props.type !== 'log') {
    bus.emit('open-control', event)
  }
}

const answer_text_list = computed(() => {
  return props.chatRecord.answer_text_list.map((item) => {
    if (typeof item == 'string') {
      return [
        {
          content: item,
          chat_record_id: undefined,
          child_node: undefined,
          runtime_node_id: undefined,
          reasoning_content: undefined
        }
      ]
    } else if (item instanceof Array) {
      return item
    } else {
      return [item]
    }
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
  props.sendMessage(chat.problem_text, { re_chat: true })
}
const stopChat = (chat: chatType) => {
  props.chatManagement.stop(chat.id)
}
const startChat = (chat: chatType) => {
  props.chatManagement.write(chat.id)
}
</script>
<style lang="scss" scoped></style>
