<script setup lang="ts">
import { computed } from 'vue'
import Sidebar from '@/layout/components/sidebar/index.vue'
import AppMain from '@/layout/app-main/index.vue'
import LayoutContainer from '@/components/layout-container/index.vue'
import useStore from '@/stores'
import { useRoute } from 'vue-router'
const route = useRoute()
const { user } = useStore()
const {
  params: { folderId }, // id为knowledgeID
  query: { from },
} = route as any
const isShared = computed(() => {
  return (
    folderId === 'shared' ||
    from === 'systemShare' ||
    from === 'systemManage' ||
    route.path.includes('resource-management')
  )
})
</script>

<template>
  <div class="app-layout">
    <div class="app-main" :class="user.isExpire() ? 'isExpire' : ''">
      <LayoutContainer>
        <template #left>
          <Sidebar />
        </template>
        <AppMain />
      </LayoutContainer>
    </div>
  </div>
</template>
<style lang="scss">
@use './index.scss';
</style>
