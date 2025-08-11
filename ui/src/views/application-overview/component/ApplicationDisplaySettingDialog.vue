<template>
  <el-dialog
    :title="$t('views.application.displaySettings')"
    v-model="dialogVisible"
    width="600"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <div class="display-settings">
      <!-- 应用图标 -->
      <el-card shadow="never" class="mb-16">
        <div class="flex-between mb-8">
          <span class="setting-title">{{ $t('views.application.appIcon') }}</span>
          <el-button size="small" @click="openIconDialog">
            {{ $t('views.application.edit') }}
          </el-button>
        </div>
        <div class="preview-item">
          <el-avatar shape="square" :size="40" style="background: none">
            <img :src="resetUrl(detail?.icon, resetUrl('./favicon.ico'))" alt="" />
          </el-avatar>
        </div>
      </el-card>

      <!-- 聊天背景 -->
      <el-card shadow="never" class="mb-16">
        <div class="flex-between mb-8">
          <span class="setting-title">{{ $t('views.application.chatBackground') }}</span>
          <el-button size="small" @click="openChatBackgroundDialog">
            {{ $t('views.application.edit') }}
          </el-button>
        </div>
        <div class="preview-item">
          <div class="background-preview" :style="chatBackgroundStyle">
            <div class="preview-text">{{ $t('views.application.backgroundPreview') }}</div>
          </div>
        </div>
      </el-card>

      <!-- AI头像 -->
      <el-card shadow="never" class="mb-16">
        <div class="flex-between mb-8">
          <span class="setting-title">{{ $t('views.application.aiAvatar') }}</span>
          <el-button size="small" @click="openAvatarDialog">
            {{ $t('views.application.edit') }}
          </el-button>
        </div>
        <div class="preview-item">
          <el-avatar shape="square" :size="40" style="background: none">
            <img v-if="detail?.avatar" :src="resetUrl(detail.avatar)" alt="" />
            <img v-else :src="resetUrl('./favicon.ico')" alt="" />
          </el-avatar>
        </div>
      </el-card>

      <!-- 用户头像 -->
      <el-card shadow="never" class="mb-16">
        <div class="flex-between mb-8">
          <span class="setting-title">{{ $t('views.application.userAvatar') }}</span>
          <el-button size="small" @click="openUserAvatarDialog">
            {{ $t('views.application.edit') }}
          </el-button>
        </div>
        <div class="preview-item">
          <el-avatar shape="square" :size="40" style="background: none">
            <img v-if="detail?.user_avatar" :src="resetUrl(detail.user_avatar)" alt="" />
            <img v-else :src="resetUrl('./favicon.ico')" alt="" />
          </el-avatar>
        </div>
      </el-card>

      <!-- 浮窗图标 -->
      <el-card shadow="never" class="mb-16">
        <div class="flex-between mb-8">
          <span class="setting-title">{{ $t('views.application.floatIcon') }}</span>
          <el-button size="small" @click="openFloatIconDialog">
            {{ $t('views.application.edit') }}
          </el-button>
        </div>
        <div class="preview-item">
          <el-avatar shape="square" :size="40" style="background: none">
            <img v-if="detail?.float_icon" :src="resetUrl(detail.float_icon)" alt="" />
            <img v-else :src="resetUrl('./favicon.ico')" alt="" />
          </el-avatar>
        </div>
      </el-card>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">{{ $t('common.close') }}</el-button>
      </span>
    </template>

    <!-- 编辑对话框 -->
    <EditApplicationIconDialog ref="EditApplicationIconDialogRef" @refresh="refreshIcon" />
    <EditChatBackgroundDialog ref="EditChatBackgroundDialogRef" @refresh="refreshChatBackground" />
    <EditAIAvatarDialog ref="EditAIAvatarDialogRef" @refresh="refreshAvatar" />
    <EditUserAvatarDialog ref="EditUserAvatarDialogRef" @refresh="refreshUserAvatar" />
    <EditFloatIconDialog ref="EditFloatIconDialogRef" @refresh="refreshFloatIcon" />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { resetUrl } from '@/utils/common'
import EditApplicationIconDialog from './EditApplicationIconDialog.vue'
import EditChatBackgroundDialog from './EditChatBackgroundDialog.vue'
import EditAIAvatarDialog from './EditAIAvatarDialog.vue'
import EditUserAvatarDialog from './EditUserAvatarDialog.vue'
import EditFloatIconDialog from './EditFloatIconDialog.vue'

const emit = defineEmits(['refresh'])

const dialogVisible = ref(false)
const detail = ref<any>({})

// 编辑对话框引用
const EditApplicationIconDialogRef = ref()
const EditChatBackgroundDialogRef = ref()
const EditAIAvatarDialogRef = ref()
const EditUserAvatarDialogRef = ref()
const EditFloatIconDialogRef = ref()

const chatBackgroundStyle = computed(() => {
  if (detail.value?.chat_background) {
    return {
      backgroundImage: `url(${resetUrl(detail.value.chat_background)})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  return {}
})

const open = (data: any) => {
  detail.value = { ...data }
  dialogVisible.value = true
}

// 打开各种编辑对话框
const openIconDialog = () => {
  EditApplicationIconDialogRef.value?.open(detail.value)
}

const openChatBackgroundDialog = () => {
  EditChatBackgroundDialogRef.value?.open(detail.value)
}

const openAvatarDialog = () => {
  EditAIAvatarDialogRef.value?.open(detail.value)
}

const openUserAvatarDialog = () => {
  EditUserAvatarDialogRef.value?.open(detail.value)
}

const openFloatIconDialog = () => {
  EditFloatIconDialogRef.value?.open(detail.value)
}

// 刷新各种资源
const refreshIcon = (newIcon: string) => {
  detail.value.icon = newIcon
  emit('refresh')
}

const refreshChatBackground = (newBackground: string) => {
  detail.value.chat_background = newBackground
  emit('refresh')
}

const refreshAvatar = (newAvatar: string) => {
  detail.value.avatar = newAvatar
  emit('refresh')
}

const refreshUserAvatar = (newUserAvatar: string) => {
  detail.value.user_avatar = newUserAvatar
  emit('refresh')
}

const refreshFloatIcon = (newFloatIcon: string) => {
  detail.value.float_icon = newFloatIcon
  emit('refresh')
}

defineExpose({ open })
</script>

<style lang="scss" scoped>
.display-settings {
  max-height: 500px;
  overflow-y: auto;
}

.setting-title {
  font-weight: 500;
  color: #303133;
}

.preview-item {
  display: flex;
  align-items: center;
}

.background-preview {
  width: 120px;
  height: 80px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  position: relative;
  overflow: hidden;
}

.preview-text {
  color: #909399;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.8);
  padding: 2px 6px;
  border-radius: 4px;
}
</style>
