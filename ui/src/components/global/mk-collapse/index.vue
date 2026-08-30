<script setup lang="ts">
import { CaretBottom } from '@element-plus/icons-vue'
import { ref, type HTMLAttributes } from 'vue'

defineOptions({ name: 'MkCollapse' })

const props = withDefaults(
  defineProps<{
    defaultExpanded?: boolean
    indicatorPosition?: 'after' | 'before'
    title?: string
    triggerClass?: HTMLAttributes['class']
    triggerStyle?: HTMLAttributes['style']
  }>(),
  { defaultExpanded: true, indicatorPosition: 'before' },
)

defineSlots<{ default?: () => unknown; label?: () => unknown }>()

const expanded = ref(props.defaultExpanded)
</script>

<template>
  <section>
    <div class="py-2" :class="triggerClass" :style="triggerStyle" @click="expanded = !expanded">
      <div class="flex w-full cursor-pointer items-center gap-2 text-left">
        <MkIcon v-if="indicatorPosition === 'before'" :icon="CaretBottom" :size="14" class="transition-transform text-N600!" :class="{ '-rotate-90': !expanded }" />
        <slot name="label">
          <span>{{ title }}</span>
        </slot>

        <MkIcon v-if="indicatorPosition === 'after'" name="icon_down_outlined" :size="16" class="transition-transform text-N600!" :class="{ '-rotate-180': expanded }" />
      </div>
    </div>
    <el-collapse-transition>
      <div v-if="expanded">
        <slot />
      </div>
    </el-collapse-transition>
  </section>
</template>
