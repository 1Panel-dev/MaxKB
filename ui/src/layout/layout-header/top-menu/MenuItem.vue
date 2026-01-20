<template>
  <div
    class="menu-item-container h-full border-r-6"
    :class="isActive ? 'active' : ''"
    @click="router.push({ name: menu.name })"
  >
    <div class="title flex align-center">
      <AppIcon
        :iconName="isActive ? menu.meta?.iconActive || menu.meta?.icon : menu?.meta?.icon"
        style="font-size: 16px"
        class="mr-4"
      />
      <span> {{ $t(menu.meta?.title as string) }}</span>
    </div>
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
  const { name, path, meta } = route
  return (name == props.menu.name && path == props.menu.path) || meta?.activeMenu == props.menu.path
})
</script>
<style lang="scss" scoped>
.menu-item-container {
  margin-right: 8px;
  cursor: pointer;
  font-size: 14px;
  position: relative;
  padding: 6px 12px;

  .icon {
    font-size: 15px;
    margin-right: 5px;
    margin-top: 2px;
  }

  &:hover {
    background-color: var(--app-text-color-light-1);
  }
  &.active {
    background-color: #ffffff;
    box-shadow: 0px 2px 4px 0px rgba(31, 35, 41, 0.12);

    .title {
      color: var(--el-color-primary) !important;
    }
  }
}
</style>
