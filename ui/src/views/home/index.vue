<template>
  <div class="home p-16">
    <el-scrollbar>
      <div class="home-calc-height p-8 pt-0">
        <el-card style="--el-card-padding: 24px">
          <h4 class="mb-16">
            {{ $t('layout.home.quickCreate') }}
          </h4>
          <QuickCreate />
        </el-card>

        <el-card style="--el-card-padding: 24px" class="mt-16">
          <h4 class="mb-16">
            {{ $t('layout.home.resource') }}
          </h4>
          <ResourceAggregation />
        </el-card>

        <el-card style="--el-card-padding: 24px" class="mt-16">
          <h4 class="mb-16">
            {{ $t('views.applicationOverview.monitor.monitoringStatistics') }}
          </h4>
          <div class="mb-16">
            <el-select v-model="history_day" class="mr-12 w-180" @change="changeDayHandle">
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
          <div v-loading="statisticsLoading">
            <StatisticsCharts
              :data="statisticsData"
              :token-usage="tokenUsage"
              :top-questions="topQuestions"
            />
          </div>
        </el-card>
        <el-card style="--el-card-padding: 24px" class="mt-16">
          <h4 class="mb-16">{{ $t('layout.home.rank') }} TOP5</h4>
          <Ranking />
        </el-card>
        <br />
      </div>
    </el-scrollbar>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, shallowRef, nextTick } from 'vue'
import { useRoute } from 'vue-router'

import StatisticsCharts from '@/views/application-overview/component/StatisticsCharts.vue'
import QuickCreate from './component/QuickCreate.vue'
import ResourceAggregation from './component/ResourceAggregation.vue'
import Ranking from './component/Ranking.vue'
import { nowDate, beforeDay } from '@/utils/time'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

const route = useRoute()
const {
  params: { id },
} = route as any

const detail = ref<any>(null)

const loading = ref(false)

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

const statisticsLoading = ref(false)
const statisticsData = ref([])
const tokenUsage = ref([])
const topQuestions = ref([])

const apiInputParams = ref([])

function getDetail() {
  loadSharedApi({ type: 'application', systemType: apiType.value })
    .getApplicationDetail(id, loading)
    .then((res: any) => {
      detail.value = res.data
      detail.value.work_flow?.nodes
        ?.filter((v: any) => v.id === 'base-node')
        .map((v: any) => {
          apiInputParams.value = v.properties.api_input_field_list
            ? v.properties.api_input_field_list.map((v: any) => {
                return {
                  name: v.variable,
                  value: v.default_value,
                }
              })
            : v.properties.input_field_list
              ? v.properties.input_field_list
                  .filter((v: any) => v.assignment_method === 'api_input')
                  .map((v: any) => {
                    return {
                      name: v.variable,
                      value: v.default_value,
                    }
                  })
              : []
        })
    })
}

onMounted(() => {
  // getDetail()
  // changeDayHandle(history_day.value)
})
</script>
<style lang="scss" scoped>
.home {
  max-width: 1280px;
  margin: 0 auto;
  .home-calc-height {
    height: calc(var(--app-main-height) + 52px);
    box-sizing: border-box;
  }
}
</style>
