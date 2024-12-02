<template>
  <div v-loading="loading">
    <el-card shadow="hover" class="border-none cursor" style="--el-card-padding: 16px 24px">
      <div v-for="item in platforms" :key="item.key" class="mb-16">
        <el-card class="mb-16" shadow="hover" style="--el-card-padding: 16px">
          <div class="flex-between">
            <div class="flex align-center ml-8 mr-8">
              <img :src="item.logoSrc" alt="" class="icon" />
              <h5 style="margin-left: 8px">{{ item.name }}</h5>
              <el-tag v-if="item.isValid" type="success" class="ml-4">有效</el-tag>
            </div>
            <div>
              <el-button type="primary" v-if="!item.isValid" @click="showDialog(item)"
                >接入</el-button
              >
              <span v-if="item.isValid">
                <span class="mr-4">{{ item.isActive ? '已开启' : '未开启' }}</span>
                <el-switch
                  size="small"
                  v-model="item.isActive"
                  :disabled="!item.isValid"
                  @change="changeStatus(item)"
                />
              </span>
            </div>
          </div>
          <el-collapse-transition>
            <div v-if="item.isValid" class="border-t mt-16">
              <el-row :gutter="12" class="mt-16">
                <el-col v-for="(value, key) in item.config" :key="key" :span="12">
                  <el-text type="info">{{ formatFieldName(key, item) }}</el-text>
                  <div class="mt-4 mb-16 flex align-center">
                    <span
                      v-if="key !== 'app_secret'"
                      class="vertical-middle lighter break-all ellipsis-1"
                      >{{ value }}</span
                    >
                    <span
                      v-if="key === 'app_secret' && !showPassword[item.key]?.[key]"
                      class="vertical-middle lighter break-all ellipsis-1"
                      >************</span
                    >
                    <span
                      v-if="key === 'app_secret' && showPassword[item.key]?.[key]"
                      class="vertical-middle lighter break-all ellipsis-1"
                      >{{ value }}</span
                    >
                    <el-button type="primary" text @click="() => copyClick(value)">
                      <AppIcon iconName="app-copy" />
                    </el-button>
                    <el-button
                      v-if="key === 'app_secret'"
                      type="primary"
                      text
                      @click="toggleShowPassword(item.key)"
                    >
                      <el-icon v-if="key === 'app_secret' && !showPassword[item.key]?.[key]">
                        <Hide />
                      </el-icon>
                      <el-icon v-if="key === 'app_secret' && showPassword[item.key]?.[key]">
                        <View />
                      </el-icon>
                    </el-button>
                  </div>
                </el-col>
              </el-row>
              <el-button type="primary" @click="showDialog(item)">编辑</el-button>
              <el-button @click="validateConnection(item)">校验</el-button>
            </div>
          </el-collapse-transition>
        </el-card>
      </div>
      <EditModel ref="EditModelRef" @refresh="refresh" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { copyClick } from '@/utils/clipboard'
import EditModel from './EditModal.vue'
import platformApi from '@/api/platform-source'
import { MsgError, MsgSuccess } from '@/utils/message'

interface PlatformConfig {
  [key: string]: string
}

interface Platform {
  key: string
  logoSrc: string
  name: string
  isActive: boolean
  isValid: boolean
  config: PlatformConfig
}

const EditModelRef = ref()
const loading = ref(false)
const platforms = reactive<Platform[]>(initializePlatforms())
const showPassword = reactive<{ [platformKey: string]: { [key: string]: boolean } }>({})

onMounted(() => {
  getPlatformInfo()
})

function initializePlatforms(): Platform[] {
  return [
    createPlatform('wecom', '企业微信'),
    createPlatform('dingtalk', '钉钉'),
    createPlatform('lark', '飞书')
  ]
}

function createPlatform(key: string, name: string): Platform {
  let logo = ''
  switch (key) {
    case 'wecom':
      logo = 'wechat-work'
      break
    case 'dingtalk':
      logo = 'dingtalk'
      break
    case 'lark':
      logo = 'lark'
      break
    default:
      logo = '' // 默认值
      break
  }

  const config = {
    ...(key === 'wecom' ? { corp_id: '', agent_id: '' } : { app_key: '' }),
    app_secret: '',
    callback_url: ''
  }

  return {
    key,
    logoSrc: new URL(`../../../assets/logo_${logo}.svg`, import.meta.url).href,
    name,
    isActive: false,
    isValid: false,
    config
  }
}

function formatFieldName(key?: any, item?: Platform): string {
  const fieldNames: { [key: string]: string } = {
    corp_id: 'Corp ID',
    app_key: item?.key != 'lark' ? 'APP Key' : 'App ID',
    app_secret: 'APP Secret',
    agent_id: 'Agent ID',
    callback_url: '回调地址'
  }
  return (
    fieldNames[key as keyof typeof fieldNames] ||
    (key ? key.charAt(0).toUpperCase() + key.slice(1) : '')
  )
}

function getPlatformInfo() {
  loading.value = true
  platformApi.getPlatformInfo(loading).then((res: any) => {
    if (res) {
      platforms.forEach((platform) => {
        const data = res.data.find((item: any) => item.platform === platform.key)
        if (data) {
          Object.assign(platform, {
            isValid: data.is_valid,
            isActive: data.is_active,
            config: data.config
          })
          if (platform.key === 'dingtalk') {
            const { corp_id, app_key, app_secret } = platform.config
            platform.config = {
              corp_id,
              app_key,
              app_secret,
              callback_url: platform.config.callback_url
            }
          }
          showPassword[platform.key] = {}
          showPassword[platform.key]['app_secret'] = false
        }
      })
    }
  })
}

function validateConnection(currentPlatform: Platform) {
  platformApi.validateConnection(currentPlatform, loading).then((res: any) => {
    res.data ? MsgSuccess('校验成功') : MsgError('校验失败')
  })
}

function refresh() {
  getPlatformInfo()
}

function changeStatus(currentPlatform: Platform) {
  platformApi.updateConfig(currentPlatform, loading).then((res: any) => {
    MsgSuccess('操作成功')
  })
}

function toggleShowPassword(platformKey: string) {
  if (!showPassword[platformKey]) {
    showPassword[platformKey] = {}
  }
  showPassword[platformKey]['app_secret'] = !showPassword[platformKey]['app_secret']
}

function showDialog(platform: Platform) {
  EditModelRef.value?.open(platform)
}
</script>

<style lang="scss" scoped>
.icon {
  width: 24px;
  height: 24px;
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

.ml-4 {
  margin-left: 4px;
}

.ml-8 {
  margin-left: 8px;
}

.mr-8 {
  margin-right: 8px;
}

.mb-16 {
  margin-bottom: 16px;
}

.border-t {
  border-top: 1px solid #ebeef5;
}

.vertical-middle {
  vertical-align: middle;
}
</style>
