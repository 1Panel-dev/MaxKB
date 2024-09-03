<template>
  <div class="p-16-24">
    <h4 class="mb-16">应用接入</h4>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12" class="mb-16">
        <el-card shadow="hover" class="border-none cursor" style="--el-card-padding: 24px">
          <div class="flex-between">
            <div class="flex align-center ml-8 mr-8">
              <img src="@/assets/logo_wechat-work.svg" alt="" />
              <div class="ml-12">
                <h5 class="mb-4">企业微信</h5>
                <el-text type="info" style="font-size: 12px">打造企业微信智能应用</el-text>
              </div>
            </div>
            <div>
              <el-button class="mr-4" @click="openDrawer()">配置</el-button>
              <el-divider direction="vertical" />
              <el-switch size="large" v-model="is_active" />
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12" class="mb-16">
        <el-card shadow="hover" class="border-none cursor" style="--el-card-padding: 24px">
          <div class="flex-between">
            <div class="flex align-center ml-8 mr-8">
              <img src="@/assets/logo_dingtalk.svg" alt="" />
              <div class="ml-12">
                <h5 class="mb-4">钉钉</h5>
                <el-text type="info" style="font-size: 12px">打造钉钉智能应用</el-text>
              </div>
            </div>
            <div>
              <el-button class="mr-4">配置</el-button>
              <el-divider direction="vertical" />
              <el-switch size="large" v-model="is_active" />
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card shadow="hover" class="border-none cursor" style="--el-card-padding: 24px">
          <div class="flex-between">
            <div class="flex align-center ml-8 mr-8">
              <img src="@/assets/logo_wechat.svg" alt="" />
              <div class="ml-12">
                <h5 class="mb-4">公众号</h5>
                <el-text type="info" style="font-size: 12px">打造公众号智能应用</el-text>
              </div>
            </div>
            <div>
              <el-button class="mr-4">配置</el-button>
              <el-divider direction="vertical" />
              <el-switch size="large" v-model="is_active" />
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card shadow="hover" class="border-none cursor" style="--el-card-padding: 24px">
          <div class="flex-between">
            <div class="flex align-center ml-8 mr-8">
              <img src="@/assets/logo_lark.svg" alt="" />
              <div class="ml-12">
                <h5 class="mb-4">飞书</h5>
                <el-text type="info" style="font-size: 12px">打造飞书智能应用</el-text>
              </div>
            </div>
            <div>
              <el-button class="mr-4">配置</el-button>
              <el-divider direction="vertical" />
              <el-switch size="large" v-model="is_active" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <AccessSettingDrawer ref="AccessSettingDrawerRef" />
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import AccessSettingDrawer from './component/AccessSettingDrawer.vue'

import applicationApi from '@/api/application'

import { MsgSuccess } from '@/utils/message'

const AccessSettingDrawerRef = ref()
const loading = ref(false)
const is_active = ref(false)

function openDrawer() {
  AccessSettingDrawerRef.value.open()
}

function refresh() {}

onMounted(() => {})
</script>
<style lang="scss" scoped></style>
