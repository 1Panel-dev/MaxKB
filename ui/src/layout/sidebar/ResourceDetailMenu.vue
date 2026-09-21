<script setup lang="ts">
import { ref, watch } from 'vue'
import type { LayoutMenuItem } from '../types'

defineOptions({ name: 'ResourceDetailMenu' })

const props = defineProps<{ menuItems: LayoutMenuItem[]; activeName: string }>()
const emit = defineEmits<{ select: [menuItem: LayoutMenuItem] }>()

/* 初始展开分组；导航时展开当前页所属分组，保留用户对其他分组的选择。 */
const expandedGroups = ref<Record<string, boolean>>(
  Object.fromEntries(props.menuItems.filter((menuItem) => menuItem.children?.length).map((menuItem) => [menuItem.name, true])),
)

watch(
  () => props.activeName,
  (activeName) => {
    const activeGroup = props.menuItems.find((menuItem) => menuItem.children?.some((child) => child.name === activeName))
    if (activeGroup) expandedGroups.value[activeGroup.name] = true
  },
  { immediate: true },
)
</script>

<template>
  <div class="space-y-1 px-4">
    <template v-for="menuItem in props.menuItems" :key="menuItem.name">
      <!-- 展开或收起菜单分组 -->
      <MkCollapse
        v-if="menuItem.children?.length"
        v-model:expanded="expandedGroups[menuItem.name]"
        indicator-position="after"
        trigger-class="rounded-md px-2 py-[9px] text-N900 hover:bg-N900/10"
      >
        <template #label>
          <span class="flex-align-center min-w-0 flex-1 gap-2">
            <MkIcon v-if="menuItem.icon" :name="menuItem.icon" :size="18" />
            <span class="min-w-0 flex-1 truncate" :title="menuItem.label">{{ menuItem.label }}</span>
          </span>
        </template>
        <div class="space-y-1 pt-1">
          <template v-for="child in menuItem.children" :key="child.name">
            <!-- 切换二级菜单页面 -->
            <MkListItem :active="child.name === props.activeName" @click="emit('select', child)">
              <span class="ml-6 min-w-0 flex-1 truncate" :title="child.label">{{ child.label }}</span>
            </MkListItem>
          </template>
        </div>
      </MkCollapse>
      <!-- 切换一级菜单页面 -->
      <MkListItem v-else :active="menuItem.name === props.activeName" @click="emit('select', menuItem)">
        <template #default="{ active }">
          <MkIcon v-if="menuItem.icon" class="mr-2" :name="active ? (menuItem.activeIcon ?? menuItem.icon) : menuItem.icon" :size="18" />
          <span class="min-w-0 flex-1 truncate" :title="menuItem.label">{{ menuItem.label }}</span>
        </template>
      </MkListItem>
    </template>
  </div>
</template>
