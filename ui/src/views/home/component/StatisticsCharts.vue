<template>
  <el-card style="--el-card-padding: 24px" class="mt-16">
    <div class="flex-between mb-16">
      <h4 class="mb-16">
        {{ $t('home.monitoringStatistics') }}
      </h4>
      <div>
        <el-select v-model="history_day" class="w-180" @change="changeDayHandle">
          <el-option
            v-for="item in dayOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-date-picker
          class="ml-12"
          v-if="history_day === 'other'"
          v-model="daterangeValue"
          type="daterange"
          :start-placeholder="$t('home.startDatePlaceholder')"
          :end-placeholder="$t('home.endDatePlaceholder')"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="changeDayRangeHandle"
        />
        <el-select
          class="ml-12"
          v-model="application_id"
          @change="changeAgent"
          filterable
          remote
          :remote-method="getAgentList"
          style="width: 220px"
          :value-on-clear:="'all'"
          popper-class="max-w-350"
        >
          <el-option :label="$t('home.allAgents')" :value="'all'">
            <el-space :size="8">
              <el-avatar shape="square" :size="24" style="background: none">
                <AppIcon :iconName="'app-all-menu'" class="color-secondary"></AppIcon>
              </el-avatar>
              <span>{{ $t('home.allAgents') }}</span>
            </el-space>
          </el-option>
          <el-option v-for="u in agentOptions" :key="u.id" :value="u.id" :label="u.name">
            <el-space :size="8">
              <el-avatar shape="square" :size="24" style="background: none">
                <img :src="resetUrl(u?.icon, resetUrl('./favicon.ico'))" alt="" />
              </el-avatar>
              <span class="ellipsis" :title="u.name">{{ u.name }}</span>
            </el-space>
          </el-option>
          <template #label="{ label, value }">
            <el-space :size="8">
              <el-avatar shape="square" :size="20" style="background: none">
                <AppIcon
                  v-if="value === 'all'"
                  :iconName="'app-all-menu'"
                  class="color-text-primary"
                ></AppIcon>
                <img
                  v-else
                  :src="
                    resetUrl(
                      relatedObject(agentOptions, value, 'id')?.icon,
                      resetUrl('./favicon.ico'),
                    )
                  "
                  alt=""
                />
              </el-avatar>
              <span class="ellipsis" :title="label">{{ label }}</span>
            </el-space>
          </template>
        </el-select>
      </div>
    </div>
    <el-skeleton :loading="loading" animated>
      <el-row :gutter="16">
        <el-col
          :xs="12"
          :sm="12"
          :md="12"
          :lg="6"
          :xl="6"
          v-for="(item, index) in statisticsType"
          :key="index"
          class="mb-16"
        >
          <el-card shadow="never">
            <div class="flex align-center ml-8 mr-8">
              <!-- <el-avatar :size="40" shape="square" :style="{ background: item.background }">
                <appIcon :iconName="item.icon" :style="{ fontSize: '24px', color: item.color }" />
              </el-avatar> -->
              <div>
                <p class="color-secondary lighter mb-4">{{ item.name }}</p>
                <div v-if="item.id !== 'starCharts'" class="flex align-baseline">
                  <h2>{{ numberFormat(item.sum?.[0]) }}</h2>
                  <span v-if="item.sum.length > 1" class="ml-12" style="color: #f54a45"
                    >+{{ numberFormat(item.sum?.[1]) }}</span
                  >
                </div>
                <div v-else class="flex align-center mr-8">
                  <AppIcon iconName="app-like-color"></AppIcon>
                  <h2 class="ml-4">{{ item.sum?.[0] }}</h2>
                  <AppIcon class="ml-12" iconName="app-oppose-color"></AppIcon>
                  <h2 class="ml-4">{{ item.sum?.[1] }}</h2>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col
          :xs="24"
          :sm="24"
          :md="24"
          :lg="12"
          :xl="12"
          v-for="(item, index) in statisticsType"
          :key="index"
          class="mb-16"
        >
          <el-card shadow="never">
            <div class="p-8">
              <AppCharts
                v-if="data.length"
                height="316px"
                :id="item.id"
                type="line"
                :option="item.option"
              />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-skeleton>
  </el-card>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppCharts from '@/components/app-charts/index.vue'
import { relatedObject } from '@/utils/array'
import homeApi from '@/api/home-page/home'
import { nowDate, beforeDay } from '@/utils/time'
import { getAttrsArray, getSum } from '@/utils/array'
import { numberFormat } from '@/utils/common'
import ApplicationApi from '@/api/application/application'
import { resetUrl } from '@/utils/common'
import { t } from '@/locales'

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

const data = ref<any>([])
const loading = ref(false)
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

const statisticsType = computed(() => [
  {
    id: 'customerCharts',
    name: t('home.activeUsers'),
    icon: 'app-user',
    background: '#EBF1FF',
    color: '#3370FF',
    sum: [
      getSum(getAttrsArray(data.value, 'customer_num') || 0),
      getSum(getAttrsArray(data.value, 'customer_added_count') || 0),
    ],
    option: {
      title: t('home.activeUsers'),
      xData: getAttrsArray(data.value, 'day'),
      yData: [
        {
          name: t('home.activeUsers'),
          area: true,
          data: getAttrsArray(data.value, 'customer_num'),
        },
        {
          name: t('home.newUsers'),
          area: true,
          data: getAttrsArray(data.value, 'customer_added_count'),
        },
      ],
    },
  },
  {
    id: 'chatRecordCharts',
    name: t('home.chatCount'),
    icon: 'app-question',
    background: '#FFF3E5',
    color: '#FF8800',
    sum: [getSum(getAttrsArray(data.value, 'chat_record_count') || 0)],
    option: {
      title: t('home.chatCount'),
      xData: getAttrsArray(data.value, 'day'),
      yData: [
        {
          data: getAttrsArray(data.value, 'chat_record_count'),
          area: true,
        },
      ],
    },
  },
  {
    id: 'tokensCharts',
    name: t('home.charts.tokensTotal'),
    icon: 'app-tokens',
    background: '#E5FBF8',
    color: '#00D6B9',
    sum: [getSum(getAttrsArray(data.value, 'tokens_num') || 0)],
    option: {
      title: t('home.charts.tokensTotal'),
      xData: getAttrsArray(data.value, 'day'),
      yData: [
        {
          data: getAttrsArray(data.value, 'tokens_num'),
          area: true,
        },
      ],
    },
  },
  {
    id: 'starCharts',
    name: t('home.charts.userSatisfaction'),
    icon: 'app-user-stars',
    background: '#FEEDEC',
    color: '#F54A45',
    sum: [
      getSum(getAttrsArray(data.value, 'star_num') || 0),
      getSum(getAttrsArray(data.value, 'trample_num') || 0),
    ],
    option: {
      title: t('home.charts.userSatisfaction'),
      xData: getAttrsArray(data.value, 'day'),
      yData: [
        {
          name: t('home.charts.approval'),
          data: getAttrsArray(data.value, 'star_num'),
          area: true,
        },
        {
          name: t('home.charts.disapproval'),
          data: getAttrsArray(data.value, 'trample_num'),
          area: true,
        },
      ],
    },
  },
])

const application_id = ref('all')
const agentOptions = ref<any[]>([])

function getAgentList(query: string) {
  const pagination = {
    current_page: 1,
    page_size: 200,
  }
  ApplicationApi.getApplication(pagination, { name: query }).then((res) => {
    agentOptions.value = res.data.records
  })
}

function changeAgent(val: string) {
  application_id.value = val
  getDetail()
}

function getDetail() {
  homeApi
    .getMonitorAggregation(
      {
        ...daterange.value,
        ...(application_id.value !== 'all' ? { application_id: application_id.value } : {}),
      },
      loading,
    )
    .then((res: any) => {
      data.value = res.data
    })
}

onMounted(() => {
  changeDayHandle(history_day.value)
  getAgentList('')
})
</script>
<style lang="scss" scoped></style>
