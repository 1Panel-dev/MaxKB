<template>
  <component
    :applicationAvailable="applicationAvailable"
    :is="currentTemplate"
    :application_profile="chatUser.application"
    :key="route.fullPath"
  />
</template>
<script setup lang="ts">
import { ref, computed, onBeforeMount } from 'vue'
import { useRoute } from 'vue-router'
import useStore from '@/stores'
import { useI18n } from 'vue-i18n'
const { locale } = useI18n({ useScope: 'global' })
const route = useRoute()
const { chatUser, common } = useStore()

const components: any = import.meta.glob('@/views/chat/**/index.vue', {
  eager: true,
})

const {
  query: { mode },
} = route as any

const currentTemplate = computed(() => {
  let modeName = ''
  if (chatUser.application) {
    if (!mode || mode === 'pc') {
      modeName = common.isMobile() ? 'mobile' : 'pc'
    } else {
      modeName = mode
    }
  } else {
    modeName = 'no-service'
  }

  const name = `/src/views/chat/${modeName}/index.vue`
  return components[name].default
})

const applicationAvailable = ref<boolean>(true)
onBeforeMount(() => {
  locale.value = chatUser.getLanguage()
})
</script>
