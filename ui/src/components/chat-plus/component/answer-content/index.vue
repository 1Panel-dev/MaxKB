<template>
  <div class="item-content lighter">
    <div v-for="(answer_text, index) in answer_text_list" :key="index" class="mb-8 flex">
      <div class="avatar mr-8" v-if="showAvatar">
        <img v-if="application.avatar" :src="application.avatar" height="28px" width="28px" />
        <LogoIcon v-else height="28px" width="28px" />
      </div>
      <div
        class="content w-full"
        @mouseup="openControl"
        :style="{ 'padding-right': showUserAvatar ? 'var(--padding-left)' : '0' }"
      >
        <template v-if="answer_text.length > 0">
          <ContentItem
            v-for="(answer, aIndex) in answer_text"
            :key="aIndex"
            :content="answer"
            :send-message="chatMessage"
          />
        </template>
        <ContentItem
          v-else-if="
            (chatRecord.write_ed === undefined || chatRecord.write_ed === true) &&
            answer_text_list.flat().map((item) => item.content).join('').trim().length === 0
          "
          :content="{ content: $t('aiChat.tip.answerMessage') }"
        />
        <p v-else-if="chatRecord.is_stop" style="margin: 0.5rem 0">
          {{ $t('aiChat.tip.stopAnswer') }}
        </p>
        <p v-else style="margin: 0.5rem 0">
          {{ $t('aiChat.tip.answerLoading') }} <span class="dotting"></span>
        </p>
        <KnowledgeSourceComponent
          :data="chatRecord"
          :application="application"
          :type="type"
          :appType="application.type"
          :executionIsRightPanel="props.executionIsRightPanel"
          @open-execution-detail="emit('openExecutionDetail')"
          @openParagraph="emit('openParagraph')"
          @openParagraphDocument="(val: string) => emit('openParagraphDocument', val)"
          v-if="showSource(chatRecord) && index === chatRecord.answer_text_list.length - 1"
        />
      </div>
    </div>

    <div
      class="content"
      :style="{
        'padding-left': showAvatar ? 'var(--padding-left)' : '0',
        'padding-right': showUserAvatar ? 'var(--padding-left)' : '0',
      }"
      v-if="!selection"
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
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import KnowledgeSourceComponent from '@/components/ai-chat/component/knowledge-source-component/index.vue'
import OperationButton from '@/components/ai-chat/component/operation-button/index.vue'
import ContentItem from './items/index.vue'
import { type chatType } from '@/api/type/application'
import bus from '@/bus'

const props = defineProps<{
  chatRecord: chatType
  application: any
  loading: boolean
  sendMessage: (question: string, other_params_data?: any, chat?: chatType) => Promise<boolean>
  chatManagement: any
  type: 'log' | 'ai-chat' | 'debug-ai-chat' | 'share'
  executionIsRightPanel?: boolean
  selection?: boolean
}>()

const emit = defineEmits([
  'update:chatRecord',
  'openExecutionDetail',
  'openParagraph',
  'openParagraphDocument',
])

const showAvatar = computed(() => props.application.show_avatar == undefined ? true : props.application.show_avatar)
const showUserAvatar = computed(() => props.application.show_user_avatar == undefined ? true : props.application.show_user_avatar)

const chatMessage = (question: string, type: 'old' | 'new', other_params_data?: any) => {
  if (type === 'old') {
    props.chatRecord.answer_text_list.push([])
    props.sendMessage(question, other_params_data, props.chatRecord).then(() => {
      props.chatManagement.open(props.chatRecord.id)
      props.chatManagement.write(props.chatRecord.id)
    })
  } else {
    props.sendMessage(question, other_params_data)
  }
}

const openControl = (event: any) => {
  if (props.type !== 'log') bus.emit('open-control', event)
}

const answer_text_list = computed(() => {
  return props.chatRecord.answer_text_list.map((item: any) => {
    if (typeof item == 'string') return [{ content: item }]
    if (item instanceof Array) return item
    return [item]
  })
})

function showSource(row: any) {
  if (props.type === 'log') return true
  if (row.write_ed && 500 !== row.status) return true
  return false
}

const regenerationChart = (chat: chatType) => {
  const container = props.chatRecord?.upload_meta || props.chatRecord.execution_details?.find((d: any) => d.type === 'start-node')
  props.sendMessage(chat.problem_text, {
    re_chat: true,
    image_list: container?.image_list || [],
    document_list: container?.document_list || [],
    audio_list: container?.audio_list || [],
    video_list: container?.video_list || [],
    other_list: container?.other_list || [],
  })
}

const stopChat = (chat: chatType) => { props.chatManagement.stop(chat.id) }
const startChat = (chat: chatType) => { props.chatManagement.write(chat.id) }
</script>
