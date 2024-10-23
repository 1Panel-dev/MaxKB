<template>
  <LayoutContainer header="对话日志">
    <div class="p-24">
      <div class="mb-16">
        <el-select v-model="history_day" class="mr-12 w-120" @change="changeDayHandle">
          <el-option
            v-for="item in dayOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-date-picker
          v-if="history_day === 'other'"
          v-model="daterangeValue"
          type="daterange"
          :start-placeholder="$t('views.applicationOverview.monitor.startDatePlaceholder')"
          :end-placeholder="$t('views.applicationOverview.monitor.endDatePlaceholder')"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="changeDayRangeHandle"
        />
        <el-input
          v-model="search"
          @change="getList"
          placeholder="搜索"
          prefix-icon="Search"
          class="w-240"
          style="margin-left: 10px"
          clearable
        />
        <div style="display: flex; align-items: center" class="float-right">
          <el-button @click="dialogVisible = true" type="primary">清除策略</el-button>
          <el-button @click="exportLog">导出</el-button>
        </div>
      </div>

      <app-table
        :data="tableData"
        :pagination-config="paginationConfig"
        @sizeChange="handleSizeChange"
        @changePage="getList"
        @row-click="rowClickHandle"
        v-loading="loading"
        :row-class-name="setRowClass"
        @selection-change="handleSelectionChange"
        class="log-table"
      >
        <el-table-column type="selection" width="55" />
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
                    <el-icon>
                      <Filter />
                    </el-icon>
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
    <el-dialog
      title="清除策略"
      v-model="dialogVisible"
      width="25%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <span>删除</span>
      <el-input-number
        v-model="days"
        controls-position="right"
        min="1"
        max="100000"
        style="width: 110px; margin-left: 8px; margin-right: 8px"
      ></el-input-number>
      <span>天之前的对话记录</span>
      <template #footer>
        <div class="dialog-footer" style="margin-top: 16px">
          <el-button @click="dialogVisible = false">{{
            $t('layout.topbar.avatar.dialog.cancel')
          }}</el-button>
          <el-button type="primary" @click="saveCleanTime">
            {{ $t('layout.topbar.avatar.dialog.save') }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep } from 'lodash'
import ChatRecordDrawer from './component/ChatRecordDrawer.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import logApi from '@/api/log'
import { beforeDay, datetimeFormat, nowDate } from '@/utils/time'
import useStore from '@/stores'
import type { Dict } from '@/api/type/common'
import { t } from '@/locales'

const { application, log } = useStore()
const route = useRoute()
const {
  params: { id }
} = route

const dayOptions = [
  {
    value: 7,
    // @ts-ignore
    label: t('views.applicationOverview.monitor.pastDayOptions.past7Days') // 使用 t 方法来国际化显示文本
  },
  {
    value: 30,
    label: t('views.applicationOverview.monitor.pastDayOptions.past30Days')
  },
  {
    value: 90,
    label: t('views.applicationOverview.monitor.pastDayOptions.past90Days')
  },
  {
    value: 183,
    label: t('views.applicationOverview.monitor.pastDayOptions.past183Days')
  },
  {
    value: 'other',
    label: t('views.applicationOverview.monitor.pastDayOptions.other')
  }
]
const daterangeValue = ref('')
// 提交日期时间
const daterange = ref({
  start_time: '',
  end_time: ''
})
const multipleSelection = ref<any[]>([])

const ChatRecordRef = ref()
const loading = ref(false)
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})
const dialogVisible = ref(false)
const days = ref<number>(180)
const tableData = ref<any[]>([])
const tableIndexMap = computed<Dict<number>>(() => {
  return tableData.value
    .map((row, index) => ({
      [row.id]: index
    }))
    .reduce((pre, next) => ({ ...pre, ...next }), {})
})
const history_day = ref<number | string>(7)

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

const handleSelectionChange = (val: any[]) => {
  multipleSelection.value = val
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

function getList() {
  paginationConfig.current_page = 1
  let obj: any = {
    start_time: daterange.value.start_time,
    end_time: daterange.value.end_time,
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
    days.value = res.data.clean_time
  })
}
const exportLog = () => {
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  if (detail.value) {
    let obj: any = {
      start_time: daterange.value.start_time,
      end_time: daterange.value.end_time,
      ...filter.value
    }
    if (search.value) {
      obj = { ...obj, abstract: search.value }
    }

    logApi.exportChatLog(detail.value.id, detail.value.name, obj, { select_ids: arr }, loading)
  }
}

function refresh() {
  getList()
}

function changeDayRangeHandle(val: string) {
  daterange.value.start_time = val[0]
  daterange.value.end_time = val[1]
  getList()
}

function changeDayHandle(val: number | string) {
  if (val !== 'other') {
    daterange.value.start_time = beforeDay(val)
    daterange.value.end_time = nowDate
    getList()
  }
}

function saveCleanTime() {
  const data = detail.value
  data.clean_time = days.value
  application
    .asyncPutApplication(id as string, data, loading)
    .then(() => {
      MsgSuccess('保存成功')
      dialogVisible.value = false
      getDetail()
    })
    .catch(() => {
      dialogVisible.value = false
    })
}

onMounted(() => {
  changeDayHandle(history_day.value)
  getDetail()
})
</script>
<style lang="scss" scoped>
.log-table {
  :deep(tr) {
    cursor: pointer;
  }
}
</style>
