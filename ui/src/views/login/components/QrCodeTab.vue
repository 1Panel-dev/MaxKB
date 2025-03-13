<template>
  <el-tabs v-model="activeKey" @tab-change="selectTab">
    <template v-for="item in tabs" :key="item.key">
      <el-tab-pane :label="item.value" :name="item.key">
        <div class="text-center mt-16" v-if="item.key === activeKey">
          <component
            :is="defineAsyncComponent(() => import(`./${item.key}QrCode.vue`))"
            :config="config"
          />
        </div>
      </el-tab-pane>
    </template>
  </el-tabs>
</template>

<script setup lang="ts">
import { onMounted, ref, defineAsyncComponent } from 'vue'

import platformApi from '@/api/platform-source'
import useStore from '@/stores'

interface Tab {
  key: string
  value: string
}

interface PlatformConfig {
  app_key: string
  app_secret: string
  platform: string
  config: any
}

interface Config {
  app_key: string
  app_secret: string
  corpId?: string
  agentId?: string
}

const props = defineProps<{ tabs: Tab[] }>()
const activeKey = ref('')
const allConfigs = ref<PlatformConfig[]>([])
const config = ref<Config>({ app_key: '', app_secret: '' })
// const logoUrl = ref('')
const { user } = useStore()
async function getPlatformInfo() {
  try {
    return await user.getQrSource()
  } catch (error) {
    return []
  }
}

onMounted(async () => {
  if (props.tabs.length > 0) {
    activeKey.value = props.tabs[0].key
  }
  allConfigs.value = await getPlatformInfo()
  updateConfig(activeKey.value)
})

const updateConfig = (key: string) => {
  const selectedConfig = allConfigs.value.find((item) => item.platform === key)
  if (selectedConfig && selectedConfig.config) {
    config.value = selectedConfig.config
  }
}

const selectTab = (key: string) => {
  activeKey.value = key
  updateConfig(key)
}
</script>

<style scoped lang="scss"></style>
