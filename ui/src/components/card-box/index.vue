<template>
  <el-card shadow="hover" class="card-box" @mouseenter="cardEnter()" @mouseleave="cardLeave()">
    <div class="card-header">
      <slot name="header">
        <div class="title flex align-center">
          <div class="mr-12 flex align-center" v-if="showIcon">
            <slot name="icon">
              <el-avatar shape="square" :size="32" class="avatar-blue">
                <img src="@/assets/knowledge/icon_document.svg" style="width: 58%" alt="" />
              </el-avatar>
            </slot>
          </div>
          <div style="width: 90%">
            <slot name="title">
              <div>
                {{ title }}
              </div>
            </slot>
            <slot name="subTitle"> </slot>
            <div class="shared" v-if="isShared">{{t('views.system.shared')}}</div>
          </div>
          <div class="status-tag">
            <slot name="tag"> </slot>
          </div>
        </div>
      </slot>
    </div>
    <div class="description break-all mt-12">
      <slot>
        <div class="content color-secondary">
          {{ description }}
        </div>
      </slot>
    </div>

    <div class="card-footer flex-between" v-if="$slots.footer || $slots.mouseEnter">
      <div>
        <slot name="footer"></slot>
      </div>
      <div @mouseenter="subHoveredEnter">
        <slot name="mouseEnter" v-if="$slots.mouseEnter && show" />
      </div>
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
    isShared?: boolean
  }>(),
  { title: t('common.title'), description: '', showIcon: true, border: true, isShared: false },
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
  .card-header {
    margin-top: -5px;
  }
  .description {
    line-height: 22px;
    font-weight: 400;
    min-height: 70px;
    .content {
      display: -webkit-box;
      height: var(--app-card-box-description-height, 40px);
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
      overflow: hidden;
    }
  }

  .shared {
    position: absolute;
    right: 20px;
    top: 17px;
    font-weight: 400;
    font-size: 12px;
    line-height: 20px;
    color: #646a73;

    &::after {
        content: '';
        background-color: #1f23291a;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 32px;
        height: 20px;
        border-radius: 4px;
      }
  }

  .card-footer {
    position: absolute;
    bottom: 8px;
    left: 0;
    min-height: 30px;
    font-weight: 400;
    padding: 0 16px;
    width: 100%;
    box-sizing: border-box;
  }
  .status-tag {
    position: absolute;
    right: 16px;
    top: 15px;
  }
}
</style>
