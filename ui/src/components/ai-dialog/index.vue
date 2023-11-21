<template>
  <div class="ai-dialog">
    <el-scrollbar>
      <div class="ai-dialog__content flex">
        <AppAvatar class="avatar-gradient">
          <img src="@/assets/icon_robot.svg" style="width: 54%" alt="" />
        </AppAvatar>
        <AppAvatar>
          <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
        </AppAvatar>
        <div class="ml-8 w-full">
          <el-card shadow="always" class="dialog-card">
            <h4>您好，我是 MaxKB 智能小助手</h4>
            <div class="mt-4">
              <el-text type="info">回答用户提出的 MaxKB 产品使用问题</el-text>
            </div>
          </el-card>
          <el-card shadow="always" class="dialog-card mt-12">
            <h4>您可以尝试输入以下问题：</h4>
            <div class="mt-8">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-button icon="EditPen" class="problem-button w-full">
                    DataEase支持哪些类型的数据源？
                  </el-button>
                </el-col>
                <el-col :span="12">
                  <el-button icon="EditPen" class="problem-button w-full">
                    DataEase支持哪些类型的数据源？
                  </el-button>
                </el-col>
              </el-row>
            </div>
          </el-card>

          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
          <el-card shadow="always" class="dialog-card mt-12"> XXXXXXXXX </el-card>
        </div>
      </div>
    </el-scrollbar>
    <div class="ai-dialog__textarea flex">
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
  // min-height: 400px;
  // height: 100%;
  height: calc(100% - 10px);
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  &__content {
    flex: 1;
    .problem-button {
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
  .dialog-card {
    border: none;
  }
  &__textarea {
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
</style>
