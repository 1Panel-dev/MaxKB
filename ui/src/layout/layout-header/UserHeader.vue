·
<template>
  <div class="app-top-bar-container border-b flex-center">
    <div class="logo">
      <LogoFull />
    </div>
    <div class="flex-between">
      <div></div>
      <TopMenu></TopMenu>
      <TopUrlMenu></TopUrlMenu>
    </div>
    <Avatar></Avatar>
  </div>
</template>
<script setup lang="ts">
import TopMenu from './top-menu/index.vue'
import Avatar from './avatar/index.vue'
import TopUrlMenu from './top-url-menu/index.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
</script>
<style lang="scss"></style>
