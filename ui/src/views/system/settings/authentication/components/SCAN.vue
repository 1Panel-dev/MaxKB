<script setup lang="ts">
import { onMounted, ref, useTemplateRef } from 'vue'
import PlatformSourceApi from '@/api/admin/system/platform-source'
import type { QrLoginPlatformRequest, QrLoginPlatformType } from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import EditModal from './EditModal.vue'

interface QrPlatformView extends QrLoginPlatformRequest {
  isValid: boolean
  name: string
}

const platformDefinitions: Array<{
  configKeys: string[]
  key: QrLoginPlatformType
  name: string
}> = [
  { key: 'wecom', name: '企业微信', configKeys: ['corp_id', 'agent_id', 'app_secret'] },
  { key: 'dingtalk', name: '钉钉', configKeys: ['corp_id', 'app_key', 'app_secret'] },
  { key: 'lark', name: '飞书', configKeys: ['app_key', 'app_secret'] },
]

const editModalRef = useTemplateRef<InstanceType<typeof EditModal>>('editModalRef')
const loading = ref(false)
const platforms = ref<QrPlatformView[]>(createDefaultPlatforms())
const fieldLabels: Record<string, string> = {
  agent_id: 'Agent ID',
  app_key: 'App Key',
  app_secret: 'App Secret',
  callback_url: '回调地址',
  corp_id: 'Corp ID',
}

function createDefaultPlatforms() {
  const apiBaseUrl = `${window.location.origin}${window.MaxKB?.prefix ?? ''}/api`
  return platformDefinitions.map(({ configKeys, key, name }) => ({
    key,
    name,
    config: Object.fromEntries([
      ...configKeys.map((configKey) => [configKey, '']),
      ['callback_url', `${apiBaseUrl}/${key}`],
    ]),
    isActive: false,
    isValid: false,
  }))
}

/* 扫码登录平台加载与状态切换 */
function loadPlatforms() {
  loading.value = true
  return PlatformSourceApi.getQrLoginPlatforms()
    .then((settings) => {
      const defaultPlatforms = createDefaultPlatforms()
      platforms.value = defaultPlatforms.map((platform) => {
        const setting = settings.find(({ auth_type }) => auth_type === platform.key)
        if (!setting) return platform
        return {
          ...platform,
          config: { ...platform.config, ...setting.config },
          isActive: setting.is_active,
          isValid: setting.is_valid,
        }
      })
    })
    .finally(() => {
      loading.value = false
    })
}

function togglePlatform(platform: QrPlatformView) {
  loading.value = true
  PlatformSourceApi.putQrLoginPlatform(platform)
    .then(() => MsgSuccess('保存成功'))
    .finally(() => {
      loading.value = false
    })
}

function editPlatform(platform: QrPlatformView) {
  editModalRef.value?.open(platform)
}

onMounted(loadPlatforms)
</script>

<template>
  <div v-loading="loading" class="h-full min-h-0">
    <el-scrollbar>
      <div class="max-w-240 space-y-4 px-6 pb-6 pt-4">
        <article
          v-for="platform in platforms"
          :key="platform.key"
          class="rounded-md border border-N300 p-5"
        >
          <div class="flex-between">
            <div class="flex items-center gap-3">
              <div class="flex-center h-9 w-9 rounded-md bg-primary/10 text-primary">
                {{ platform.name.slice(0, 1) }}
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <h6>{{ platform.name }}</h6>
                  <el-tag v-if="platform.isValid" size="small" type="success">已验证</el-tag>
                </div>
                <p class="text-N500">配置后，用户可通过{{ platform.name }}扫码登录。</p>
              </div>
            </div>

            <div v-if="platform.isValid" class="flex items-center gap-2">
              <span class="text-N500">{{ platform.isActive ? '已启用' : '未启用' }}</span>
              <el-switch v-model="platform.isActive" @change="togglePlatform(platform)" />
            </div>
            <el-button v-else type="primary" @click="editPlatform(platform)">接入</el-button>
          </div>

          <template v-if="platform.isValid">
            <el-divider class="!my-4" />
            <dl class="grid grid-cols-2 gap-x-8 gap-y-3">
              <div v-for="(value, key) in platform.config" :key="key" class="min-w-0">
                <dt class="text-N500">{{ fieldLabels[key] ?? key }}</dt>
                <dd class="truncate text-N900">
                  {{ key === 'app_secret' ? '••••••••••••' : value }}
                </dd>
              </div>
            </dl>
            <div class="mt-4 flex gap-3">
              <el-button type="primary" @click="editPlatform(platform)">编辑</el-button>
              <el-button @click="editPlatform(platform)">验证</el-button>
            </div>
          </template>
        </article>
      </div>
    </el-scrollbar>

    <EditModal ref="editModalRef" @saved="loadPlatforms" />
  </div>
</template>
