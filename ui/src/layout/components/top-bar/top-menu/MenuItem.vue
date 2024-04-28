<template>
  <div class="menu-item-container flex-center h-full" :class="isActive ? 'active' : ''"
    @click="router.push({ name: menu.name })">
    <!-- <div class="icon">
      <AppIcon :iconName="menu.meta ? (menu.meta.icon as string) : '404'" />
    </div> -->
    <div class="title">
      {{
        $te(`layout.topbar.MenuItem.${String(props.menu.name)}`)
          ? $t(`layout.topbar.MenuItem.${String(props.menu.name)}`)
          : menu.meta?.title
      }}
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
  margin-right: 28px;
  cursor: pointer;
  font-size: 16px;
  position: relative;

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
  color: var(--el-color-primary);

  &::after {
    position: absolute;
    bottom: 0;
    width: 100%;
    height: 2px;
    content: '';
    background-color: var(--el-color-primary-light-9);
    border-bottom: 3px solid var(--el-color-primary);
  }
}
</style>
