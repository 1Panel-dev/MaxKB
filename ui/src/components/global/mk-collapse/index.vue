<script setup lang="ts">
import { CaretBottom } from '@element-plus/icons-vue'
import { ref, type HTMLAttributes } from 'vue'

defineOptions({ name: 'MkCollapse' })

const props = withDefaults(
  defineProps<{
    defaultExpanded?: boolean
    title?: string
    triggerClass?: HTMLAttributes['class']
    triggerStyle?: HTMLAttributes['style']
  }>(),
  {
    defaultExpanded: true,
  },
)

defineSlots<{
  label(): unknown
  default(): unknown
}>()

const expanded = ref(props.defaultExpanded)
</script>

<template>
  <section>
    <div class="py-2" :class="triggerClass" :style="triggerStyle" @click="expanded = !expanded">
      <div class="flex w-full cursor-pointer items-center gap-2 text-left">
        <MkIcon
          :icon="CaretBottom"
          :size="14"
          class="transition-transform text-N600"
          :class="{ '-rotate-90': !expanded }"
        />
        <slot name="label">
          <span>{{ title }}</span>
        </slot>
      </div>
    </div>
    <el-collapse-transition>
      <div v-if="expanded">
        <slot />
      </div>
    </el-collapse-transition>
  </section>
</template>
