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
const { chatUser, common } = useStore()

const components: any = import.meta.glob('@/views/chat/**/index.vue', {
  eager: true,
})

const {
  query: { mode },
} = route as any

const currentTemplate = computed(() => {
  console.log(common.isMobile())
  let modeName = ''
  if (!mode || mode === 'pc') {
    modeName = common.isMobile() ? 'mobile' : 'pc'
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
