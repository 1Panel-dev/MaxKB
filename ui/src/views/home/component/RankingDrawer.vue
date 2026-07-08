<template>
  <el-drawer
    v-model="drawerVisible"
    :title="$t('home.rankDetail')"
    size="1000"
    :append-to-body="true"
  >
    <el-tabs v-model="activeName" @tab-change="handleClick">
      <div class="flex-between">
        <div class="flex align-center mb-12 mt-12">
          <el-input
            v-model="search_text"
            class="mr-12 ml-12 w-240"
            :placeholder="$t('common.searchBar.placeholder')"
            @change="searchHandle"
          >
            <template #suffix>
              <el-icon class="el-input__icon">
                <search />
              </el-icon>
            </template>
          </el-input>

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
            :start-placeholder="$t('home.startDatePlaceholder')"
            :end-placeholder="$t('home.endDatePlaceholder')"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="changeDayRangeHandle"
          />
        </div>
        <el-button @click="exportHandle">
          {{ $t('common.export') }}
        </el-button>
      </div>

      <el-tab-pane
        :label="'Tokens ' + $t('home.usage') + ' · Top ' + $t('views.application.title')"
        name="tokens_agent"
      >
        <app-table
          class="mt-16"
          :data="tokensRankding"
          :pagination-config="paginationConfig"
          @sizeChange="handleSizeChange"
          @changePage="getDetail"
          :maxTableHeight="280"
          :row-key="(row: any) => row.id"
          v-loading="loading"
        >
          <el-table-column :label="$t('home.rank')" width="80">
            <template #default="{ row, $index }">
              <span class="rank" :class="'rank-' + ($index + 1)">{{ $index + 1 }}</span>
            </template>
          </el-table-column>

          <el-table-column
            prop="name"
            min-width="100"
            show-overflow-tooltip
            :label="$t('views.application.form.appName.label')"
          />
          <el-table-column min-width="100" :label="'Tokens ' + $t('home.usage')" align="right">
            <template #default="{ row }">
              {{ numberFormat(row.total_tokens) }}
            </template>
          </el-table-column>
          <el-table-column width="200" :label="$t('home.proportion')">
            <template #default="{ row }">
              <el-progress
                :percentage="
                  TokenTotal
                    ? Number((((row?.total_tokens || 0) / TokenTotal) * 100).toFixed(1))
                    : 0
                "
              />
            </template>
          </el-table-column>
          <el-table-column
            min-width="80"
            show-overflow-tooltip
            :label="$t('home.chatCount')"
            align="right"
          >
            <template #default="{ row }">
              {{ numberFormat(row.chat_record_count) }}
            </template>
          </el-table-column>
          <el-table-column
            min-width="80"
            show-overflow-tooltip
            :label="$t('home.activeUsers')"
            align="right"
          >
            <template #default="{ row }">
              {{ numberFormat(row.chat_user_count) }}
            </template>
          </el-table-column>
          <el-table-column
            min-width="100"
            show-overflow-tooltip
            :label="$t('home.average‌') + ' tokens/' + $t('views.system.time')"
            align="right"
          >
            <template #default="{ row }">
              {{
                numberFormat(Number((row?.total_tokens / row?.chat_record_count || 0).toFixed(1)))
              }}
            </template>
          </el-table-column>
        </app-table>
      </el-tab-pane>
      <el-tab-pane
        :label="$t('home.chatCount') + ' · Top ' + $t('views.application.title')"
        name="questions_agent"
      >
        <app-table
          class="mt-16"
          :data="questionRanking"
          :pagination-config="paginationConfig"
          @sizeChange="handleSizeChange"
          @changePage="getDetail"
          :maxTableHeight="280"
          :row-key="(row: any) => row.id"
          v-loading="loading"
        >
          <el-table-column :label="$t('home.rank')" width="80">
            <template #default="{ row, $index }">
              <span class="rank" :class="'rank-' + ($index + 1)">{{ $index + 1 }}</span>
            </template>
          </el-table-column>

          <el-table-column
            prop="name"
            min-width="100"
            show-overflow-tooltip
            :label="$t('views.application.form.appName.label')"
          />
          <el-table-column
            min-width="80"
            show-overflow-tooltip
            :label="$t('home.chatCount')"
            align="right"
          >
            <template #default="{ row }">
              {{ numberFormat(row.chat_record_count) }}
            </template>
          </el-table-column>
          <el-table-column width="200" :label="$t('home.proportion')">
            <template #default="{ row }">
              <el-progress
                :percentage="
                  ChatRecordTotal
                    ? Number((((row?.chat_record_count || 0) / ChatRecordTotal) * 100).toFixed(1))
                    : 0
                "
              />
            </template>
          </el-table-column>
          <el-table-column
            min-width="80"
            show-overflow-tooltip
            :label="$t('home.activeUsers')"
            align="right"
          >
            <template #default="{ row }">
              {{ numberFormat(row.chat_user_count) }}
            </template>
          </el-table-column>

          <el-table-column
            min-width="80"
            show-overflow-tooltip
            :label="$t('home.perDialogueRounds')"
            align="right"
          >
            <template #default="{ row }">
              {{
                numberFormat(
                  Number((row?.chat_record_count / row?.chat_user_count || 0).toFixed(1)),
                )
              }}
            </template>
          </el-table-column>
        </app-table>
      </el-tab-pane>
      <el-tab-pane
        :label="'Tokens ' + $t('home.usage') + ' · Top ' + $t('views.chatLog.table.user')"
        name="user_tokens_agent"
      >
        <app-table
          class="mt-16"
          :data="userTokensRanking"
          :pagination-config="paginationConfig"
          @sizeChange="handleSizeChange"
          @changePage="getDetail"
          :maxTableHeight="280"
          :row-key="(row: any) => row.id"
          v-loading="loading"
        >
          <el-table-column :label="$t('home.rank')" width="80">
            <template #default="{ row, $index }">
              <span class="rank" :class="'rank-' + ($index + 1)">{{ $index + 1 }}</span>
            </template>
          </el-table-column>

          <el-table-column
            min-width="100"
            show-overflow-tooltip
            :label="$t('views.chatLog.table.user')"
          >
            <template #default="{ row }">
              {{ row?.asker?.username || '-' }}
            </template>
          </el-table-column>
          <el-table-column min-width="100" :label="'Tokens ' + $t('home.usage')" align="right">
            <template #default="{ row }">
              {{ numberFormat(row.total_tokens) }}
            </template>
          </el-table-column>
          <el-table-column width="200" :label="$t('home.proportion')">
            <template #default="{ row }">
              <el-progress
                :percentage="
                  TokenTotal ? Number((((row.total_tokens || 0) / TokenTotal) * 100).toFixed(1)) : 0
                "
              />
            </template>
          </el-table-column>
          <el-table-column
            min-width="80"
            show-overflow-tooltip
            :label="$t('home.chatCount')"
            align="right"
          >
            <template #default="{ row }">
              {{ numberFormat(row.chat_record_count) }}
            </template>
          </el-table-column>
          <el-table-column
            min-width="100"
            show-overflow-tooltip
            :label="$t('home.average‌') + ' tokens/' + $t('views.system.time')"
            align="right"
          >
            <template #default="{ row }">
              {{ numberFormat(Number((row.total_tokens / row.chat_record_count || 0).toFixed(1))) }}
            </template>
          </el-table-column>
          <!-- <el-table-column
            prop="name"
            min-width="100"
            show-overflow-tooltip
            :label="$t('home.commonlyAgents')"
          /> -->
        </app-table>
      </el-tab-pane>
    </el-tabs>
  </el-drawer>
</template>
<script setup lang="ts">
import { ref, onMounted, watch, computed, reactive } from 'vue'
import useStore from '@/stores'
import { numberFormat } from '@/utils/common'
import homeApi from '@/api/home-page/home'
import { nowDate, beforeDay } from '@/utils/time'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import { t } from '@/locales'
const { user } = useStore()
const drawerVisible = ref(false)
const activeName = ref('tokens_agent')

const loading = ref(false)

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})
const tokensRankding = ref<any[]>([])
const questionRanking = ref<any[]>()
const userTokensRanking = ref<any[]>()

const search_text = ref('')
function searchHandle() {
  getDetail()
}

function handleClick(tab: any) {
  activeName.value = tab
  paginationConfig.current_page = 1
  changeDayHandle(history_day.value)
}

const dayOptions = [
  {
    value: 7,
    label: t('home.pastDayOptions.past7Days'),
  },
  {
    value: 30,
    label: t('home.pastDayOptions.past30Days'),
  },
  {
    value: 90,
    label: t('home.pastDayOptions.past90Days'),
  },
  {
    value: 183,
    label: t('home.pastDayOptions.past183Days'),
  },
  {
    value: 'other',
    label: t('common.custom'),
  },
]

const history_day = ref<number | string>(7)

// 日期组件时间
const daterangeValue = ref('')
// 提交日期时间
const daterange = ref({
  start_time: '',
  end_time: '',
})
function changeDayHandle(val: number | string) {
  if (val !== 'other') {
    daterange.value.start_time = beforeDay(val)
    daterange.value.end_time = nowDate
    getDetail()
  }
}

function changeDayRangeHandle(val: string) {
  daterange.value.start_time = val[0]
  daterange.value.end_time = val[1]
  getDetail()
}

const ChatRecordTotal = ref<any>(0)
const TokenTotal = ref<any>(0)

function getDetail() {
  if (activeName.value === 'tokens_agent') {
    homeApi.getTokensAggregation(daterange.value, loading).then((res: any) => {
      TokenTotal.value = res.data
    })
    homeApi
      .getTokensRanking(paginationConfig, { name: search_text.value, ...daterange.value }, loading)
      .then((res: any) => {
        paginationConfig.total = res.data?.total || 0
        tokensRankding.value = res.data?.records
      })
  } else if (activeName.value === 'questions_agent') {
    homeApi.getChatRecordAggregation(daterange.value, loading).then((res: any) => {
      ChatRecordTotal.value = res.data
    })
    homeApi
      .getQuestionsRanking(
        paginationConfig,
        { name: search_text.value, ...daterange.value },
        loading,
      )
      .then((res: any) => {
        paginationConfig.total = res.data?.total || 0
        questionRanking.value = res.data?.records
      })
  } else if (activeName.value === 'user_tokens_agent') {
    homeApi.getTokensAggregation(daterange.value, loading).then((res: any) => {
      TokenTotal.value = res.data
    })
    homeApi
      .getUserTokensRanking(
        paginationConfig,
        { name: search_text.value, ...daterange.value },
        loading,
      )
      .then((res: any) => {
        paginationConfig.total = res.data?.total || 0
        userTokensRanking.value = res.data?.records
      })
  }
}
function handleSizeChange() {
  paginationConfig.current_page = 1
  changeDayHandle(history_day.value)
}

function exportHandle() {
  console.log('sss')
  if (activeName.value === 'tokens_agent') {
    homeApi
      .exportTokensRankings({ name: search_text.value, ...daterange.value }, loading)
      .catch((e: any) => {
        if (e.response.status !== 403) {
          e.response.data.text().then((res: string) => {
            MsgError(`${t('views.application.tip.ExportError')}:${JSON.parse(res).message}`)
          })
        }
      })
  } else if (activeName.value === 'questions_agent') {
    homeApi
      .exportQuestionsRankings({ name: search_text.value, ...daterange.value }, loading)
      .catch((e: any) => {
        if (e.response.status !== 403) {
          e.response.data.text().then((res: string) => {
            MsgError(`${t('views.application.tip.ExportError')}:${JSON.parse(res).message}`)
          })
        }
      })
  } else if (activeName.value === 'user_tokens_agent') {
    homeApi
      .exportUserTokensRankings({ name: search_text.value, ...daterange.value }, loading)
      .catch((e: any) => {
        if (e.response.status !== 403) {
          e.response.data.text().then((res: string) => {
            MsgError(`${t('views.application.tip.ExportError')}:${JSON.parse(res).message}`)
          })
        }
      })
  }
}

watch(drawerVisible, (bool) => {
  if (!bool) {
    search_text.value = ''
    activeName.value = 'tokens_agent'
    tokensRankding.value = []
    paginationConfig.current_page = 1
    paginationConfig.total = 0
    history_day.value = 7
  }
})

const open = (name: string, historyDay: number | string, daterangeVal: string, daterange: any) => {
  activeName.value = name
  history_day.value = historyDay
  daterangeValue.value = daterangeVal
  daterange.value = daterange
  changeDayHandle(history_day.value)
  drawerVisible.value = true
}
defineExpose({
  open,
})
</script>
<style lang="scss" scoped></style>
