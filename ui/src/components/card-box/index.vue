<template>
  <el-card shadow="hover" class="card-box" @mouseenter="cardEnter()" @mouseleave="cardLeave()">
    <div class="card-header">
      <slot name="header">
        <div class="title flex align-center">
          <slot name="icon">
            <AppAvatar v-if="showIcon" class="mr-12 avatar-blue" shape="square" :size="32">
              <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
            </AppAvatar>
          </slot>
          <auto-tooltip :content="title" style="width: 65%">
            {{ title }}
          </auto-tooltip>
        </div>
      </slot>
    </div>
    <div class="description break-all mt-12" v-if="$slots.description || description">
      <slot name="description">
        <div class="content">
          {{ description }}
        </div>
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
  { title: '标题', description: '', showIcon: true, border: true }
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
  min-width: var(--card-min-width);
  border-radius: 8px;
  .description {
    color: var(--app-text-color-secondary);
    line-height: 22px;
    font-weight: 400;
    .content {
      display: -webkit-box;
      height: var(--app-card-box-description-height, 40px);
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
      overflow: hidden;
    }
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
