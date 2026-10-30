<script setup lang="ts">
import { ref } from 'vue'
import AccessRestrictionDrawer from './AccessRestrictionDrawer.vue'

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
  <AccessRestrictionDrawer v-if="drawerVisible" @closed="drawerVisible = false" />
</template>
