<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getChildRouteList } from '@/router/admin/utils'
import type { RouteLocationRaw } from 'vue-router'

const props = defineProps<{
  collapsed?: boolean
}>()

const emit = defineEmits<{
  toggle: []
}>()

const route = useRoute()
const router = useRouter()
const items = getChildRouteList('system')
const menuRoutes = new Map<string, RouteLocationRaw>()

const activeKey = computed(() => {
  const matchedMenu = [...route.matched]
    .reverse()
    .find((item) => item.name && menuRoutes.has(String(item.name)))

  return matchedMenu?.name ? String(matchedMenu.name) : ''
})

const defaultOpeneds = items.filter((item) => item.children?.length).map((item) => item.key)

function handleSelect(index: string) {
  const targetRoute = menuRoutes.get(index)
  if (targetRoute) router.push(targetRoute)
}
</script>

<template>
  <div class="mk-sidebar-system flex h-full flex-col">
    <el-scrollbar class="min-h-0 flex-1">
      <el-menu
        :class="props.collapsed ? 'w-12!' : 'w-full!'"
        :collapse="props.collapsed"
        :collapse-transition="false"
        :default-active="activeKey"
        :default-openeds="defaultOpeneds"
        @select="handleSelect"
      >
        <template v-for="item in items" :key="item.key">
          <el-sub-menu v-if="item.children?.length" :index="item.key">
            <template #title>
              <MkIcon v-if="item.icon" :name="item.icon" />
              <span>{{ item.label }}</span>
            </template>

            <el-menu-item v-for="child in item.children" :key="child.key" :index="child.key">
              {{ child.label }}
            </el-menu-item>
          </el-sub-menu>

          <el-menu-item v-else :index="item.key">
            <MkIcon v-if="item.icon" :name="item.icon" />
            <template #title>{{ item.label }}</template>
          </el-menu-item>
        </template>
      </el-menu>
    </el-scrollbar>

    <div :class="props.collapsed ? 'px-2.5 pb-[18px]' : 'px-5 pb-[18px] max-md:px-2.5'">
      <button
        type="button"
        class="flex h-[46px] w-full cursor-pointer items-center gap-2.5 px-1"
        @click="emit('toggle')"
      >
        <MkIcon name="icon_left_outlined" />
        <span :class="props.collapsed && 'hidden'" class="max-md:hidden">收起导航</span>
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.mk-sidebar-system {

}
</style>
