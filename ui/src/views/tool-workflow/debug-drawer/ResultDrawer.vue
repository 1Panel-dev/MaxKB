<template>
  <el-drawer
    v-if="resultDrawer"
    v-model="resultDrawer"
    :title="$t('common.debug')"
    direction="rtl"
    :before-close="close"
    :destroy-on-close="true"
    :modal="false"
    size="800px"
    class="tool-debug-result-drawer"
  >
    <template #header>
      <div class="flex align-center" style="margin-left: -8px">
        <el-button class="cursor mr-4" link @click.prevent="close">
          <el-icon :size="20">
            <Back />
          </el-icon>
        </el-button>
        <h4>{{ $t('views.tool.toolWorkflow.debugResult') }}</h4>
      </div>
    </template>
    <el-tabs v-model="activeName" style="margin-top: -10px">
      <el-tab-pane label="输出" name="result">
        <div class="scrollbar-height">
          <h4 class="title-decoration-1 mb-16 mt-8">回复内容</h4>

          <AnswerContent
            :application="details"
            :loading="loading"
            v-model:chat-record="currentChat"
            type="ai-chat"
            :send-message="sendMessage"
            :chat-management="ChatManagement"
            :executionIsRightPanel="false"
            @open-execution-detail="() => {}"
            @openParagraph="() => {}"
            @openParagraphDocument="() => {}"
            :selection="true"
          ></AnswerContent>
          <div v-if="toolRecord">
            <h4 class="title-decoration-1 mb-16 mt-16">输出参数</h4>
            <div class="mb-16" v-if="isSuccess !== undefined">
              <el-alert
                v-if="isSuccess"
                :title="$t('views.tool.form.debug.runSuccess')"
                type="success"
                show-icon
                :closable="false"
              />
              <el-alert
                v-else
                :title="$t('views.tool.form.debug.runFailed')"
                type="error"
                show-icon
                :closable="false"
              />
            </div>
            <el-card
              style="overflow: auto"
              :class="isSuccess ? '' : 'color-danger'"
              class="pre-wrap"
              shadow="never"
            >
              {{ output }}
            </el-card>
          </div>
        </div>
      </el-tab-pane>
      <el-tab-pane label="执行详情" name="executionDetails">
        <el-scrollbar>
          <div class="scrollbar-height">
            <template
              v-for="(item, index) in arraySort(executionDetails ?? [], 'index')"
              :key="index"
            >
              <ExecutionDetailCard :data="item"> </ExecutionDetailCard>
            </template>
          </div>
        </el-scrollbar>
      </el-tab-pane>
    </el-tabs>
  </el-drawer>
</template>
<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { randomId } from '@/utils/common'
import { ChatManagement, type chatType } from '@/api/type/application'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { t } from '@/locales'
import AnswerContent from '@/components/ai-chat/component/answer-content/index.vue'
import ExecutionDetailCard from '@/components/execution-detail-card/index.vue'
import { arraySort } from '@/utils/array'
import { getWrite } from '@/utils/chat'

const route = useRoute()
const {
  params: { folderId },
  /*
  folderId 可以区分 resource-management shared还是 workspace
  */
} = route as any
const isShared = computed(() => {
  return folderId === 'share'
})
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else if (route.path.includes('share/')) {
    return 'workspaceShare'
  } else {
    return 'workspace'
  }
})
const details = {
  show_avatar: false,
  show_user_avatar: false,
}
const activeName = ref<string>('result')
const currentToolId = ref<string>()
const currentData = ref<any>({})
const emit = defineEmits(['close'])
const output = computed(() => {
  if (toolRecord.value) {
    return toolRecord.value.meta.output
  }
  return {}
})

const executionDetails = computed(() => {
  if (toolRecord.value) {
    return Object.values(toolRecord.value.meta.details)
  }
  return []
})

const isSuccess = computed(() => {
  if (toolRecord.value) {
    return toolRecord.value.state == 'FAILURE' ? false : true
  }
  return undefined
})

const toolRecord = ref<any>()

const execute = (toolId: string, data: any) => {
  currentToolId.value = toolId
  currentData.value = data
  ChatManagement.addChatRecord(currentChat, 50, loading)
  ChatManagement.write(currentChat.id)
  return loadSharedApi({ type: 'tool', isShared: isShared.value, systemType: apiType.value })
    .debugToolWorkflow(toolId, data)
    .then((response: any) => {
      if (response.status === 460) {
        return Promise.reject(t('chat.tip.errorIdentifyMessage'))
      } else if (response.status === 461) {
        return Promise.reject(t('chat.tip.errorLimitMessage'))
      } else {
        const reader = response.body.getReader()
        // 处理流数据
        const write = getWrite(
          currentChat,
          reader,
          response.headers.get('Content-Type') !== 'application/json',
        )
        return write()
      }
    })
    .finally(() => {
      getToolRecord()
      ChatManagement.close(currentChat.id)
    })
    .catch((e: any) => {
      console.log(e)
    })
}
const loading = ref<boolean>(false)
const currentChat = reactive<any>({
  id: randomId(),
  answer_text_list: [[]],
  buffer: [],
  reasoning_content: '',
  reasoning_content_buffer: [],
  write_ed: false,
  is_stop: false,
  record_id: '',
  chat_id: '',
  vote_status: '-1',
  status: undefined,
})

const sendMessage = (val: string, other_params_data?: any, chat?: chatType) => {
  loadSharedApi({ type: 'tool', isShared: isShared.value, systemType: apiType.value })
    .debugToolWorkflow(currentToolId.value, { ...other_params_data, ...currentData.value })
    .then((response: any) => {
      if (response.status === 460) {
        return Promise.reject(t('chat.tip.errorIdentifyMessage'))
      } else if (response.status === 461) {
        return Promise.reject(t('chat.tip.errorLimitMessage'))
      } else {
        const reader = response.body.getReader()
        // 处理流数据
        const write = getWrite(
          currentChat,
          reader,
          response.headers.get('Content-Type') !== 'application/json',
        )
        return write()
      }
    })
    .finally(() => {
      ChatManagement.close(currentChat.id)
      getToolRecord()
    })
    .catch((e: any) => {
      console.log(e)
    })
  return Promise.resolve(true)
}
const getToolRecord = () => {
  loadSharedApi({
    type: 'tool',
    isShared: isShared.value,
    systemType: apiType.value,
  })
    .getToolRecordDetail(currentToolId.value, currentChat.record_id)
    .then((ok: any) => {
      toolRecord.value = ok.data
    })
}

const resultDrawer = ref<boolean>(false)
const open = (toolId: string, data: any) => {
  resultDrawer.value = true
  execute(toolId, data)
}
const close = () => {
  ChatManagement.close(currentChat.id)
  emit('close')
  resultDrawer.value = false
  toolRecord.value = null
  currentChat.value = {
    id: randomId(),
    answer_text_list: [[]],
    buffer: [],
    reasoning_content: '',
    reasoning_content_buffer: [],
    write_ed: false,
    is_stop: false,
    record_id: '',
    chat_id: '',
    vote_status: '-1',
    status: undefined,
  }
}

defineExpose({ open, close })
</script>
<style lang="scss" scoped>
.tool-debug-result-drawer {
  .el-drawer__body {
    padding: 16px !important;
  }
  .scrollbar-height {
    max-height: calc(100vh - 134px);
    overflow: auto;
  }
}
</style>
