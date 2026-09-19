<script setup lang="ts">
import { CaretBottom } from '@element-plus/icons-vue'
import { computed, ref, type HTMLAttributes } from 'vue'

defineOptions({ name: 'MkCollapse' })

const props = withDefaults(
  defineProps<{
    defaultExpanded?: boolean
    indicatorPosition?: 'after' | 'before'
    title?: string
    trigger?: 'header' | 'indicator'
    triggerClass?: HTMLAttributes['class']
    triggerStyle?: HTMLAttributes['style']
  }>(),
  { defaultExpanded: true, indicatorPosition: 'before', trigger: 'header' },
)

defineSlots<{ default?: () => unknown; label?: () => unknown }>()

const expandedModel = defineModel<boolean>('expanded')
const localExpanded = ref(props.defaultExpanded)
const expanded = computed({
  get: () => expandedModel.value ?? localExpanded.value,
  set: (value: boolean) => {
    localExpanded.value = value
    expandedModel.value = value
  },
})
</script>

<template>
  <section>
    <div :class="triggerClass" :style="triggerStyle" @click="trigger === 'header' && (expanded = !expanded)">
      <div class="flex w-full items-center gap-2 text-left" :class="{ 'cursor-pointer': trigger === 'header' }">
        <!-- 展开或收起内容 -->
        <button
          type="button"
          class="flex-center shrink-0 cursor-pointer border-0 bg-transparent p-0"
          :class="{ 'order-last': indicatorPosition === 'after' }"
          :title="expanded ? '收起' : '展开'"
          :aria-expanded="expanded"
          @click.stop="expanded = !expanded"
        >
          <MkIcon
            v-if="indicatorPosition === 'before'"
            :icon="CaretBottom"
            :size="14"
            class="transition-transform text-N600!"
            :class="{ '-rotate-90': !expanded }"
          />
          <MkIcon v-else name="icon_down_outlined" :size="16" class="transition-transform text-N600!" :class="{ '-rotate-180': expanded }" />
        </button>
        <slot name="label">
          <span>{{ title }}</span>
        </slot>
      </div>
    </div>
    <el-collapse-transition>
      <div v-show="expanded">
        <slot />
      </div>
    </el-collapse-transition>
  </section>
</template>
