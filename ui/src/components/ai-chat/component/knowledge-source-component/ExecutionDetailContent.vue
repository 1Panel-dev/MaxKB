<template>
  <el-scrollbar>
    <div class="execution-details p-8">
      <div v-if="isWorkFlow(props.appType)">
        <template v-for="(item, index) in arraySort(props.detail ?? [], 'index')" :key="index">
          <ExecutionDetailCard :data="item"> </ExecutionDetailCard>
        </template>
      </div>

      <template v-else>
        <div class="card-never border-r-6 mb-12">
          <h5 class="p-8-12">
            {{ $t('chat.paragraphSource.question') }}
          </h5>
          <div class="p-8-12 border-t-dashed lighter">
            <span class="mb-8">user: {{ problem }}</span>
          </div>
        </div>
        <div v-if="paddedProblem" class="card-never border-r-6 mb-12">
          <h5 class="p-8-12">
            {{ $t('chat.paragraphSource.questionPadded') }}
          </h5>
          <div class="p-8-12 border-t-dashed lighter">
            <span class="mb-8">user: {{ paddedProblem }}</span>
          </div>
        </div>
        <div v-if="system" class="card-never border-r-6 mb-12">
          <h5 class="p-8-12">
            {{ $t('views.application.form.roleSettings.label') }}
          </h5>
          <div class="p-8-12 border-t-dashed lighter">
            <span class="mb-8">{{ system }}</span>
          </div>
        </div>

        <div class="card-never border-r-6 mb-12">
          <h5 class="p-8-12">
            {{ $t('chat.history') }}
          </h5>
          <div class="p-8-12 border-t-dashed lighter">
            <div v-for="(msg, index) in historyRecord" :key="index">
              <span>{{ msg.role }}: </span>
              <span>{{ msg.content }}</span>
            </div>
          </div>
        </div>

        <div class="card-never border-r-6 mb-12">
          <h5 class="p-8-12">
            {{ $t('chat.executionDetails.currentChat') }}
          </h5>
          <div class="p-8-12 border-t-dashed lighter">
            <div class="mb-8">{{ $t('chat.executionDetails.knowedMessage') }}:</div>
            <div v-for="(msg, index) in currentChat" :key="index">
              <span>{{ msg.content }}</span>
            </div>
          </div>
        </div>

        <div class="card-never border-r-6 mb-12">
          <h5 class="p-8-12">
            {{ $t('chat.executionDetails.answer') }}
          </h5>
          <div class="p-8-12 border-t-dashed lighter">
            <div v-for="(msg, index) in AiResponse" :key="index">
              <span>{{ msg.content }}</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </el-scrollbar>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import ExecutionDetailCard from '@/components/ai-chat/component/knowledge-source-component/ExecutionDetailCard.vue'
import { arraySort } from '@/utils/array'
import { isWorkFlow } from '@/utils/application'

const props = defineProps<{
  detail?: any[]
  appType?: string
}>()

const messageList = computed(() => {
  const chat_step = props.detail?.find((item) => item.step_type == 'chat_step')
  if (chat_step) {
    return chat_step.message_list
  }
  return []
})
const get_padding_problem = () => {
  return props.detail?.find((item) => item.step_type == 'problem_padding')
}

const get_padded_problem = () => {
  return props.detail?.find((item) => item.step_type == 'problem_padding')
}

const paddedProblem = computed(() => {
  const problem_padded = get_padded_problem()
  if (problem_padded) {
    return problem_padded.padding_problem_text
  } else {
    return ''
  }
})

const problem = computed(() => {
  const problem_padding = get_padding_problem()
  if (problem_padding) {
    return problem_padding.problem_text
  }
  const user_list = messageList.value.filter((item: any) => item.role == 'user')
  if (user_list.length > 0) {
    return user_list[user_list.length - 1].content
  } else {
    return ''
  }
})

const system = computed(() => {
  const user_list = messageList.value.filter((item: any) => item.role == 'system')
  if (user_list.length > 0) {
    return user_list[user_list.length - 1].content
  } else {
    return ''
  }
})

const historyRecord = computed<any>(() => {
  const messages = messageList.value.filter((item: any) => item.role != 'system')
  if (messages.length > 2) {
    return messages.slice(0, messages.length - 2)
  }
  return []
})

const currentChat = computed(() => {
  const messages = messageList.value.filter((item: any) => item.role != 'system')
  return messages.slice(messages.length - 2, messages.length - 1)
})

const AiResponse = computed(() => {
  const messages = messageList.value?.filter((item: any) => item.role != 'system')
  return messages.slice(messages.length - 1, messages.length)
})


</script>
<style lang="scss" scoped>
.execution-details {
  max-height: calc(100vh - 260px);

  .arrow-icon {
    transition: 0.2s;
  }
}
</style>
