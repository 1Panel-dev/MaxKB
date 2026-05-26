<template>
  <el-card style="--el-card-padding: 24px" class="mt-16">
    <div class="flex-between mb-16">
      <h4>{{ $t('layout.home.rank') }} TOP5</h4>
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
          :start-placeholder="$t('views.applicationOverview.monitor.startDatePlaceholder')"
          :end-placeholder="$t('views.applicationOverview.monitor.endDatePlaceholder')"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="changeDayRangeHandle"
        />
      </div>
    </div>

    <el-skeleton :loading="loading" animated>
      <el-row :gutter="16">
        <el-col :xs="12" :sm="12" :md="12" :lg="8" :xl="8" class="mb-16">
          <el-card shadow="never" style="--el-card-padding: 24px">
            <div class="flex-between">
              <h4>
                Tokens
                {{ $t('layout.home.consume') }}
                Top
                {{ $t('views.application.title') }}
              </h4>
              <el-button link class="flex align-center lighter" @click="openDrawer('tokens_agent')">
                <span class="mr-4"> {{ $t('common.detail') }}</span>
                <el-icon>
                  <ArrowRight />
                </el-icon>
              </el-button>
            </div>
            <template v-for="(item, index) in tokensRankding" :key="index">
              <div class="flex-between mt-24">
                <div class="flex align-center">
                  <span class="rank" :class="'rank-' + (index + 1)"> {{ index + 1 }}</span>
                  <div class="ml-12">
                    <p>{{ item?.name }}</p>
                    <p class="color-secondary font-small lighter">
                      {{ $t('layout.home.chat') }} {{ numberFormat(item?.chat_record_count || 0) }}
                      {{ $t('views.system.time') }} <el-divider direction="vertical" />{{
                        $t('layout.home.average‌')
                      }}
                      {{ numberFormat(item?.total_tokens / item?.chat_record_count || 0) }} tokens
                    </p>
                  </div>
                </div>
                <div class="text-right" style="width: 100px">
                  <el-progress :percentage="0" :show-text="false" />
                  <p class="color-secondary mt-4">{{ numberFormat(item?.total_tokens || 0) }}</p>
                </div>
              </div>
            </template>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="12" :md="12" :lg="8" :xl="8" class="mb-16">
          <el-card shadow="never" style="--el-card-padding: 24px">
            <div class="flex-between">
              <h4>
                {{ $t('views.applicationOverview.monitor.charts.queryCount') }}
                Top
                {{ $t('views.application.title') }}
              </h4>
              <el-button
                link
                class="flex align-center lighter"
                @click="openDrawer('questions_agent')"
              >
                <span class="mr-4"> {{ $t('common.detail') }}</span>
                <el-icon>
                  <ArrowRight />
                </el-icon>
              </el-button>
            </div>
            <template v-for="(item, index) in questionRanking" :key="index">
              <div class="flex-between mt-24">
                <div class="flex align-center">
                  <span class="rank" :class="'rank-' + (index + 1)"> {{ index + 1 }}</span>
                  <div class="ml-12">
                    <p>{{ item?.name }}</p>
                    <p class="color-secondary font-small lighter">
                      {{ $t('layout.home.activeUsers') }}
                      {{ numberFormat(item?.chat_user_count || 0) }}
                      <el-divider direction="vertical" />{{ $t('layout.home.average‌') }}
                      {{
                        item?.chat_record_count / item?.chat_user_count > 1
                          ? numberFormat(item?.chat_record_count / item?.chat_user_count || 0)
                          : (item?.chat_record_count / item?.chat_user_count).toFixed(1)
                      }}
                      {{ $t('layout.home.wheel') }}/{{ $t('layout.home.person') }}
                    </p>
                  </div>
                </div>
                <div class="text-right" style="width: 100px">
                  <el-progress :percentage="0" :show-text="false" />
                  <p class="color-secondary mt-4">
                    {{ numberFormat(item?.chat_record_count || 0) }}
                  </p>
                </div>
              </div>
            </template>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="12" :md="12" :lg="8" :xl="8" class="mb-16">
          <el-card shadow="never" style="--el-card-padding: 24px">
            <div class="flex-between">
              <h4>
                Tokens
                {{ $t('layout.home.consume') }}
                Top
                {{ $t('views.chatLog.table.user') }}
              </h4>
              <el-button
                link
                class="flex align-center lighter"
                @click="openDrawer('user_tokens_agent')"
              >
                <span class="mr-4"> {{ $t('common.detail') }}</span>
                <el-icon>
                  <ArrowRight />
                </el-icon>
              </el-button>
            </div>
            <template v-for="(item, index) in userTokensRanking" :key="index">
              <div class="flex-between mt-24">
                <div class="flex align-center">
                  <span class="rank" :class="'rank-' + (index + 1)"> {{ index + 1 }}</span>
                  <div class="ml-12">
                    <p>{{ item?.asker?.username }}</p>
                    <p class="color-secondary font-small lighter">
                      {{ $t('layout.home.questions') }}
                      {{ numberFormat(item?.chat_record_count || 0) }}
                      {{ $t('views.system.time') }}
                      <el-divider direction="vertical" />
                      {{ '-' }}
                    </p>
                  </div>
                </div>
                <div class="text-right" style="width: 100px">
                  <el-progress :percentage="0" :show-text="false" />
                  <p class="color-secondary mt-4">
                    {{ numberFormat(item?.chat_record_count || 0) }}
                  </p>
                </div>
              </div>
            </template>
          </el-card>
        </el-col>
      </el-row>
    </el-skeleton>
    <RankingDrawer ref="RankingDrawerRef" />
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import RankingDrawer from './RankingDrawer.vue'
import homeApi from '@/api/home-page/home'
import { nowDate, beforeDay } from '@/utils/time'
import { numberFormat } from '@/utils/common'
import { t } from '@/locales'
const loading = ref(true)
const tokensRankding = ref<any[]>([])
const questionRanking = ref<any[]>()
const userTokensRanking = ref<any[]>()
const paginationConfig = reactive({
  current_page: 1,
  page_size: 5,
  total: 0,
})

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
  homeApi.getTokensRanking(paginationConfig, daterange.value, loading).then((res: any) => {
    tokensRankding.value = res.data?.records
  })
  homeApi.getQuestionsRanking(paginationConfig, daterange.value, loading).then((res: any) => {
    questionRanking.value = res.data?.records
  })
  homeApi.getUserTokensRanking(paginationConfig, daterange.value, loading).then((res: any) => {
    userTokensRanking.value = res.data?.records
  })
}

const RankingDrawerRef = ref()
const openDrawer = (name: string) => {
  RankingDrawerRef.value.open(name)
}
onMounted(() => {
  changeDayHandle(history_day.value)
})
</script>
<style lang="scss" scoped></style>
