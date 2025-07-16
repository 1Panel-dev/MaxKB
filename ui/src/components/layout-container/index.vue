<template>
  <div class="layout-container flex h-full">
    <div :class="`layout-container__left border-r ${isCollapse ? 'hidden' : ''}`">
      <div class="layout-container__left_content">
        <slot name="left"></slot>
      </div>
      <el-tooltip
        :content="isCollapse ? $t('common.expand') : $t('common.collapse')"
        placement="right"
      >
        <el-button
          v-if="props.showCollapse"
          class="collapse"
          size="small"
          circle
          @click="isCollapse = !isCollapse"
          :icon="isCollapse ? 'ArrowRightBold' : 'ArrowLeftBold'"
        />
      </el-tooltip>
    </div>
    <div class="layout-container__right">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, useSlots, ref } from 'vue'
defineOptions({ name: 'LayoutContainer' })
const slots = useSlots()
const props = defineProps({
  header: String || null,
  backTo: String,
  showCollapse: Boolean,
})

const isCollapse = ref(false)

const showBack = computed(() => {
  const { backTo } = props
  return backTo
})
</script>

<style lang="scss" scoped>
.layout-container {
  &__left {
    position: relative;
    box-sizing: border-box;
    transition: width 0.28s;
    width: var(--sidebar-width);
    min-width: var(--sidebar-width);
    box-sizing: border-box;

    .collapse {
      position: absolute;
      top: 36px;
      right: -12px;
      box-shadow: 0px 5px 10px 0px rgba(31, 35, 41, 0.1);
      z-index: 1;
    }

    .layout-container__left_content {
      width: 100%;
      // height: 100%;
    }

    &.hidden {
      width: 0;
      min-width: 0;

      .layout-container__left_content {
        visibility: hidden;
      }

      .collapse {
        right: -18px;
      }
    }
  }

  &__right {
    flex: 1;
    overflow: hidden;
  }
}
</style>
