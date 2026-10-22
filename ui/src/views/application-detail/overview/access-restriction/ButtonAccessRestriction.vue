<script setup lang="ts">
import { ref } from 'vue'
import { useStore } from '@/stores/admin'
import AccessRestrictionDrawer from './AccessRestrictionDrawer.vue'
import XpackAccessRestrictionDrawer from './XpackAccessRestrictionDrawer.vue'

defineOptions({ name: 'ButtonAccessRestriction' })

const { auth } = useStore()
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
  <template v-if="drawerVisible">
    <AccessRestrictionDrawer v-if="auth.isCE" @closed="drawerVisible = false" />
    <XpackAccessRestrictionDrawer v-else @closed="drawerVisible = false" />
  </template>
</template>
