<template>
  <LayoutContainer header="对话日志">
    <div class="p-24">
      <div class="mb-16">
        <el-select v-model="history_day" class="mr-12 w-240" @change="changeHandle">
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
          clearable
        />
        <el-button class="float-right" @click="exportLog">导出</el-button>
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
        <el-table-column prop="star_num" align="right">
          <template #header>
            <div>
              <span>用户反馈</span>
              <el-popover :width="190" trigger="click" :visible="popoverVisible">
                <template #reference>
                  <el-button
                    style="margin-top: -2px"
                    :type="filter.min_star || filter.min_trample ? 'primary' : ''"
                    link
                    @click="popoverVisible = !popoverVisible"
                  >
                    <el-icon><Filter /></el-icon>
                  </el-button>
                </template>
                <div class="filter">
                  <div class="form-item mb-16">
                    <div @click.stop>
                      赞同 >=
                      <el-input-number
                        v-model="filter.min_star"
                        :min="0"
                        :step="1"
                        :value-on-clear="0"
                        controls-position="right"
                        style="width: 100px"
                        size="small"
                        step-strictly
                      />
                    </div>
                  </div>
                  <div class="form-item mb-16">
                    <div @click.stop>
                      反对 >=
                      <el-input-number
                        v-model="filter.min_trample"
                        :min="0"
                        :step="1"
                        :value-on-clear="0"
                        controls-position="right"
                        style="width: 100px"
                        size="small"
                        step-strictly
                      />
                    </div>
                  </div>
                </div>
                <div class="text-right">
                  <el-button size="small" @click="filterChange('clear')">清除</el-button>
                  <el-button type="primary" @click="filterChange" size="small">确认</el-button>
                </div>
              </el-popover>
            </div>
          </template>
          <template #default="{ row }">
            <span class="mr-8" v-if="!row.trample_num && !row.star_num"> - </span>
            <span class="mr-8" v-else>
              <span v-if="row.star_num">
                <AppIcon iconName="app-like-color"></AppIcon>
                {{ row.star_num }}
              </span>
              <span v-if="row.trample_num" class="ml-8">
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

        <!-- <el-table-column label="操作" width="70" align="left">
          <template #default="{ row }">
            <el-tooltip effect="dark" content="删除" placement="top">
              <el-button type="primary" text @click.stop="deleteLog(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column> -->
      </app-table>
    </div>
    <ChatRecordDrawer
      :next="nextChatRecord"
      :pre="preChatRecord"
      ref="ChatRecordRef"
      v-model:chatId="currentChatId"
      v-model:currentAbstract="currentAbstract"
      :application="detail"
      :pre_disable="pre_disable"
      :next_disable="next_disable"
      @refresh="refresh"
    />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep } from 'lodash'
import ChatRecordDrawer from './component/ChatRecordDrawer.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import logApi from '@/api/log'
import { datetimeFormat } from '@/utils/time'
import useStore from '@/stores'
import type { Dict } from '@/api/type/common'
const { application, log } = useStore()
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
const popoverVisible = ref(false)
const defaultFilter = {
  min_star: 0,
  min_trample: 0,
  comparer: 'and'
}
const filter = ref<any>({
  min_star: 0,
  min_trample: 0,
  comparer: 'and'
})

function filterChange(val: string) {
  if (val === 'clear') {
    filter.value = cloneDeep(defaultFilter)
  }
  getList()
  popoverVisible.value = false
}

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
    getList().then(() => {
      index = paginationConfig.page_size - 1
      currentChatId.value = tableData.value[index].id
      currentAbstract.value = tableData.value[index].abstract
    })
  } else {
    currentChatId.value = tableData.value[index].id
    currentAbstract.value = tableData.value[index].abstract
  }
}

function rowClickHandle(row: any, column?: any) {
  if (column && column.type === 'selection') {
    return
  }
  currentChatId.value = row.id
  currentAbstract.value = row.abstract
  ChatRecordRef.value.open()
}

const setRowClass = ({ row }: any) => {
  return currentChatId.value === row?.id ? 'highlight' : ''
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
    history_day: history_day.value,
    ...filter.value
  }
  if (search.value) {
    obj = { ...obj, abstract: search.value }
  }
  return log.asyncGetChatLog(id as string, paginationConfig, obj, loading).then((res: any) => {
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

const exportLog = () => {
  if (detail.value) {
    let obj: any = {
      history_day: history_day.value,
      ...filter.value
    }
    if (search.value) {
      obj = { ...obj, abstract: search.value }
    }
    logApi.exportChatLog(detail.value.id, detail.value.name, obj, loading)
  }
}
function refresh() {
  getList()
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
