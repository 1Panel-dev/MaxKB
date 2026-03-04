<template>
  <div class="app-layout">
    <div class="app-main" :class="user.isExpire() ? 'isExpire' : ''">
      <layout-container>
        <template #left>
          <Sidebar />
        </template>
        <AppMain />
      </layout-container>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import Sidebar from '@/layout/components/sidebar/index.vue'
import AppMain from '@/layout/app-main/index.vue'
import useStore from '@/stores'
import { useRoute } from 'vue-router'
const route = useRoute()
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
const { user } = useStore()
</script>
<style lang="scss" scoped>
@use './index.scss';
</style>
