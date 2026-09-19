<script setup lang="ts">
import { RouterView } from 'vue-router'
import { TOOLTIP_SHOW_DELAY } from '@/components/global/mk-tooltip/constants'

const tableConfig = { tooltipOptions: { showAfter: TOOLTIP_SHOW_DELAY } }
</script>

<template>
  <el-config-provider :table="tableConfig">
    <RouterView />
  </el-config-provider>
</template>
