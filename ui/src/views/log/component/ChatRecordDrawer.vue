<template>
  <el-drawer
    v-model="visible"
    size="50%"
    append-to-body
    @close="closeHandel"
    class="chat-record-drawer"
  >
    <template #header>
      <h4>{{ data?.name }}</h4>
    </template>
    <div
      v-loading="paginationConfig.current_page === 1 && loading"
      class="h-full"
      style="padding: 24px 0"
    >
      <div v-infinite-scroll="loadDataset" :infinite-scroll-disabled="disabledScroll">
        <AiChat :data="data" :record="recordList" log></AiChat>
      </div>
      <div style="padding: 16px 10px">
        <el-divider class="custom-divider" v-if="recordList.length > 0 && loading">
          <el-text type="info"> 加载中...</el-text>
        </el-divider>
        <el-divider class="custom-divider" v-if="noMore">
          <el-text type="info"> 到底啦！</el-text>
        </el-divider>
      </div>
    </div>
    <template #footer>
      <div>
        <el-button>上一条</el-button>
        <el-button>下一条</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import logApi from '@/api/log'
import { type chatType } from '@/api/type/application'

const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  }
})

const emit = defineEmits(['changeId', 'close'])

const route = useRoute()
const {
  params: { id }
} = route
const loading = ref(false)
const visible = ref(false)
const recordList = ref<chatType[]>([])
const currentChatId = ref('')

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})

const noMore = computed(
  () =>
    recordList.value.length > 0 &&
    recordList.value.length === paginationConfig.total &&
    paginationConfig.total > 20 &&
    !loading.value
)
const disabledScroll = computed(
  () => recordList.value.length > 0 && (loading.value || noMore.value)
)

function closeHandel() {
  recordList.value = []
  currentChatId.value = ''
  paginationConfig.total = 0
  paginationConfig.current_page = 1
  emit('close')
}

function loadDataset() {
  if (paginationConfig.total > paginationConfig.page_size) {
    paginationConfig.current_page += 1
    getChatRecord()
  }
}

function getChatRecord() {
  logApi
    .getChatRecordLog(id as string, currentChatId.value, paginationConfig, loading)
    .then((res) => {
      paginationConfig.total = res.data.total
      recordList.value = [...recordList.value, ...res.data.records]
    })
}

// function nextRecord(id: string) {
//   currentChatId.value = id
//   emit('changeId', id)
//   recordList.value = []
//   paginationConfig.total = 0
//   paginationConfig.current_page = 1
//   getChatRecord()
// }

const open = (id: string) => {
  currentChatId.value = id
  getChatRecord()
  visible.value = true
}

defineExpose({
  open
})
</script>
<style lang="scss">
.chat-record-drawer {
  .el-drawer__body {
    background: var(--app-layout-bg-color);
    padding: 0;
  }
}
</style>
