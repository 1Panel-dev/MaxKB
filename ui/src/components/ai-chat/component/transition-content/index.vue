<template>
  <!-- 问题内容 -->
  <div class="question-content item-content mb-16 lighter">
    <div class="content p-12-16 border-r-8">
      <span> {{ text }}</span
      ><span class="dotting"></span>
    </div>
    <div class="avatar ml-8" v-if="application.show_user_avatar">
      <el-image
        v-if="application.user_avatar"
        :src="application.user_avatar"
        alt=""
        fit="cover"
        style="width: 28px; height: 28px; display: block"
      />
      <AppAvatar v-else>
        <img src="@/assets/user-icon.svg" style="width: 50%" alt="" />
      </AppAvatar>
    </div>
  </div>
</template>
<script setup lang="ts">
defineProps<{
  text: string
  application: any
  type: 'log' | 'ai-chat' | 'debug-ai-chat'
}>()
</script>
<style lang="scss" scoped>
.question-content {
  display: flex;
  justify-content: flex-end;
  padding-left: var(--padding-left);
  width: 100%;
  box-sizing: border-box;

  .content {
    background: #d6e2ff;
    padding-left: 16px;
    padding-right: 16px;
  }

  .download-file {
    height: 43px;

    &:hover {
      color: var(--el-color-primary);
      border: 1px solid var(--el-color-primary);

      .download-button {
        display: block;
        text-align: center;
        line-height: 26px;
      }

      .show {
        display: none;
      }
    }

    .download-button {
      display: none;
    }
  }
  .media-file-width {
    :deep(.el-space__item) {
      min-width: 40% !important;
      flex-grow: 1;
    }
  }
  .media_2 {
    flex: 1;
  }
  .media_0 {
    flex: inherit;
  }
  .media_1 {
    width: 50%;
  }
}
@media only screen and (max-width: 768px) {
  .question-content {
    .media-file-width {
      :deep(.el-space__item) {
        min-width: 100% !important;
      }
    }
    .media_1 {
      width: 100%;
    }
  }
}
.debug-ai-chat {
  .question-content {
    .media-file-width {
      :deep(.el-space__item) {
        min-width: 100% !important;
      }
    }
    .media_1 {
      width: 100%;
    }
  }
}
</style>
