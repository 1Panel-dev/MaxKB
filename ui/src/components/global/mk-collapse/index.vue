<script setup lang="ts">
import { CaretBottom } from '@element-plus/icons-vue'

/*  目前折叠面板仅仅是基础功能。后期会增加 自定义插槽*/

defineOptions({ name: 'MkCollapse' })

defineProps<{
  title: string
}>()

const expanded = defineModel<boolean>({ default: true })
</script>

<template>
  <section>
    <div
      class="flex w-full cursor-pointer items-center gap-2 py-2 text-left text-N500"
      @click="expanded = !expanded"
    >
      <MkIcon
        :icon="CaretBottom"
        :size="14"
        class="transition-transform"
        :class="{ '-rotate-90': !expanded }"
      />
      <span>{{ title }}</span>
    </div>
    <el-collapse-transition>
      <div v-if="expanded">
        <slot />
      </div>
    </el-collapse-transition>
  </section>
</template>
