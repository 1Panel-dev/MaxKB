<template>
  <component :is="currentTemplate" :key="route.fullPath" />
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import useStore from '@/stores'
const { application, user } = useStore()

const components: any = import.meta.glob('@/views/chat/**/index.vue', {
  eager: true
})
const route = useRoute()
const {
  query: { mode }
} = route as any

const currentTemplate = computed(() => {
  let modeName = ''
  if (mode && mode === 'embed') {
    modeName = 'embed'
  } else {
    modeName = show_history.value || !user.isEnterprise() ? 'pc' : 'base'
  }

  const name = `/src/views/chat/${modeName}/index.vue`
  return components[name].default
})
const loading = ref(false)

const show_history = ref(false)

function getAppProfile() {
  application.asyncGetAppProfile(loading).then((res: any) => {
    show_history.value = res.data?.show_history
  })
}

onMounted(() => {
  user.asyncGetProfile().then(() => {
    if (user.isEnterprise()) {
      getAppProfile()
    }
  })
})
</script>
<style lang="scss"></style>
