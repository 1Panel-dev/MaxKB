<script setup lang="ts">
import { datetimeFormat } from '@/utils/time'

defineOptions({ name: 'WorkflowViewLayout' })

withDefaults(
  defineProps<{
    loading?: boolean
    title?: string
    saveTime?: Date | string
    historyVisible?: boolean
    canRestoreVersion?: boolean
  }>(),
  { loading: false },
)

const emit = defineEmits<{ back: []; restoreVersion: [] }>()

defineSlots<{
  icon(): unknown
  actions(): unknown
  default(): unknown
}>()
</script>

<template>
  <main v-loading="loading" class="flex h-screen w-screen flex-col overflow-hidden">
    <header class="h-header flex-between shrink-0 gap-3 border-b bg-white px-5">
      <div class="flex min-w-0 items-center gap-3">
        <!-- 返回资源页面 -->
        <el-button text @click="emit('back')">
          <MkIcon name="icon_arrow-left_outlined" :size="20" />
        </el-button>
        <slot name="icon" />
        <h4 class="max-w-[300px] truncate" :title="title">
          {{ title }}
        </h4>
        <el-divider direction="vertical" />
        <span v-if="saveTime" class="shrink-0 text-sm text-N600">保存时间：{{ datetimeFormat(saveTime) }} </span>
      </div>

      <div class="flex shrink-0 items-center">
        <!-- 恢复选中的历史版本 -->
        <el-button v-if="historyVisible" type="primary" :disabled="!canRestoreVersion" @click="emit('restoreVersion')"> 恢复此版本 </el-button>
        <!-- 保留操作入口实例，避免切换头部时卸载其发布历史面板。 -->
        <div v-show="!historyVisible" class="flex items-center">
          <slot name="actions" />
        </div>
      </div>
    </header>

    <slot />
  </main>
</template>
