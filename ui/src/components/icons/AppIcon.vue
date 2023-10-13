<template>
  <component
    v-if="isIconfont"
    :is="
      Object.keys(iconMap).includes(iconName)
        ? iconMap[iconName].iconReader()
        : iconMap['404'].iconReader()
    "
    class="app-icon"
  >
  </component>
  <el-icon v-else-if="iconName">
    <component :is="iconName" />
  </el-icon>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { iconMap } from '@/components/icons/index'
defineOptions({ name: 'AppIcon' })

const props = withDefaults(
  defineProps<{
    iconName?: string
  }>(),
  {
    iconName: '404'
  }
)

const isIconfont = computed(() => props.iconName?.includes('app-'))
</script>

<style lang="scss" scoped>
.app-icon {
  line-height: 1em;
  svg {
    height: 1em;
    width: 1em;
  }
}
</style>
