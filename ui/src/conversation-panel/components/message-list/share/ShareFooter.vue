<script setup lang="ts">
import { computed, inject, onBeforeUnmount } from 'vue'
import { SHARE_PANEL_KEY } from '../../../main/share-panel/index'
import { useConversationListStore } from '../../../left-sidebar/conversation-list/index'

defineOptions({ name: 'ShareFooter' })

const props = defineProps<{ recordIds: string[] }>()
const selectedRecordIds = defineModel<string[]>({ required: true })
const sharePanel = inject(SHARE_PANEL_KEY, null)
const { switchShared } = useConversationListStore()

// 全选与数量仅统计当前列表中的可分享记录。
const selectedIds = computed(() => props.recordIds.filter((recordId) => selectedRecordIds.value.includes(recordId)))
const selectedCount = computed(() => selectedIds.value.length)
const totalCount = computed(() => props.recordIds.length)
const allSelected = computed(() => totalCount.value > 0 && selectedCount.value === totalCount.value)
const sharing = computed(() => Boolean(sharePanel?.sharing.value))
const selectAll = (checked: boolean | string | number) => {
  if (sharing.value) return
  selectedRecordIds.value = checked ? [...props.recordIds] : []
}

// 创建链接成功后退出，失败时保留选择供重试。
const cancelShare = () => {
  switchShared(false)
  sharePanel?.close()
}
const copyShareLink = () => {
  if (!sharePanel || !selectedCount.value || sharing.value) return
  void sharePanel
    .share(selectedIds.value)
    .then(cancelShare)
    .catch(() => {})
}
onBeforeUnmount(() => {
  selectedRecordIds.value = []
  switchShared(false)
})
</script>

<template>
  <footer class="shrink-0 border-t">
    <div class="mk-conversation-content flex-between gap-3 p-4">
      <!-- 全选已加载的可分享问答 -->
      <el-checkbox
        :model-value="allSelected"
        :indeterminate="selectedCount > 0 && !allSelected"
        :disabled="!totalCount || sharing"
        @change="selectAll($event)"
      >
        已选 {{ selectedCount }}/{{ totalCount }}
      </el-checkbox>
      <div>
        <!-- 退出分享选择 -->
        <el-button plain :disabled="sharing" @click="cancelShare()">取消</el-button>
        <!-- 创建并复制分享链接 -->
        <el-button type="primary" :disabled="!selectedCount || !sharePanel" :loading="sharing" @click="copyShareLink()">复制链接</el-button>
      </div>
    </div>
  </footer>
</template>
