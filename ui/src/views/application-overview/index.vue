<template>
  <LayoutContainer header="概览">
    <el-scrollbar>
      <div class="main-calc-height p-24">
        <h4 class="title-decoration-1 mb-16">应用信息</h4>
        <el-card shadow="never" class="overview-card" v-loading="loading">
          <div class="title flex align-center">
            <AppAvatar
              v-if="detail?.name"
              :name="detail?.name"
              pinyinColor
              class="mr-12"
              shape="square"
              :size="32"
            />
            <h4>{{ detail?.name }}</h4>
          </div>

          <el-row :gutter="12">
            <el-col :span="12" class="mt-16">
              <div class="flex">
                <el-text type="info">公开访问链接</el-text>
                <el-switch
                  v-model="accessToken.is_active"
                  class="ml-8"
                  size="small"
                  inline-prompt
                  active-text="开"
                  inactive-text="关"
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
                  <a v-if="accessToken?.is_active" :href="shareUrl" target="_blank"> 演示 </a>
                  <span v-else>演示</span>
                </el-button>
                <el-button :disabled="!accessToken?.is_active" @click="openDialog">
                  嵌入第三方
                </el-button>
                <el-button @click="openLimitDialog"> 访问限制 </el-button>
              </div>
            </el-col>
            <el-col :span="12" class="mt-16">
              <div class="flex">
                <el-text type="info">API访问凭据</el-text>
              </div>
              <div class="mt-4 mb-16 url-height">
                <span class="vertical-middle lighter break-all">
                  {{ apiUrl }}
                </span>

                <el-button type="primary" text @click="copyClick(apiUrl)">
                  <AppIcon iconName="app-copy"></AppIcon>
                </el-button>
              </div>
              <div>
                <el-button @click="openAPIKeyDialog"> API Key </el-button>
              </div>
            </el-col>
          </el-row>
        </el-card>
        <h4 class="title-decoration-1 mt-16 mb-16">监控统计</h4>
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
            start-placeholder="开始时间"
            end-placeholder="结束时间"
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
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import EmbedDialog from './component/EmbedDialog.vue'
import APIKeyDialog from './component/APIKeyDialog.vue'
import LimitDialog from './component/LimitDialog.vue'
import StatisticsCharts from './component/StatisticsCharts.vue'
import applicationApi from '@/api/application'
import overviewApi from '@/api/application-overview'
import { nowDate, beforeDay } from '@/utils/time'

import { MsgSuccess, MsgConfirm } from '@/utils/message'

import { copyClick } from '@/utils/clipboard'
import useStore from '@/stores'
const { application } = useStore()
const route = useRoute()
const {
  params: { id }
} = route as any

const apiUrl = window.location.origin + '/doc'

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
  },
  {
    value: 'other',
    label: '自定义'
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
    `是否重新生成公开访问链接?`,
    `重新生成公开访问链接会影响嵌入第三方脚本变更，需要将新脚本重新嵌入第三方，请谨慎操作！`,
    {
      confirmButtonText: '确认'
    }
  )
    .then(() => {
      const obj = {
        access_token_reset: true
      }
      const str = '刷新成功'
      updateAccessToken(obj, str)
    })
    .catch(() => {})
}
function changeState(bool: Boolean) {
  const obj = {
    is_active: bool
  }
  const str = bool ? '启用成功' : '禁用成功'
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
}
</style>
