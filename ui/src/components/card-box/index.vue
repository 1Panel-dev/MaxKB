<template>
  <el-card shadow="always" class="card-box" @mouseenter="cardEnter()" @mouseleave="cardLeave()">
    <div class="card-header">
      <slot name="header">
        <div class="title flex align-center">
          <AppAvatar v-if="!slots.icon && showIcon" class="mr-12" shape="square" :size="32">
            <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
          </AppAvatar>
          <slot v-else name="icon"> </slot>
          <h4 class="ellipsis-1">{{ title }}</h4>
        </div>
      </slot>
    </div>
    <div class="description mt-12">
      <slot name="description">
        {{ description }}
      </slot>
    </div>
    <slot />
    <slot name="mouseEnter" v-if="$slots.mouseEnter && show" />
    <div class="card-footer" v-if="$slots.footer">
      <slot name="footer" />
    </div>
  </el-card>
</template>
<script setup lang="ts">
import { ref, useSlots } from 'vue'

const slots = useSlots()
defineOptions({ name: 'CardBox' })
const props = withDefaults(
  defineProps<{
    /**
     * 标题
     */
    title?: string
    /**
     * 描述
     */
    description?: string
    /**
     * 是否展示icon
     */
    showIcon?: boolean
  }>(),
  { title: '标题', description: '', showIcon: true }
)

const show = ref(false)
function cardEnter() {
  show.value = true
}
function cardLeave() {
  show.value = false
}
</script>
<style lang="scss" scoped>
.card-box {
  font-size: 14px;
  position: relative;
  min-height: var(--card-min-height);
  border: 1px solid #ffffff;
  border-radius: 8px;
  .description {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    overflow: hidden;
    height: 40px;
    color: var(--app-text-color-secondary);
    line-height: 22px;
    font-weight: 400;
  }
  .card-footer {
    position: absolute;
    bottom: 8px;
    left: 0;
    min-height: 30px;
    color: var(--app-text-color-secondary);
    font-weight: 400;
    padding: 0 16px;
    width: 100%;
    box-sizing: border-box;
  }
}
</style>
