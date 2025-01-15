<template>
  <el-drawer v-model="visible" size="60%" @close="closeHandle" class="chat-record-drawer">
    <template #header>
      <h4 class="single-line">{{ currentAbstract }}</h4>
    </template>
    <div
      v-loading="paginationConfig.current_page === 1 && loading"
      class="h-full"
      style="padding: 24px 0"
    >
      <AiChat
        ref="AiChatRef"
        :application-details="application"
        type="log"
        :record="recordList"
        @scroll="handleScroll"
      >
      </AiChat>
    </div>
    <template #footer>
      <div>
        <el-button @click="pre" :disabled="pre_disable || loading">{{
          $t('views.log.buttons.prev')
        }}</el-button>
        <el-button @click="next" :disabled="next_disable || loading">{{
          $t('views.log.buttons.next')
        }}</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { type ApplicationFormType, type chatType } from '@/api/type/application'
import useStore from '@/stores'
const AiChatRef = ref()
const { log } = useStore()
const props = withDefaults(
  defineProps<{
    /**
     * 应用信息
     */
    application?: ApplicationFormType
    /**
     * 对话 记录id
     */
    chatId: string
    currentAbstract: string
    /**
     * 下一条
     */
    next: () => void
    /**
     * 上一条
     */
    pre: () => void

    pre_disable: boolean

    next_disable: boolean
  }>(),
  {}
)

const emit = defineEmits(['update:chatId', 'update:currentAbstract', 'refresh'])

const route = useRoute()
const {
  params: { id }
} = route
const loading = ref(false)
const visible = ref(false)
const recordList = ref<chatType[]>([])

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})

function closeHandle() {
  recordList.value = []
  paginationConfig.total = 0
  paginationConfig.current_page = 1
}

function getChatRecord() {
  return log
    .asyncChatRecordLog(id as string, props.chatId, paginationConfig, loading)
    .then((res: any) => {
      paginationConfig.total = res.data.total
      const list = res.data.records
      recordList.value = [...list, ...recordList.value].sort((a, b) =>
        a.create_time.localeCompare(b.create_time)
      )
      if (paginationConfig.current_page === 1) {
        nextTick(() => {
          // 将滚动条滚动到最下面
          AiChatRef.value.setScrollBottom()
        })
      }
    })
}

watch(
  () => props.chatId,
  () => {
    recordList.value = []
    paginationConfig.total = 0
    paginationConfig.current_page = 1
    if (props.chatId) {
      getChatRecord()
    }
  }
)

watch(visible, (bool) => {
  if (!bool) {
    emit('update:chatId', '')
    emit('update:currentAbstract', '')
    emit('refresh')
  }
})

function handleScroll(event: any) {
  if (
    props.chatId !== 'new' &&
    event.scrollTop === 0 &&
    paginationConfig.total > recordList.value.length
  ) {
    const history_height = event.dialogScrollbar.offsetHeight
    paginationConfig.current_page += 1
    getChatRecord().then(() => {
      event.scrollDiv.setScrollTop(event.dialogScrollbar.offsetHeight - history_height)
    })
  }
}

const open = () => {
  visible.value = true
}

defineExpose({
  open
})
</script>
<style lang="scss">
.single-line {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-record-drawer {
  .el-drawer__body {
    background: var(--app-layout-bg-color);
    padding: 0;
  }

  :deep(.el-divider__text) {
    background: var(--app-layout-bg-color);
  }
}
</style>
