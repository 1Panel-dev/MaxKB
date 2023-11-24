<template>
  <router-view v-slot="{ Component }">
    <transition appear name="fade-transform" mode="out-in">
      <keep-alive :include="cachedViews">
        <component :is="Component" :key="route.fullPath" />
      </keep-alive>
    </transition>
  </router-view>
</template>

<script setup lang="ts">
import { ref, onBeforeUpdate } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const cachedViews: any = ref([])
onBeforeUpdate(() => {
  const { name, meta } = route
  let isCached = meta?.cache
  if (isCached && name && !cachedViews.value.includes(name)) {
    cachedViews.value.push(name)
  }
})
</script>
