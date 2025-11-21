<template>
  <div class="p-16-24">
    <h2 class="mb-16">{{ $t('views.applicationOverview.title') }}</h2>
    <el-scrollbar>
      <div class="main-calc-height">
        <el-card style="--el-card-padding: 24px">
          <h4 class="title-decoration-1 mb-16">
            {{ $t('views.applicationOverview.appInfo.header') }}
          </h4>
          <el-card shadow="never" class="overview-card" v-loading="loading">
            <div class="title flex align-center">
              <div class="edit-avatar mr-12">
                <el-avatar shape="square" :size="32" style="background: none">
                  <img :src="resetUrl(detail?.icon, resetUrl('./favicon.ico'))" alt=""/>
                </el-avatar>
              </div>

              <h4>{{ detail?.name || '-' }}</h4>
            </div>

            <el-row :gutter="12">
              <el-col :span="12" class="mt-16">
                <div class="flex">
                  <el-text type="info"
                  >{{ $t('views.applicationOverview.appInfo.publicAccessLink') }}
                  </el-text>
                  <el-switch
                    v-model="accessToken.is_active"
                    class="ml-8"
                    size="small"
                    inline-prompt
                    :active-text="$t('views.applicationOverview.appInfo.openText')"
                    :inactive-text="$t('views.applicationOverview.appInfo.closeText')"
                    :before-change="() => changeState(accessToken.is_active)"
                  />
                </div>

                <div class="mt-4 mb-16 url-height flex align-center" style="margin-bottom: 37px">
                  <span class="vertical-middle lighter break-all ellipsis-1">
                    {{ shareUrl }}
                  </span>
                  <el-tooltip effect="dark" :content="$t('common.copy')" placement="top">
                    <el-button type="primary" text @click="copyClick(shareUrl)">
                      <AppIcon iconName="app-copy"></AppIcon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip effect="dark" :content="$t('common.refresh')" placement="top">
                    <el-button
                      @click="refreshAccessToken"
                      type="primary"
                      text
                      style="margin-left: 1px"
                    >
                      <el-icon>
                        <RefreshRight/>
                      </el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
                <div>
                  <el-button
                    v-if="accessToken?.is_active"
                    :disabled="!accessToken?.is_active"
                    tag="a"
                    :href="shareUrl"
                    target="_blank"
                  >
                    <AppIcon iconName="app-create-chat" class="mr-4"></AppIcon>
                    {{ $t('views.application.operation.toChat') }}
                  </el-button>
                  <el-button v-else :disabled="!accessToken?.is_active">
                    <AppIcon iconName="app-create-chat" class="mr-4"></AppIcon>
                    {{ $t('views.application.operation.toChat') }}
                  </el-button>
                  <el-button
                    :disabled="!accessToken?.is_active"
                    @click="openDialog"
                    v-if="permissionPrecise.overview_embed(id)"
                  >
                    <AppIcon iconName="app-export" class="mr-4"></AppIcon>
                    {{ $t('views.applicationOverview.appInfo.embedInWebsite') }}
                  </el-button>
                  <!-- 访问限制 -->
                  <el-button @click="openLimitDialog" v-if="permissionPrecise.overview_access(id)">
                    <AppIcon iconName="app-lock" class="mr-4"></AppIcon>
                    {{ $t('views.applicationOverview.appInfo.accessControl') }}
                  </el-button>
                  <!-- 显示设置 -->
                  <el-button
                    @click="openDisplaySettingDialog"
                    v-if="permissionPrecise.overview_display(id)"
                  >
                    <AppIcon iconName="app-setting" class="mr-4"></AppIcon>
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
                  <div>
                    <el-text>API {{ $t('common.fileUpload.document') }}：</el-text>
                    <el-button
                      type="primary"
                      link
                      @click="toUrl(apiUrl)"
                      class="vertical-middle lighter break-all"
                    >
                      {{ apiUrl }}
                    </el-button>
                  </div>
                  <div class="flex align-center">
                    <span class="flex">
                      <el-text style="width: 80px">Base URL：</el-text>
                    </span>

                    <span class="vertical-middle lighter break-all ellipsis-1">{{
                        baseUrl + id
                      }}</span>
                    <el-tooltip effect="dark" :content="$t('common.copy')" placement="top">
                      <el-button type="primary" text @click="copyClick(baseUrl + id)">
                        <AppIcon iconName="app-copy"></AppIcon>
                      </el-button>
                    </el-tooltip>
                  </div>
                </div>
                <div>
                  <el-button
                    @click="openAPIKeyDialog"
                    v-if="permissionPrecise.overview_api_key(id)"
                  >
                    <el-icon class="mr-4">
                      <Key/>
                    </el-icon>
                    {{ $t('views.applicationOverview.appInfo.apiKey') }}
                  </el-button>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </el-card>
        <el-card style="--el-card-padding: 24px" class="mt-16">
          <h4 class="title-decoration-1 mb-16">
            {{ $t('views.applicationOverview.monitor.monitoringStatistics') }}
          </h4>
          <div class="mb-16">
            <el-select
              v-model="history_day"
              class="mr-12"
              @change="changeDayHandle"
              style="width: 180px"
            >
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
            <StatisticsCharts :data="statisticsData" :token-usage="tokenUsage"
                              :top-questions="topQuestions"/>
          </div>
        </el-card>
      </div>
    </el-scrollbar>

    <EmbedDialog
      ref="EmbedDialogRef"
      :data="detail"
      :api-input-params="mapToUrlParams(apiInputParams)"
    />
    <APIKeyDialog ref="APIKeyDialogRef"/>

    <!-- 社区版访问限制 -->
    <component :is="currentLimitDialog" ref="LimitDialogRef" @refresh="refresh"/>
    <!-- 显示设置 -->
    <component :is="currentDisplaySettingDialog" ref="DisplaySettingDialogRef" @refresh="refresh"/>
  </div>
</template>
<script setup lang="ts">
import {ref, computed, onMounted, shallowRef, nextTick} from 'vue'
import {useRoute} from 'vue-router'
import EmbedDialog from './component/EmbedDialog.vue'
import APIKeyDialog from './component/APIKeyDialog.vue'
import LimitDialog from './component/LimitDialog.vue'
import XPackLimitDrawer from './xpack-component/XPackLimitDrawer.vue'
import DisplaySettingDialog from './component/DisplaySettingDialog.vue'
import XPackDisplaySettingDialog from './xpack-component/XPackDisplaySettingDialog.vue'
import StatisticsCharts from './component/StatisticsCharts.vue'
import {nowDate, beforeDay} from '@/utils/time'
import {MsgSuccess, MsgConfirm} from '@/utils/message'
import {copyClick} from '@/utils/clipboard'
import {resetUrl} from '@/utils/common'
import {mapToUrlParams} from '@/utils/application'
import {t} from '@/locales'
import {EditionConst} from '@/utils/permission/data'
import {hasPermission} from '@/utils/permission/index'
import permissionMap from '@/permission'
import {loadSharedApi} from '@/utils/dynamics-api/shared-api'

const route = useRoute()
const {
  params: {id},
} = route as any

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const permissionPrecise = computed(() => {
  return permissionMap['application'][apiType.value]
})

const apiUrl = window.location.origin + `${window.MaxKB.chatPrefix}/api-doc/`

const baseUrl = window.location.origin + `${window.MaxKB.chatPrefix}/api/`

const APIKeyDialogRef = ref()
const EmbedDialogRef = ref()

const accessToken = ref<any>({})
const detail = ref<any>(null)

const loading = ref(false)

const urlParams = computed(() =>
  mapToUrlParams(apiInputParams.value) ? '?' + mapToUrlParams(apiInputParams.value) : '',
)
const shareUrl = computed(
  () =>
    `${window.location.origin}${window.MaxKB.chatPrefix}/` +
    accessToken.value?.access_token +
    urlParams.value,
)

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

const statisticsLoading = ref(false)
const statisticsData = ref([])
const tokenUsage = ref([])
const topQuestions = ref([])

const apiInputParams = ref([])

function toUrl(url: string) {
  window.open(url, '_blank')
}

// 显示设置
const DisplaySettingDialogRef = ref()
const currentDisplaySettingDialog = shallowRef<any>(null)

function openDisplaySettingDialog() {
  // 企业版和专业版
  if (hasPermission([EditionConst.IS_EE, EditionConst.IS_PE], 'OR')) {
    currentDisplaySettingDialog.value = XPackDisplaySettingDialog
  } else {
    // 社区版
    currentDisplaySettingDialog.value = DisplaySettingDialog
  }
  nextTick(() => {
    if (currentDisplaySettingDialog.value == XPackDisplaySettingDialog) {
      loadSharedApi({type: 'application', systemType: apiType.value})
        .getApplicationSetting(id)
        .then((ok: any) => {
          DisplaySettingDialogRef.value?.open(ok.data, detail.value)
        })
    } else {
      DisplaySettingDialogRef.value?.open(accessToken.value, detail.value)
    }
  })
}

// 访问限制
const LimitDialogRef = ref()
const currentLimitDialog = shallowRef<any>(null)

function openLimitDialog() {
  // 企业版和专业版
  if (hasPermission([EditionConst.IS_EE, EditionConst.IS_PE], 'OR')) {
    currentLimitDialog.value = XPackLimitDrawer
  } else {
    // 社区版
    currentLimitDialog.value = LimitDialog
  }
  nextTick(() => {
    LimitDialogRef.value.open(accessToken.value)
  })
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
  loadSharedApi({type: 'application', systemType: apiType.value})
    .getStatistics(id, daterange.value, statisticsLoading)
    .then((res: any) => {
      statisticsData.value = res.data
    })
  loadSharedApi({type: 'application', systemType: apiType.value})
    .getTokenUsage(id, daterange.value, statisticsLoading)
    .then((res: any) => {
      // [{'token_usage': 200, 'username': '张三'}, ...]
      tokenUsage.value = res.data
    })
  loadSharedApi({type: 'application', systemType: apiType.value})
    .topQuestions(id, daterange.value, statisticsLoading)
    .then((res: any) => {
      // [{'chat_record_count': 200, 'username': '张三'}, ...]
      topQuestions.value = res.data
    })
}

function refreshAccessToken() {
  MsgConfirm(
    t('views.applicationOverview.appInfo.refreshToken.msgConfirm1'),
    t('views.applicationOverview.appInfo.refreshToken.msgConfirm2'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
    },
  )
    .then(() => {
      const obj = {
        access_token_reset: true,
      }
      const str = t('views.applicationOverview.appInfo.refreshToken.refreshSuccess')
      updateAccessToken(obj, str)
    })
    .catch(() => {
    })
}

async function changeState(bool: boolean) {
  const obj = {
    is_active: !bool,
  }
  const str = obj.is_active ? t('common.status.enableSuccess') : t('common.status.disableSuccess')
  await updateAccessToken(obj, str)
    .then(() => {
      return true
    })
    .catch(() => {
      return false
    })
}

async function updateAccessToken(obj: any, str: string) {
  loadSharedApi({type: 'application', systemType: apiType.value})
    .putAccessToken(id as string, obj, loading)
    .then((res: any) => {
      accessToken.value = res?.data
      MsgSuccess(str)
    })
}

function openAPIKeyDialog() {
  APIKeyDialogRef.value.open()
}

function openDialog() {
  EmbedDialogRef.value.open(accessToken.value?.access_token)
}

function getAccessToken() {
  loadSharedApi({type: 'application', systemType: apiType.value})
    .getAccessToken(id, loading)
    .then((res: any) => {
      accessToken.value = res?.data
    })
}

function getDetail() {
  loadSharedApi({type: 'application', systemType: apiType.value})
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
