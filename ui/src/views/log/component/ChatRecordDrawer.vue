<template>
  <el-drawer
    v-model="visible"
    size="50%"
    append-to-body
    @close="closeHandel"
    class="chat-record-drawer"
  >
    <template #header>
      <h4>{{ application?.name }}</h4>
    </template>
    <div
      v-loading="paginationConfig.current_page === 1 && loading"
      class="h-full"
      style="padding: 24px 0"
    >
      <div v-infinite-scroll="loadDataset" :infinite-scroll-disabled="disabledScroll">
        <AiChat :data="application" :record="recordList" log></AiChat>
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
        <el-button @click="pre" :disabled="pre_disable != undefined ? pre_disable : false"
          >上一条</el-button
        >
        <el-button @click="next" :disabled="next_disable != undefined ? next_disable : false"
          >下一条</el-button
        >
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import logApi from '@/api/log'
import { type chatType } from '@/api/type/application'
import { type ApplicationFormType } from '@/api/type/application'
const props = withDefaults(
  defineProps<{
    /**
     * 应用信息
     */
    application?: ApplicationFormType
    /**
     * 对话 记录id
     */
    id?: string
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

defineEmits(['update:id'])

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
  paginationConfig.total = 0
  paginationConfig.current_page = 1
}

function loadDataset() {
  if (paginationConfig.total > paginationConfig.page_size) {
    paginationConfig.current_page += 1
    getChatRecord()
  }
}

function getChatRecord() {
  if (props.id && visible.value) {
    logApi.getChatRecordLog(id as string, props.id, paginationConfig, loading).then((res) => {
      paginationConfig.total = res.data.total
      recordList.value = [...recordList.value, ...res.data.records]
    })
  }
}

watch(
  () => props.id,
  () => {
    recordList.value = []
    paginationConfig.total = 0
    paginationConfig.current_page = 1
    getChatRecord()
  }
)

const open = () => {
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
