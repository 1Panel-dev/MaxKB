<template>
  <LayoutContainer header="对话日志">
    <div class="p-24">
      <div class="mb-16">
        <el-select v-model="history_day" class="mr-12" @change="changeHandle">
          <el-option
            v-for="item in dayOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-input
          v-model="search"
          @change="getList"
          placeholder="搜索"
          prefix-icon="Search"
          class="w-240"
        />
      </div>

      <app-table
        :data="tableData"
        :pagination-config="paginationConfig"
        @sizeChange="handleSizeChange"
        @changePage="getList"
        @row-click="rowClickHandle"
        v-loading="loading"
        :row-class-name="setRowClass"
        class="log-table"
      >
        <el-table-column prop="abstract" label="摘要" show-overflow-tooltip />
        <el-table-column prop="chat_record_count" label="对话提问数" align="right" />
        <el-table-column prop="star_num" label="用户反馈" align="right">
          <template #default="{ row }">
            <span v-if="!row.trample_num && !row.star_num"> - </span>
            <span v-else>
              <span v-if="row.star_num">
                <AppIcon iconName="app-like-color"></AppIcon>
                {{ row.star_num }}
              </span>
              <span v-if="row.trample_num" class="ml-4">
                <AppIcon iconName="app-oppose-color"></AppIcon>
                {{ row.trample_num }}
              </span>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="mark_sum" label="改进标注" align="right" />
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            {{ datetimeFormat(row.create_time) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="70" align="center">
          <template #default="{ row }">
            <el-tooltip effect="dark" content="删除" placement="top">
              <el-button type="primary" text @click.stop="deleteLog(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </app-table>
    </div>
    <ChatRecordDrawer
      :next="nextChatRecord"
      :pre="preChatRecord"
      ref="ChatRecordRef"
      v-model:chartId="currentChatId"
      v-model:currentAbstract="currentAbstract"
      :application="detail"
      :pre_disable="pre_disable"
      :next_disable="next_disable"
    />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import ChatRecordDrawer from './component/ChatRecordDrawer.vue'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import logApi from '@/api/log'
import { datetimeFormat } from '@/utils/time'
import useStore from '@/stores'
import type { Dict } from '@/api/type/common'
const { application } = useStore()
const route = useRoute()
const {
  params: { id }
} = route

const dayOptions = [
  {
    value: 7,
    label: '过去7天'
  },
  {
    value: 30,
    label: '过去30天'
  },
  {
    value: 90,
    label: '过去90天'
  },
  {
    value: 183,
    label: '过去半年'
  }
]

const ChatRecordRef = ref()
const loading = ref(false)
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})
const tableData = ref<any[]>([])
const tableIndexMap = computed<Dict<number>>(() => {
  return tableData.value
    .map((row, index) => ({
      [row.id]: index
    }))
    .reduce((pre, next) => ({ ...pre, ...next }), {})
})
const history_day = ref(7)
const search = ref('')
const detail = ref<any>(null)

const currentChatId = ref<string>('')
const currentAbstract = ref<string>('')

/**
 * 下一页
 */
const nextChatRecord = () => {
  let index = tableIndexMap.value[currentChatId.value] + 1
  if (index >= tableData.value.length) {
    if (
      index + (paginationConfig.current_page - 1) * paginationConfig.page_size >=
      paginationConfig.total - 1
    ) {
      return
    }
    paginationConfig.current_page = paginationConfig.current_page + 1
    getList().then(() => {
      index = 0
      currentChatId.value = tableData.value[index].id
      currentAbstract.value = tableData.value[index].abstract
    })
  } else {
    currentChatId.value = tableData.value[index].id
    currentAbstract.value = tableData.value[index].abstract
  }
}
const pre_disable = computed(() => {
  let index = tableIndexMap.value[currentChatId.value] - 1
  return index < 0 && paginationConfig.current_page <= 1
})

const next_disable = computed(() => {
  let index = tableIndexMap.value[currentChatId.value] + 1
  return (
    index >= tableData.value.length &&
    index + (paginationConfig.current_page - 1) * paginationConfig.page_size >=
      paginationConfig.total - 1
  )
})
/**
 * 上一页
 */
const preChatRecord = () => {
  let index = tableIndexMap.value[currentChatId.value] - 1

  if (index < 0) {
    if (paginationConfig.current_page <= 1) {
      return
    }
    paginationConfig.current_page = paginationConfig.current_page - 1
    getList().then((ok) => {
      index = paginationConfig.page_size - 1
      currentChatId.value = tableData.value[index].id
      currentAbstract.value = tableData.value[index].abstract
    })
  } else {
    currentChatId.value = tableData.value[index].id
    currentAbstract.value = tableData.value[index].abstract
  }
}

function rowClickHandle(row: any) {
  currentChatId.value = row.id
  currentAbstract.value = row.abstract
  ChatRecordRef.value.open()
}

const setRowClass = ({ row }: any) => {
  return currentChatId.value === row?.id ? 'hightlight' : ''
}

function deleteLog(row: any) {
  MsgConfirm(`是否删除对话：${row.abstract} ?`, `删除后无法恢复，请谨慎操作。`, {
    confirmButtonText: '删除',
    confirmButtonClass: 'danger'
  })
    .then(() => {
      loading.value = true
      logApi.delChatLog(id as string, row.id, loading).then(() => {
        MsgSuccess('删除成功')
        getList()
      })
    })
    .catch(() => {})
}

function handleSizeChange() {
  paginationConfig.current_page = 1
  getList()
}

function changeHandle(val: number) {
  history_day.value = val
  paginationConfig.current_page = 1
  getList()
}

function getList() {
  let obj: any = {
    history_day: history_day.value
  }
  if (search.value) {
    obj = { ...obj, abstract: search.value }
  }
  return logApi.getChatLog(id as string, paginationConfig, obj, loading).then((res) => {
    tableData.value = res.data.records
    if (currentChatId.value) {
      currentChatId.value = tableData.value[0]?.id
    }
    paginationConfig.total = res.data.total
  })
}

function getDetail() {
  application.asyncGetApplicationDetail(id as string, loading).then((res: any) => {
    detail.value = res.data
  })
}

onMounted(() => {
  getList()
  getDetail()
})
</script>
<style lang="scss" scoped>
.log-table tr {
  cursor: pointer;
}
</style>
