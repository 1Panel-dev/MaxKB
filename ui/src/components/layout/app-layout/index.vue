<script setup lang="ts">
import { ref, onBeforeUpdate } from 'vue'
import { useRoute } from 'vue-router'
import TopBar from '@/components/layout/top-bar/index.vue'

const route = useRoute()
const cachedViews: any = ref([])

onBeforeUpdate(() => {
  let isCached = route.meta?.cache
  let name = route.name
  if (isCached && name && !cachedViews.value.includes(name)) {
    cachedViews.value.push(name)
  }
})
</script>

<template>
  <div class="app-layout">
    <div class="app-header">
      <TopBar></TopBar>
    </div>
    <div class="app-main">
      <router-view v-slot="{ Component }">
        <transition appear name="fade-transform" mode="out-in">
          <keep-alive :include="cachedViews">
            <component :is="Component" />
          </keep-alive>
        </transition>
      </router-view>
    </div>
  </div>
</template>
<style lang="scss" scoped>
.app-main {
  height: calc(100vh - var(--app-header-height));
  padding: 0 !important;
}
</style>
