<template>
  <div class="p-16-24">
    <h4 class="mb-16">应用接入</h4>

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
        <el-card shadow="hover" class="border-none cursor" style="--el-card-padding: 24px">
          <div class="flex-between">
            <div class="flex align-center ml-8 mr-8">
              <img :src="item.logoSrc" alt="" class="icon" />
              <div class="ml-12">
                <h5 class="mb-4">{{ item.name }}</h5>
                <el-text type="info" style="font-size: 12px">{{ item.description }}</el-text>
              </div>
            </div>
            <div>
              <el-switch
                size="small"
                v-model="item.isActive"
                @change="changeStatus(item.key, item.isActive)"
                :disabled="!item.exists"
              />
              <el-divider direction="vertical" />
              <el-button class="mr-4" @click="openDrawer(item.key)">配置</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <AccessSettingDrawer ref="AccessSettingDrawerRef" @refresh="refresh" />
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import AccessSettingDrawer from './component/AccessSettingDrawer.vue'
import applicationApi from '@/api/application'
import { MsgSuccess } from '@/utils/message'
import { useRoute } from 'vue-router'

// 平台数据
const platforms = reactive([
  {
    key: 'wecom',
    logoSrc: new URL(`../../assets/logo_wechat-work.svg`, import.meta.url).href,
    name: '企业微信应用',
    description: '打造企业微信智能应用',
    isActive: false,
    exists: false
  },
  {
    key: 'dingtalk',
    logoSrc: new URL(`../../assets/logo_dingtalk.svg`, import.meta.url).href,
    name: '钉钉应用',
    description: '打造钉钉智能应用',
    isActive: false,
    exists: false
  },
  {
    key: 'wechat',
    logoSrc: new URL(`../../assets/logo_wechat.svg`, import.meta.url).href,
    name: '公众号',
    description: '打造公众号智能应用',
    isActive: false,
    exists: false
  },
  {
    key: 'feishu',
    logoSrc: new URL(`../../assets/logo_lark.svg`, import.meta.url).href,
    name: '飞书应用',
    description: '打造飞书智能应用',
    isActive: false,
    exists: false
  }
])

const AccessSettingDrawerRef = ref()
const loading = ref(false)
const route = useRoute()
const {
  params: { id }
} = route as any

function openDrawer(key: string) {
  AccessSettingDrawerRef.value.open(id, key)
}

function refresh() {
  getPlatformStatus()
}

function getPlatformStatus() {
  loading.value = true
  applicationApi.getPlatformStatus(id).then((res: any) => {
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
    status: value
  }
  applicationApi.updatePlatformStatus(id, data).then(() => {
    MsgSuccess('操作成功')
  })
}

onMounted(() => {
  getPlatformStatus()
})
</script>

<style lang="scss" scoped>
.p-16-24 {
  padding: 16px 24px;
}

.mb-16 {
  margin-bottom: 16px;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.flex {
  display: flex;
}

.align-center {
  align-items: center;
}

.ml-8 {
  margin-left: 8px;
}

.mr-8 {
  margin-right: 8px;
}

.ml-12 {
  margin-left: 12px;
}

.mr-4 {
  margin-right: 4px;
}

.cursor {
  cursor: pointer;
}

.icon {
  width: 32px; // 设置图标宽度
  height: 32px; // 设置图标高度
}
</style>
