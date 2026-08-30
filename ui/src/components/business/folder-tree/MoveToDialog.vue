<script setup lang="ts">
import { computed, ref } from 'vue'
import type { FolderSource } from '@/api/types'
import { FOLDER_ENTRY_ID } from '@/constants'
import FolderTree from './index.vue'

defineOptions({ name: 'MoveToDialog' })

withDefaults(defineProps<{ loading?: boolean; source: FolderSource }>(), { loading: false })

const emit = defineEmits<{ submit: [targetFolderId: string] }>()

const visible = ref(false)
const selectedTargetId = ref<string>(FOLDER_ENTRY_ID.ALL)

const canSubmit = computed(() => Boolean(selectedTargetId.value) && selectedTargetId.value !== FOLDER_ENTRY_ID.ALL)

/* 移动提交 */
function handleSubmit() {
  if (!canSubmit.value) return
  emit('submit', selectedTargetId.value)
}

function open(currentFolderId = FOLDER_ENTRY_ID.ALL) {
  selectedTargetId.value = currentFolderId
  visible.value = true
}

function resetData() {
  selectedTargetId.value = FOLDER_ENTRY_ID.ALL
}

function close() {
  visible.value = false
}

defineExpose({ close, open })
</script>

<template>
  <MkDialog align-center v-model="visible" class="move-to-dialog" content-class="move-to-dialog__content" title="移动到" :show-close="!loading" @closed="resetData">
    <FolderTree v-model="selectedTargetId" class="move-to-dialog__folder-tree" :can-edit="false" :show-all="false" :show-shared="false" :source="source" />

    <template #footer>
      <el-button :disabled="loading" @click="visible = false">取消</el-button>
      <el-button type="primary" :disabled="!canSubmit" :loading="loading" @click="handleSubmit"> 确定 </el-button>
    </template>
  </MkDialog>
</template>

<style lang="scss">
.move-to-dialog {
  .move-to-dialog__content {
    display: flex;
    flex-direction: column;
    height: min(600px, calc(100vh - 272px));
    overflow: hidden;
  }

  .move-to-dialog__folder-tree {
    > div:first-child {
      padding-left: 0;
      padding-right: 0;
    }

    > div:nth-child(2) {
      overflow: hidden;
      border: var(--el-border);
      border-radius: var(--el-border-radius-base);
    }

    .mk-virtualized-tree {
      padding: calc(var(--spacing) * 2);
      padding-right: 0;
    }
  }
}
</style>
