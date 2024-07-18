<script setup lang="ts">
import { AppHeader, AppMain } from '../components'
import useStore from '@/stores'
const { user } = useStore()
</script>

<template>
  <div class="app-layout">
    <AppHeader />
    <div class="app-main" :class="user.isExpire() ? 'isExpire' : ''">
      <AppMain />
    </div>
  </div>
</template>
<style lang="scss">
@import './index.scss';
</style>
