<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import AccessApi from '@/api/admin/workspace/application/access'
import type { ApplicationAccessStatus } from '@/api/types'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import { MsgSuccess } from '@/utils/message'
import AccessSettingDrawer from './AccessSettingDrawer.vue'
import { accessPlatforms, type AccessPlatformDefinition } from './platforms'

defineOptions({ name: 'ApplicationAccessView' })
defineProps<ResourceDetailPageProps>()

const route = useRoute()
const applicationId = computed(() => String(route.params.applicationId ?? ''))
const loading = ref(false)
const platformStatus = ref<ApplicationAccessStatus>({})
const editingPlatform = ref<AccessPlatformDefinition>()

// 加载发布渠道状态。
function loadPlatformStatus() {
  loading.value = true
  return AccessApi.getPlatformStatus(applicationId.value)
    .then((status) => {
      platformStatus.value = status
    })
    .finally(() => {
      loading.value = false
    })
}

function handleOpenPlatform(platform: AccessPlatformDefinition) {
  if (loading.value) return
  editingPlatform.value = platform
}

// 请求成功后更新开关，失败时保持原有状态。
function handlePlatformStatusChange(platform: AccessPlatformDefinition, value: string | number | boolean) {
  const status = platformStatus.value[platform.key]
  if (loading.value || !status?.[0]) return
  loading.value = true
  return AccessApi.postPlatformStatus(applicationId.value, { type: platform.key, status: value === true })
    .then(() => {
      status[1] = value === true
      MsgSuccess('保存成功')
    })
    .finally(() => {
      loading.value = false
    })
}

watch(
  applicationId,
  () => {
    platformStatus.value = {}
    editingPlatform.value = undefined
    void loadPlatformStatus()
  },
  { immediate: true },
)
</script>

<template>
  <div v-loading="loading" :inert="loading" class="min-h-0 flex-1">
    <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <template v-for="platform in accessPlatforms" :key="platform.key">
        <!-- 点击平台卡片配置发布渠道 -->
        <el-card shadow="hover" class="cursor-pointer" @click="handleOpenPlatform(platform)">
          <div class="flex-between gap-4">
            <div class="flex-align-center min-w-0 gap-3">
              <img :src="platform.logo" :alt="platform.name" class="h-6 w-6 shrink-0" />
              <div class="min-w-0">
                <h4>{{ platform.name }}</h4>
                <p class="text-sm text-N600">{{ platform.description }}</p>
              </div>
            </div>
            <div class="flex-align-center shrink-0 gap-4">
              <!-- 配置发布渠道 -->
              <el-button plain @click.stop="handleOpenPlatform(platform)">{{ platformStatus[platform.key]?.[0] ? '配置' : '未配置' }}</el-button>
              <template v-if="platformStatus[platform.key]?.[0]">
                <el-divider direction="vertical" />
                <!-- 启停发布渠道，阻止点击打开配置 -->
                <span @click.stop>
                  <el-switch
                    :model-value="platformStatus[platform.key]?.[1] ?? false"
                    @change="(value: string | number | boolean) => handlePlatformStatusChange(platform, value)"
                  />
                </span>
              </template>
            </div>
          </div>
        </el-card>
      </template>
    </div>
  </div>

  <AccessSettingDrawer
    v-if="editingPlatform"
    :application-id="applicationId"
    :platform="editingPlatform"
    @refresh="loadPlatformStatus"
    @closed="editingPlatform = undefined"
  />
</template>
