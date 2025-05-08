<template>
  <el-card shadow="hover" class="card-box" @mouseenter="cardEnter()" @mouseleave="cardLeave()">
    <div class="card-header">
      <slot name="header">
        <div class="title flex align-center" :class="$slots.subTitle ? 'mt-4' : ''">
          <slot name="icon">
            <el-avatar v-if="showIcon" class="mr-12 avatar-blue" shape="square" :size="32">
              <img src="@/assets/knowledge/icon_document.svg" style="width: 58%" alt="" />
            </el-avatar>
          </slot>
          <div style="width: 90%">
            <slot name="title">
              <div>
                {{ title }}
              </div>
            </slot>
            <slot name="subTitle"> </slot>
          </div>
        </div>
      </slot>
    </div>
    <div class="description break-all mt-12">
      <slot>
        <div class="content">
          {{ description }}
        </div>
      </slot>
    </div>
    <div @mouseenter="subHoveredEnter">
      <slot name="mouseEnter" v-if="$slots.mouseEnter && show" />
    </div>
    <div class="card-footer" v-if="$slots.footer">
      <slot name="footer" />
    </div>
  </el-card>
</template>
<script setup lang="ts">
import { ref, useSlots } from 'vue'
import { t } from '@/locales'
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
  { title: t('common.title'), description: '', showIcon: true, border: true },
)

const show = ref(false)
// card上面存在dropdown菜单
const subHovered = ref(false)
function cardEnter() {
  show.value = true
  subHovered.value = false
}

function cardLeave() {
  show.value = subHovered.value
}

function subHoveredEnter() {
  subHovered.value = true
}
</script>
<style lang="scss" scoped>
.card-box {
  font-size: 14px;
  position: relative;
  min-height: var(--card-min-height);
  min-width: var(--card-min-width);
  border-radius: 8px;
  .card-header {
    margin-top: -10px;
  }
  .description {
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
    bottom: 4px;
    left: 0;
    min-height: 30px;
    font-weight: 400;
    padding: 0 16px;
    width: 100%;
    box-sizing: border-box;
  }
}
</style>
