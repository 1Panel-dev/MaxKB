<template>
  <el-card shadow="always" class="card-box" @mouseenter="cardEnter()" @mouseleave="cardLeave()">
    <div class="card-header">
      <slot name="header">
        <div class="title flex align-center">
          <AppAvatar class="mr-10">
            <el-icon><Document /></el-icon>
          </AppAvatar>
          <h4>{{ title }}</h4>
        </div>
      </slot>
    </div>
    <div class="description mt-10">
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
import { ref, watch } from 'vue'
defineOptions({ name: 'CardBox' })
const props = defineProps({
  title: {
    type: String,
    default: '标题'
  },
  description: {
    type: String,
    default: ''
  }
})

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
  min-height: 150px;

  .description {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    overflow: hidden;
    height: 40px;
  }
  .card-footer {
    position: absolute;
    bottom: 0;
    min-height: 30px;
  }
}
</style>
