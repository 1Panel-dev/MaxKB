<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { getChildRouteList } from '@/router/admin/utils'

const props = defineProps<{
  collapsed?: boolean
}>()

const emit = defineEmits<{
  toggle: []
}>()

const route = useRoute()
const router = useRouter()
const systemMenuItems = getChildRouteList('system')
</script>

<template>
  <div class="mk-system-sidebar flex h-full flex-col">
    <el-scrollbar class="min-h-0 flex-1">
      <el-menu
        class="mt-2!"
        :class="props.collapsed ? 'px-3.5!' : 'px-4!'"
        :collapse="props.collapsed"
        :collapse-transition="false"
        :default-active="route.path"
        router
      >
        <template v-for="item in systemMenuItems" :key="item.key">
          <!-- 有子菜单 -->
          <el-sub-menu
            v-if="item.children?.length && item.route"
            :index="router.resolve(item.route).path"
            popper-class="mk-system-sidebar-menu-popper"
          >
            <template #title>
              <MkIcon v-if="item.icon" :name="item.icon" :size="18" />
              <span>{{ item.label }}</span>
            </template>

            <el-menu-item
              v-for="child in item.children"
              :key="child.key"
              :index="child.route ? router.resolve(child.route).path : child.key"
            >
              {{ child.label }}
            </el-menu-item>
          </el-sub-menu>
          <!-- 无子菜单 -->
          <el-menu-item v-else :index="item.route ? router.resolve(item.route).path : item.key">
            <MkIcon v-if="item.icon" :name="item.icon" :size="18" />
            <template #title>{{ item.label }}</template>
          </el-menu-item>
        </template>
      </el-menu>
    </el-scrollbar>

    <!-- 收起导航按钮 -->
    <div>
      <button
        type="button"
        class="flex h-[46px] w-full cursor-pointer items-center gap-2.5 px-1"
        @click="emit('toggle')"
      >
        <MkIcon name="icon_left_outlined" />
        <span :class="props.collapsed && 'hidden'">收起导航</span>
      </button>
    </div>
  </div>
</template>
<style lang="scss">
.mk-system-sidebar,
.mk-system-sidebar-menu-popper {
  /* menu */
  .el-menu {
    background: none !important;
    border: none !important;

    &:not(.el-menu--horizontal) {
      display: flex;
      flex-direction: column;
      gap: calc(var(--spacing) * 1);
    }
  }
  .el-menu-item {
    border-radius: var(--el-border-radius-base);
    color: var(--mk-N900);
    height: auto;
    line-height: 18px;
    padding: 11px calc(var(--spacing) * 2) !important;
    [class^='el-icon'] {
      margin-right: calc(var(--spacing) * 2);
    }
    &:hover {
      background-color: var(--mk-N900-transparent-10);
    }
    &.is-active {
      background-color: white;
      color: var(--mk-primary);
      font-weight: 500;
    }
  }
  // 子菜单
  .el-sub-menu {
    display: flex;
    flex-direction: column;
    gap: calc(var(--spacing) * 1);

    &__title {
      border-radius: var(--el-border-radius-base);
      color: var(--mk-N900);
      height: auto;
      line-height: 18px;
      padding: 11px calc(var(--spacing) * 2) !important;
      &:hover {
        background-color: var(--mk-N900-transparent-10);
      }
    }
    .el-icon {
      margin-right: calc(var(--spacing) * 2);
      width: auto;
    }
    .el-menu-item {
      height: auto;
      line-height: 18px;
      padding: 11px calc(var(--spacing) * 2) !important;
      padding-left: 34px !important;
    }
    .el-sub-menu__icon-arrow {
      font-size: 16px;
      margin-top: calc(var(--spacing) * -2);
      right: 0;
    }
  }

  // 菜单收起
  .el-menu--collapse {
    > .el-menu-item {
      min-height: calc(var(--spacing) * 10);
      .el-menu-tooltip__trigger {
        padding: 11px !important;
      }
    }

    > .el-sub-menu {
      > .el-sub-menu__title {
        min-height: calc(var(--spacing) * 10);
        padding: 11px !important;
      }
      &.is-active > .el-sub-menu__title {
        background-color: white;
      }
    }
  }
}

.el-popper.mk-system-sidebar-menu-popper {
  background-color: var(--mk-layout);
  background-image: var(--mk-layout-gradient);
  border-radius: var(--el-border-radius-base);
  .el-menu {
    padding: calc(var(--spacing) * 2);
    border-radius: var(--el-border-radius-base);
  }
  .el-menu-item {
    padding: 9px calc(var(--spacing) * 4) !important;
  }
}
</style>
