<script setup lang="ts">
import { onBeforeUnmount } from 'vue'
import { useShareLinkStoreOptional } from './index'

defineOptions({ name: 'ShareFooter' })

const shareLink = useShareLinkStoreOptional()
// 消息列表卸载（切换会话等）时退出分享态
onBeforeUnmount(() => shareLink?.exitShare())
</script>

<template>
  <footer v-if="shareLink" class="shrink-0 border-t">
    <div class="mk-conversation-content flex-between gap-3 p-4">
      <!-- 全选已加载的可分享问答 -->
      <el-checkbox
        :model-value="shareLink.allSelected.value"
        :indeterminate="shareLink.partiallySelected.value"
        :disabled="!shareLink.totalCount.value || shareLink.sharing.value"
        @change="shareLink.selectAll"
      >
        已选 {{ shareLink.selectedCount.value }}/{{ shareLink.totalCount.value }}
      </el-checkbox>
      <div>
        <!-- 退出分享选择 -->
        <el-button plain :disabled="shareLink.sharing.value" @click="shareLink.exitShare()">取消</el-button>
        <!-- 创建并复制分享链接 -->
        <el-button type="primary" :disabled="!shareLink.selectedCount.value" :loading="shareLink.sharing.value" @click="shareLink.copyShareLink()">
          复制链接
        </el-button>
      </div>
    </div>
  </footer>
</template>
