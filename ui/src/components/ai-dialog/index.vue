<template>
  <div class="ai-dialog p-24">
    <el-scrollbar>
      <div class="ai-dialog__content">
        <div class="avatar">
          <AppAvatar class="avatar-gradient">
            <img src="@/assets/icon_robot.svg" style="width: 54%" alt="" />
          </AppAvatar>
          <!-- <AppAvatar>
            <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
          </AppAvatar> -->
        </div>

        <div class="content">
          <el-card shadow="always" class="dialog-card">
            <h4>您好，我是 MaxKB 智能小助手</h4>
            <div class="mt-4">
              <el-text type="info">回答用户提出的 MaxKB 产品使用问题</el-text>
            </div>
          </el-card>
          <el-card shadow="always" class="dialog-card mt-12">
            <h4 class="mb-8">您可以尝试输入以下问题：</h4>
            <el-space wrap>
              <el-button icon="EditPen" class="problem-button">
                DataEase支持哪些类型的数据源？
              </el-button>
              <el-button icon="EditPen" class="problem-button">
                DataEase支持哪些类型的数据源？XXXXXXXXXXX
              </el-button>
            </el-space>
          </el-card>

          <!-- <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card> -->
        </div>
      </div>
    </el-scrollbar>
    <div class="ai-dialog__operate p-24">
      <div class="operate-textarea flex">
        <el-input
          v-model="inputValue"
          type="textarea"
          placeholder="请输入"
          :autosize="{ minRows: 1, maxRows: 8 }"
        />
        <div class="operate">
          <el-button text class="sent-button" disabled>
            <AppIcon iconName="app-send"></AppIcon>
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
const props = defineProps({
  data: {
    type: Array<any>,
    default: () => []
  }
})
const inputValue = ref('')
</script>
<style lang="scss" scoped>
.ai-dialog {
  --padding-left: 40px;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  position: relative;
  padding-right: 20px;
  padding-top: 0;
  &__content {
    width: 99%;
    padding-bottom: 96px;
    .avatar {
      float: left;
    }
    .content {
      padding-left: var(--padding-left);
    }
    .problem-button {
      width: 100%;
      border: none;
      border-radius: 8px;
      background: var(--app-layout-bg-color);
      height: 46px;
      justify-content: left;
      &:hover {
        background: var(--el-color-primary-light-9);
      }
      :deep(.el-icon) {
        color: var(--el-color-primary);
      }
    }
  }
  &__operate {
    background: #f3f7f9;
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    box-sizing: border-box;
    z-index: 10;
    padding-top: 16px;
    &:before {
      background: linear-gradient(0deg, #f3f7f9 0%, rgba(243, 247, 249, 0) 100%);
      content: '';
      position: absolute;
      width: 100%;
      top: -16px;
      left: 0;
      height: 16px;
    }
    .operate-textarea {
      box-shadow: 0px 6px 24px 0px rgba(31, 35, 41, 0.08);
      background-color: #ffffff;
      border-radius: 8px;
      border: 1px solid #ffffff;
      box-sizing: border-box;

      &:has(.el-textarea__inner:focus) {
        border: 1px solid var(--el-color-primary);
      }

      :deep(.el-textarea__inner) {
        border-radius: 8px !important;
        box-shadow: none;
        resize: none;
        padding: 12px 16px;
      }
      .operate {
        padding: 10px 12px;
        .sent-button {
          .el-icon {
            font-size: 24px;
          }
        }
      }
    }
  }
  .dialog-card {
    border: none;
  }
}
</style>
