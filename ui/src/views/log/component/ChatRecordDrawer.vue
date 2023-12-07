<template>
  <el-drawer
    v-model="visible"
    size="50%"
    append-to-body
    @close="closeHandel"
    class="chat-record-drawer"
  >
    <template #header>
      <h4>应用标题</h4>
    </template>
    <AiChat record></AiChat>
    <template #footer>
      <div>
        <el-button>上一条</el-button>
        <el-button>下一条</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRoute } from 'vue-router'
import logApi from '@/api/log'
const route = useRoute()
const {
  params: { id }
} = route

const loading = ref(false)
const visible = ref(false)

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})

function closeHandel() {}

function getChatRecord(chatId) {
  logApi.getChatRecordLog(id as string, chatId, paginationConfig, loading).then((res) => {
    // tableData.value = res.data.records
    paginationConfig.total = res.data.total
  })
}

const open = (id) => {
  getChatRecord(id)
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
    padding: 24px 0;
  }
}
</style>
