<script setup lang="ts">
import { datetimeFormat } from '@/utils/time'

defineOptions({ name: 'WorkflowViewLayout' })

withDefaults(
  defineProps<{
    loading?: boolean
    title?: string
    saveTime?: Date | string
  }>(),
  { loading: false },
)

const emit = defineEmits<{ back: [] }>()

defineSlots<{
  actions(): unknown
  default(): unknown
}>()
</script>

<template>
  <main v-loading="loading" class="flex h-screen w-screen flex-col overflow-hidden">
    <header class="h-header flex-between shrink-0 gap-3 border-b bg-white px-6">
      <div class="flex min-w-0 items-center gap-3">
        <el-button text class="-ml-3" aria-label="返回" @click="emit('back')">
          <MkIcon name="icon_left_outlined" :size="18" />
        </el-button>
        <h4 class="max-w-[300px] truncate" :title="title">
          {{ title }}
        </h4>
        <span v-if="saveTime" class="shrink-0 text-sm text-N600"> 保存于 {{ datetimeFormat(saveTime) }} </span>
      </div>

      <div class="flex shrink-0 items-center gap-3">
        <slot name="actions" />
      </div>
    </header>

    <slot />
  </main>
</template>
