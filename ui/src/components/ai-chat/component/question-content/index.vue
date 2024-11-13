<template>
  <!-- 问题内容 -->
  <div class="item-content mb-16 lighter">
    <div class="avatar">
      <el-image
        v-if="application.user_avatar"
        :src="application.user_avatar"
        alt=""
        fit="cover"
        style="width: 30px; height: 30px; display: block"
      />
      <AppAvatar v-else>
        <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
      </AppAvatar>
    </div>
    <div class="content">
      <div class="text break-all pre-wrap">
        {{ chatRecord.problem_text }}
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { type chatType } from '@/api/type/application'
defineProps<{
  application: any
  chatRecord: chatType
}>()
</script>
<style lang="scss" scoped>
.ai-chat {
  &__content {
    padding-top: 0;
    box-sizing: border-box;

    .avatar {
      float: left;
    }

    .content {
      padding-left: var(--padding-left);

      :deep(ol) {
        margin-left: 16px !important;
      }
    }

    .text {
      padding: 6px 0;
    }

    .problem-button {
      width: 100%;
      border: none;
      border-radius: 8px;
      background: var(--app-layout-bg-color);
      height: 46px;
      padding: 0 12px;
      line-height: 46px;
      box-sizing: border-box;
      color: var(--el-text-color-regular);
      -webkit-line-clamp: 1;
      word-break: break-all;

      &:hover {
        background: var(--el-color-primary-light-9);
      }

      &.disabled {
        &:hover {
          background: var(--app-layout-bg-color);
        }
      }

      .el-icon {
        color: var(--el-color-primary);
      }
    }
  }
}
</style>
