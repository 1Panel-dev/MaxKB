<template>
  <LayoutContainer :header="$t('views.applicationOverview.title')">
    <el-scrollbar>
      <div class="main-calc-height p-24">
        <h4 class="title-decoration-1 mb-16">
          {{ $t('views.applicationOverview.appInfo.header') }}
        </h4>
        <el-card shadow="never" class="overview-card" v-loading="loading">
          <div class="title flex align-center">
            <div
              class="edit-avatar mr-12"
              @mouseenter="showEditIcon = true"
              @mouseleave="showEditIcon = false"
            >
              <AppAvatar
                v-if="isAppIcon(detail?.icon)"
                shape="square"
                :size="32"
                style="background: none"
              >
                <img :src="detail?.icon" alt="" />
              </AppAvatar>
              <AppAvatar
                v-else-if="detail?.name"
                :name="detail?.name"
                pinyinColor
                shape="square"
                :size="32"
              />
              <AppAvatar
                v-if="showEditIcon"
                shape="square"
                class="edit-mask"
                :size="32"
                @click="openEditAvatar"
              >
                <el-icon><EditPen /></el-icon>
              </AppAvatar>
            </div>

            <h4>{{ detail?.name }}</h4>
          </div>

          <el-row :gutter="12">
            <el-col :span="12" class="mt-16">
              <div class="flex">
                <el-text type="info">{{
                  $t('views.applicationOverview.appInfo.publicAccessLink')
                }}</el-text>
                <el-switch
                  v-model="accessToken.is_active"
                  class="ml-8"
                  size="small"
                  inline-prompt
                  :active-text="$t('views.applicationOverview.appInfo.openText')"
                  :inactive-text="$t('views.applicationOverview.appInfo.closeText')"
                  @change="changeState($event)"
                />
              </div>

              <div class="mt-4 mb-16 url-height">
                <span class="vertical-middle lighter break-all">
                  {{ shareUrl }}
                </span>

                <el-button type="primary" text @click="copyClick(shareUrl)">
                  <AppIcon iconName="app-copy"></AppIcon>
                </el-button>
                <el-button @click="refreshAccessToken" type="primary" text style="margin-left: 1px">
                  <el-icon><RefreshRight /></el-icon>
                </el-button>
              </div>
              <div>
                <el-button :disabled="!accessToken?.is_active" type="primary">
                  <a v-if="accessToken?.is_active" :href="shareUrl" target="_blank">
                    {{ $t('views.applicationOverview.appInfo.demo') }}
                  </a>
                  <span v-else> {{ $t('views.applicationOverview.appInfo.demo') }}</span>
                </el-button>
                <el-button :disabled="!accessToken?.is_active" @click="openDialog">
                  {{ $t('views.applicationOverview.appInfo.embedThirdParty') }}
                </el-button>
                <el-button @click="openLimitDialog">
                  {{ $t('views.applicationOverview.appInfo.accessRestrictions') }}
                </el-button>
                <el-button @click="openDisplaySettingDialog">
                  {{ $t('views.applicationOverview.appInfo.displaySetting') }}
                </el-button>
              </div>
            </el-col>
            <el-col :span="12" class="mt-16">
              <div class="flex">
                <el-text type="info"
                  >{{ $t('views.applicationOverview.appInfo.apiAccessCredentials') }}
                </el-text>
              </div>
              <div class="mt-4 mb-16 url-height">
                <a target="_blank" :href="apiUrl" class="vertical-middle lighter break-all">
                  {{ apiUrl }}
                </a>

                <el-button type="primary" text @click="copyClick(apiUrl)">
                  <AppIcon iconName="app-copy"></AppIcon>
                </el-button>
              </div>
              <div>
                <el-button @click="openAPIKeyDialog">{{
                  $t('views.applicationOverview.appInfo.apiKey')
                }}</el-button>
              </div>
            </el-col>
          </el-row>
        </el-card>
        <h4 class="title-decoration-1 mt-16 mb-16">
          {{ $t('views.applicationOverview.monitor.monitoringStatistics') }}
        </h4>
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
        </div>
        <div v-loading="statisticsLoading">
          <StatisticsCharts :data="statisticsData" />
        </div>
      </div>
    </el-scrollbar>
    <EmbedDialog ref="EmbedDialogRef" />
    <APIKeyDialog ref="APIKeyDialogRef" />
    <LimitDialog ref="LimitDialogRef" @refresh="refresh" />
    <EditAvatarDialog ref="EditAvatarDialogRef" @refresh="refreshIcon" />
    <DisplaySettingDialog ref="DisplaySettingDialogRef" @refresh="refresh" />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import EmbedDialog from './component/EmbedDialog.vue'
import APIKeyDialog from './component/APIKeyDialog.vue'
import LimitDialog from './component/LimitDialog.vue'
import DisplaySettingDialog from './component/DisplaySettingDialog.vue'

import EditAvatarDialog from './component/EditAvatarDialog.vue'
import StatisticsCharts from './component/StatisticsCharts.vue'
import applicationApi from '@/api/application'
import overviewApi from '@/api/application-overview'
import { nowDate, beforeDay } from '@/utils/time'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { copyClick } from '@/utils/clipboard'
import { isAppIcon } from '@/utils/application'
import useStore from '@/stores'
import { t } from '@/locales'
const { application } = useStore()
const route = useRoute()
const {
  params: { id }
} = route as any

const apiUrl = window.location.origin + '/doc/chat/'

const DisplaySettingDialogRef = ref()
const EditAvatarDialogRef = ref()
const LimitDialogRef = ref()
const APIKeyDialogRef = ref()
const EmbedDialogRef = ref()

const accessToken = ref<any>({})
const detail = ref<any>(null)

const loading = ref(false)

const shareUrl = computed(() => application.location + accessToken.value.access_token)

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

const history_day = ref<number | string>(7)

// 日期组件时间
const daterangeValue = ref('')

// 提交日期时间
const daterange = ref({
  start_time: '',
  end_time: ''
})

const statisticsLoading = ref(false)
const statisticsData = ref([])

const showEditIcon = ref(false)

function openDisplaySettingDialog() {
  DisplaySettingDialogRef.value.open(accessToken.value)
}
function openEditAvatar() {
  EditAvatarDialogRef.value.open(detail.value)
}

function changeDayHandle(val: number | string) {
  if (val !== 'other') {
    daterange.value.start_time = beforeDay(val)
    daterange.value.end_time = nowDate
    getAppStatistics()
  }
}

function changeDayRangeHandle(val: string) {
  daterange.value.start_time = val[0]
  daterange.value.end_time = val[1]
  getAppStatistics()
}

function getAppStatistics() {
  overviewApi.getStatistics(id, daterange.value, statisticsLoading).then((res: any) => {
    statisticsData.value = res.data
  })
}

function refreshAccessToken() {
  MsgConfirm(
    t('views.applicationOverview.appInfo.refreshToken.msgConfirm1'),
    t('views.applicationOverview.appInfo.refreshToken.msgConfirm2'),
    {
      confirmButtonText: t('views.applicationOverview.appInfo.refreshToken.confirm'),
      cancelButtonText: t('views.applicationOverview.appInfo.refreshToken.cancel')
    }
  )
    .then(() => {
      const obj = {
        access_token_reset: true
      }
      // @ts-ignore
      const str = t('views.applicationOverview.appInfo.refreshToken.refreshSuccess')
      updateAccessToken(obj, str)
    })
    .catch(() => {})
}
function changeState(bool: Boolean) {
  const obj = {
    is_active: bool
  }
  const str = bool
    ? t('views.applicationOverview.appInfo.changeState.enableSuccess')
    : t('views.applicationOverview.appInfo.changeState.disableSuccess')
  updateAccessToken(obj, str)
}

function updateAccessToken(obj: any, str: string) {
  applicationApi.putAccessToken(id as string, obj, loading).then((res) => {
    accessToken.value = res?.data
    MsgSuccess(str)
  })
}

function openLimitDialog() {
  LimitDialogRef.value.open(accessToken.value)
}

function openAPIKeyDialog() {
  APIKeyDialogRef.value.open()
}
function openDialog() {
  EmbedDialogRef.value.open(accessToken.value?.access_token)
}
function getAccessToken() {
  application.asyncGetAccessToken(id, loading).then((res: any) => {
    accessToken.value = res?.data
  })
}

function getDetail() {
  application.asyncGetApplicationDetail(id, loading).then((res: any) => {
    detail.value = res.data
  })
}

function refresh() {
  getAccessToken()
}

function refreshIcon() {
  getDetail()
}

onMounted(() => {
  getDetail()
  getAccessToken()
  changeDayHandle(history_day.value)
})
</script>
<style lang="scss" scoped>
.overview-card {
  position: relative;
  .active-button {
    position: absolute;
    right: 16px;
    top: 21px;
  }

  .edit-avatar {
    position: relative;
    .edit-mask {
      position: absolute;
      left: 0;
      background: rgba(0, 0, 0, 0.4);
    }
  }
}
</style>
