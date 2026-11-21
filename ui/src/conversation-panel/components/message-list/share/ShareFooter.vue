<script setup lang="ts">
import { onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { useShareLinkStoreOptional } from './index'

defineOptions({ name: 'ShareFooter' })

const { t } = useI18n({ useScope: 'global' })
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
        {{ t('common.labels.selected') }} {{ shareLink.selectedCount.value }}/{{ shareLink.totalCount.value }}
      </el-checkbox>
      <div>
        <!-- 退出分享选择 -->
        <el-button plain :disabled="shareLink.sharing.value" @click="shareLink.exitShare()">{{ t('common.actions.cancel') }}</el-button>
        <!-- 创建并复制分享链接 -->
        <el-button type="primary" :disabled="!shareLink.selectedCount.value" :loading="shareLink.sharing.value" @click="shareLink.copyShareLink()">
          {{ t('chat.share.copy') }}
        </el-button>
      </div>
    </div>
  </footer>
</template>
