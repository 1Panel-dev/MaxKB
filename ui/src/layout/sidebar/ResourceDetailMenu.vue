<script setup lang="ts">
import { ref, watch } from 'vue'
import type { LayoutMenuItem } from '../types'

defineOptions({ name: 'ResourceDetailMenu' })

const props = defineProps<{ menuItems: LayoutMenuItem[]; activeName: string }>()
const emit = defineEmits<{ select: [menuItem: LayoutMenuItem] }>()

/* 初始展开分组；导航时展开当前页所属分组，保留用户对其他分组的选择。 */
const expandedGroups = ref<string[]>(props.menuItems.filter((menuItem) => menuItem.children?.length).map((menuItem) => menuItem.name))

watch(
  () => props.activeName,
  (activeName) => {
    const activeGroup = props.menuItems.find((menuItem) => menuItem.children?.some((child) => child.name === activeName))
    if (activeGroup && !expandedGroups.value.includes(activeGroup.name)) expandedGroups.value.push(activeGroup.name)
  },
  { immediate: true },
)
</script>

<template>
  <el-collapse v-model="expandedGroups" class="resource-detail-menu space-y-1 border-0! px-4">
    <template v-for="menuItem in props.menuItems" :key="menuItem.name">
      <!-- 展开或收起菜单分组 -->
      <el-collapse-item v-if="menuItem.children?.length" :name="menuItem.name">
        <template #title>
          <span class="flex-align-center min-w-0 gap-3">
            <MkIcon v-if="menuItem.icon" :name="menuItem.icon" />
            <span class="min-w-0 flex-1 truncate" :title="menuItem.label">{{ menuItem.label }}</span>
          </span>
        </template>
        <template #icon="{ isActive }">
          <MkIcon name="icon_down_outlined" class="ml-2 text-N500 transition-transform" :class="{ 'rotate-180': isActive }" />
        </template>
        <div class="space-y-1 pt-1">
          <template v-for="child in menuItem.children" :key="child.name">
            <!-- 切换二级菜单页面 -->
            <MkListItem :active="child.name === props.activeName" @click="emit('select', child)">
              <span class="ml-7 min-w-0 flex-1 truncate" :title="child.label">{{ child.label }}</span>
            </MkListItem>
          </template>
        </div>
      </el-collapse-item>
      <!-- 切换一级菜单页面 -->
      <MkListItem v-else :active="menuItem.name === props.activeName" @click="emit('select', menuItem)">
        <template #default="{ active }">
          <MkIcon v-if="menuItem.icon" class="mr-3" :name="active ? (menuItem.activeIcon ?? menuItem.icon) : menuItem.icon" />
          <span class="min-w-0 flex-1 truncate" :title="menuItem.label">{{ menuItem.label }}</span>
        </template>
      </MkListItem>
    </template>
  </el-collapse>
</template>

<style lang="scss" scoped>
/* 详情导航折叠分组与 MkListItem 使用相同的行尺寸和悬停样式。 */
.resource-detail-menu {
  :deep(.el-collapse-item__content) {
    color: var(--mk-N900);
    font-size: var(--mk-font-size-base);
    line-height: var(--mk-line-height-base);
    padding-bottom: 0;
  }

  :deep(.el-collapse-item__header) {
    background: transparent;
    border: 0;
    border-radius: var(--el-border-radius-base);
    color: var(--mk-N900);
    font-size: var(--mk-font-size-base);
    font-weight: 400;
    height: auto;
    line-height: var(--mk-line-height-base);
    padding: 9px calc(var(--spacing) * 2);

    &:hover {
      background: rgb(var(--mk-N900-rgb) / 10%);
    }
  }

  :deep(.el-collapse-item__title) {
    min-width: 0;
  }

  :deep(.el-collapse-item__wrap) {
    background: transparent;
    border: 0;
  }
}
</style>
