<script setup lang="ts">
import { ref } from 'vue'
import AccessRestrictionDrawer from './AccessRestrictionDrawer.vue'
import type { ApplicationAccessToken } from '@/api/types'

defineProps<{ accessTokenConfig?: ApplicationAccessToken }>()

defineOptions({ name: 'ButtonAccessRestriction' })

const drawerVisible = ref(false)

function handleOpenAccessRestriction() {
  drawerVisible.value = true
}
</script>

<template>
  <!-- 设置访问限制 -->
  <el-button plain @click="handleOpenAccessRestriction">
    <MkIcon name="icon-lock" />
    <span>访问限制</span>
  </el-button>
  <AccessRestrictionDrawer v-if="drawerVisible" :initial-config="accessTokenConfig" @closed="drawerVisible = false" />
</template>
