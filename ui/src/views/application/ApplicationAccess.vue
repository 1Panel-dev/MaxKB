<template>
  <div class="p-16-24">
    <h4 class="mb-16">{{ $t('views.application.applicationAccess.title') }}</h4>

    <el-row :gutter="16">
      <el-col
        :xs="24"
        :sm="24"
        :md="12"
        :lg="12"
        :xl="12"
        class="mb-16"
        v-for="(item, index) in platforms"
        :key="index"
      >
        <el-card shadow="never" class="border-none cursor">
          <div class="flex-between">
            <div class="flex align-center ml-8 mr-8">
              <img :src="item.logoSrc" alt="" class="icon" />
              <div class="ml-12">
                <h5 class="mb-4">{{ item.name }}</h5>
                <el-text type="info" class="font-small">{{ item.description }}</el-text>
              </div>
            </div>
            <div>
              <el-switch
                size="small"
                v-model="item.isActive"
                @change="changeStatus(item.key, item.isActive)"
                :disabled="!item.exists"
                v-if="permissionPrecise.access_edit(id)"
              />
              <el-divider direction="vertical" />
              <el-button
                class="mr-4"
                @click="openDrawer(item.key)"
                v-if="permissionPrecise.access_edit(id)"
                >{{ $t('views.application.applicationAccess.setting') }}</el-button
              >
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <AccessSettingDrawer ref="AccessSettingDrawerRef" @refresh="refresh" />
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import AccessSettingDrawer from './component/AccessSettingDrawer.vue'
import { MsgSuccess } from '@/utils/message'
import { useRoute } from 'vue-router'
import { t } from '@/locales'
import permissionMap from '@/permission'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
const route = useRoute()

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

// 平台数据
const platforms = reactive([
  {
    key: 'wecomBot',
    logoSrc: new URL(`../../assets/logo/logo_wechat-bot.svg`, import.meta.url).href,
    name: t('views.application.applicationAccess.wecomBot'),
    description: t('views.application.applicationAccess.wecomBotTip'),
    isActive: false,
    exists: false,
  },
  {
    key: 'wecom',
    logoSrc: new URL(`../../assets/logo/logo_wechat-work.svg`, import.meta.url).href,
    name: t('views.application.applicationAccess.wecom'),
    description: t('views.application.applicationAccess.wecomTip'),
    isActive: false,
    exists: false,
  },
  {
    key: 'dingtalk',
    logoSrc: new URL(`../../assets/logo/logo_dingtalk.svg`, import.meta.url).href,
    name: t('views.application.applicationAccess.dingtalk'),
    description: t('views.application.applicationAccess.dingtalkTip'),
    isActive: false,
    exists: false,
  },
  {
    key: 'wechat',
    logoSrc: new URL(`../../assets/logo/logo_wechat.svg`, import.meta.url).href,
    name: t('views.application.applicationAccess.wechat'),
    description: t('views.application.applicationAccess.wechatTip'),
    isActive: false,
    exists: false,
  },
  {
    key: 'lark',
    logoSrc: new URL(`../../assets/logo/logo_lark.svg`, import.meta.url).href,
    name: t('views.application.applicationAccess.lark'),
    description: t('views.application.applicationAccess.larkTip'),
    isActive: false,
    exists: false,
  },
  {
    key: 'slack',
    logoSrc: new URL(`../../assets/logo/logo_slack.svg`, import.meta.url).href,
    name: t('views.application.applicationAccess.slack'),
    description: t('views.application.applicationAccess.slackTip'),
    isActive: false,
    exists: false,
  },
])

const AccessSettingDrawerRef = ref()
const loading = ref(false)
const {
  params: { id },
} = route as any

function openDrawer(key: string) {
  AccessSettingDrawerRef.value.open(id, key)
}

function refresh() {
  getPlatformStatus()
}

function getPlatformStatus() {
  loading.value = true
  loadSharedApi({ type: 'application', systemType: apiType.value })
    .getPlatformStatus(id)
    .then((res: any) => {
      platforms.forEach((platform) => {
        platform.isActive = res.data[platform.key][1]
        platform.exists = res.data[platform.key][0]
      })
      loading.value = false
    })
}

function changeStatus(type: string, value: boolean) {
  const data = {
    type: type,
    status: value,
  }
  loadSharedApi({ type: 'application', systemType: apiType.value })
    .updatePlatformStatus(id, data)
    .then(() => {
      MsgSuccess(t('common.saveSuccess'))
    })
}

onMounted(() => {
  getPlatformStatus()
})
</script>

<style lang="scss" scoped></style>
