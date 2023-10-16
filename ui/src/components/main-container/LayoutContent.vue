<template>
  <el-scrollbar>
    <div class="content-container">
      <div class="content-container__header" v-if="slots.header || header">
        <slot name="header">
          <back-button :path="backPath" :name="backName" :to="backTo" v-if="showBack"></back-button>
          <span>{{ header }}</span>
        </slot>
      </div>
      <slot></slot>
    </div>
  </el-scrollbar>
</template>

<script setup>
import { computed, useSlots } from 'vue';
import BackButton from '@/components/back-button/index.vue';
defineOptions({ name: 'LayoutContent' });
const slots = useSlots();
const prop = defineProps({
  header: String,
  backPath: String,
  backName: String,
  backTo: [Object, String],
});

const showBack = computed(() => {
  const { backPath, backName, backTo } = prop;
  return backPath || backName || backTo;
});
</script>

<style lang="scss">
@use '@/styles/common/mixins.scss' as *;
@use '@/styles/common/variables.scss' as *;

.content-container {
  transition: 0.3s;
  color: var(--el-text-color-primary);
  padding: $view-padding;

  .content-container__header {
    font-weight: 500;
    padding-bottom: $view-padding;
    font-size: 20px;
    box-sizing: border-box;
    span {
      vertical-align: middle;
    }
  }
}
</style>
