<template>
  <div
    class="menu-item-container flex-center h-full"
    :class="isActive ? 'active' : ''"
    @click="router.push({ name: menu.name })"
  >
    <div class="icon">
      <AppIcon :iconName="menu.meta ? (menu.meta.icon as string) : '404'" />
    </div>
    <div class="title">{{ menu.meta?.title }}</div>
  </div>
</template>
<script setup lang="ts">
import { useRouter, useRoute, type RouteRecordRaw } from 'vue-router'
import { computed } from 'vue'
const router = useRouter()
const route = useRoute()
const props = defineProps<{
  menu: RouteRecordRaw
}>()

const isActive = computed(() => {
  return route.name == props.menu.name && route.path == props.menu.path
})
</script>
<style lang="scss" scoped>
.menu-item-container {
  padding: 0 20px;
  cursor: pointer;
  .icon {
    font-size: 15px;
    margin-right: 5px;
    margin-top: 2px;
  }
  &:hover {
    color: var(--el-color-primary);
  }
}

.active {
  font-weight: 600;
  color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
  border-bottom: 3px solid var(--el-color-primary);
}
</style>
