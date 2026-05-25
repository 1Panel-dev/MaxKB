<template>
  <el-drawer
    v-model="drawerVisible"
    :title="$t('layout.home.rankDetail')"
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
            :start-placeholder="$t('views.applicationOverview.monitor.startDatePlaceholder')"
            :end-placeholder="$t('views.applicationOverview.monitor.endDatePlaceholder')"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="changeDayRangeHandle"
          />
        </div>
        <el-button>
          {{ $t('common.export') }}
        </el-button>
      </div>

      <el-tab-pane
        :label="'Tokens ' + $t('layout.home.consume') + ' Top ' + $t('views.application.title')"
        name="tokens_agent"
      >
        <app-table
          class="mt-16"
          :data="tokensRankding"
          :pagination-config="paginationConfig"
          @sizeChange="handleSizeChange"
          @changePage="getDetail"
          :maxTableHeight="200"
          :row-key="(row: any) => row.id"
          v-loading="loading"
        >
          <el-table-column
            prop="nick_name"
            :label="$t('views.userManage.userForm.nick_name.label')"
            min-width="120"
            show-overflow-tooltip
          />
          <el-table-column
            prop="username"
            min-width="120"
            show-overflow-tooltip
            :label="$t('views.login.loginForm.username.label')"
          />
        </app-table>
      </el-tab-pane>
    </el-tabs>
  </el-drawer>
</template>
<script setup lang="ts">
import { ref, onMounted, watch, computed, reactive } from 'vue'

import useStore from '@/stores'
import { hasPermission } from '@/utils/permission/index'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
import homeApi from '@/api/home-page/home'
import { nowDate, beforeDay } from '@/utils/time'
import { t } from '@/locales'
const { user } = useStore()
const drawerVisible = ref(false)
const activeName = ref('tokens_agent')
const search_text = ref('')
const loading = ref(false)

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})
const tokensRankding = ref<any[]>([])
const questionRanking = ref<any[]>()
const userTokensRanking = ref<any[]>()

function handleClick(tab: any) {
  activeName.value = tab
  search_text.value = ''
}

const dayOptions = [
  {
    value: 7,
    label: t('views.applicationOverview.monitor.pastDayOptions.past7Days'),
  },
  {
    value: 30,
    label: t('views.applicationOverview.monitor.pastDayOptions.past30Days'),
  },
  {
    value: 90,
    label: t('views.applicationOverview.monitor.pastDayOptions.past90Days'),
  },
  {
    value: 183,
    label: t('views.applicationOverview.monitor.pastDayOptions.past183Days'),
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

function getDetail() {
  if (activeName.value === 'tokens_agent') {
    homeApi.getTokensRanking(paginationConfig, daterange.value, loading).then((res: any) => {
      paginationConfig.total = res.data?.total || 0
      tokensRankding.value = res.data?.records
    })
  } else if (activeName.value === 'questions_agent') {
    homeApi.getQuestionsRanking(paginationConfig, daterange.value, loading).then((res: any) => {
      paginationConfig.total = res.data?.total || 0
      questionRanking.value = res.data?.records
    })
  } else if (activeName.value === 'user_tokens_agent') {
    homeApi.getUserTokensRanking(paginationConfig, daterange.value, loading).then((res: any) => {
      paginationConfig.total = res.data?.total || 0
      userTokensRanking.value = res.data?.records
    })
  }
}
function handleSizeChange() {
  paginationConfig.current_page = 1
  changeDayHandle(history_day.value)
}

watch(drawerVisible, (bool) => {
  if (!bool) {
    search_text.value = ''
    activeName.value = 'tokens_agent'
    tokensRankding.value = []
    paginationConfig.current_page = 1
    paginationConfig.total = 0
  }
})

const open = (name: string) => {
  activeName.value = name
  changeDayHandle(history_day.value)
  drawerVisible.value = true
}
defineExpose({
  open,
})
</script>
<style lang="scss" scoped></style>
