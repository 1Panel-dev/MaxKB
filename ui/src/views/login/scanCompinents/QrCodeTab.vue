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
import {onMounted, ref, defineAsyncComponent} from 'vue'
import useStore from '@/stores'

const {login} = useStore()

interface Tab {
  key: string
  value: string
}

interface PlatformConfig {
  app_key: string
  app_secret: string
  auth_type: string
  config: any
}

interface Config {
  app_key: string
  app_secret: string
  corpId?: string
  agentId?: string
}

const props = defineProps<{ tabs: Tab[], defaultTab?: string }>()
const activeKey = ref('')
const allConfigs = ref<PlatformConfig[]>([])
const config = ref<Config>({app_key: '', app_secret: ''})


async function getPlatformInfo() {
  try {
    return await login.getQrSource()
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
  console.log(props.defaultTab)
  if (props.defaultTab) {
    selectTab(props.defaultTab)
  }
})

const updateConfig = (key: string) => {
  const selectedConfig = allConfigs.value.find((item) => item.auth_type === key)
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
