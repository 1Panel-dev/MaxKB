<script setup lang="ts">
import FileUploadCard from '@/components/mk-drag-upload/FileUploadCard.vue'
import type { UploadCardFile } from '@/components/mk-drag-upload/types'

defineOptions({ name: 'MessageInputFileUploadCard' })
withDefaults(defineProps<{ file: UploadCardFile; percentage?: number; disabled?: boolean }>(), { disabled: false })
const emit = defineEmits<{ remove: [] }>()
</script>

<template>
  <div class="group relative">
    <FileUploadCard :file="file" :percentage="percentage" :disabled="disabled" :show-remove="false" class="rounded-lg!" />
    <!-- 删除已选附件 -->
    <button
      type="button"
      class="group-hover-visible mk-remove-button disabled:cursor-not-allowed"
      title="删除文件"
      :disabled="disabled"
      @click.stop="emit('remove')"
    >
      <MkIcon name="icon_close_bold_outlined" class="text-white!" :size="6" />
    </button>
  </div>
</template>
