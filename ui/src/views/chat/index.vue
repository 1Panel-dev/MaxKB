<template>
  <component :is="currentTemplate" :key="route.fullPath" />
</template>
<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import useStore from '@/stores'
const { user } = useStore()

const components: any = import.meta.glob('@/views/chat/**/index.vue', {
  eager: true
})
const route = useRoute()
const {
  query: { mode }
} = route as any

const currentTemplate = computed(() => {
  const name = `/src/views/chat/${mode || 'pc'}/index.vue`
  return components[name].default
})

onMounted(() => {
  user.asyncGetProfile()
})
</script>
<style lang="scss"></style>
