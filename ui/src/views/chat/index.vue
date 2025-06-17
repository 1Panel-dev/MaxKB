<template>
  <component
    :applicationAvailable="applicationAvailable"
    :is="currentTemplate"
    :application_profile="chatUser.application"
    :key="route.fullPath"
    v-loading="loading"
  />
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import useStore from '@/stores'

const route = useRoute()
const { chatUser } = useStore()

const components: any = import.meta.glob('@/views/chat/**/index.vue', {
  eager: true,
})

const {
  query: { mode },
  params: { accessToken },
} = route as any

const currentTemplate = computed(() => {
  let modeName = ''
  if (!mode || mode === 'pc') {
    modeName = 'pc'
  } else {
    modeName = mode
  }
  const name = `/src/views/chat/${modeName}/index.vue`
  return components[name].default
})

const loading = ref(false)

const applicationAvailable = ref<boolean>(true)
</script>
<style lang="scss"></style>
