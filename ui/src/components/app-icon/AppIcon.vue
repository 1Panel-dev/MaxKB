<template>
  <component
    v-if="isIconfont"
    :is="
      Object.keys(iconMap).includes(iconName)
        ? iconMap[iconName].iconReader()
        : iconMap['app-404'].iconReader()
    "
    class="el-icon app-icon"
  >
  </component>
  <el-icon v-else-if="iconName">
    <component :is="iconName" />
  </el-icon>
</template>
<script setup lang="ts">
import { iconMap } from './index'
import { computed } from 'vue'
defineOptions({ name: 'AppIcon' })
const props = withDefaults(
  defineProps<{
    iconName?: string
  }>(),
  {
    iconName: 'app-404',
  },
)

const isIconfont = computed(() => props.iconName?.includes('app-'))
</script>

<style lang="scss" scoped></style>
