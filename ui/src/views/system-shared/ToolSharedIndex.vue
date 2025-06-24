<template>
  <div class="tool-shared">
    <ToolListContainer>
      <template #header>
        <el-breadcrumb separator-icon="ArrowRight">
          <el-breadcrumb-item>{{ t('views.system.shared.shared_resources') }}</el-breadcrumb-item>
          <el-breadcrumb-item>
            {{ t('views.tool.title') }}
          </el-breadcrumb-item>
        </el-breadcrumb>
      </template>
    </ToolListContainer>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, computed } from 'vue'

import ToolListContainer from '@/views/tool/component/ToolListContainer.vue'

import { t } from '@/locales'

onMounted(() => {})
</script>

<style lang="scss" scoped>
.tool-shared {
  padding-left: 8px;
  .shared-header {
    color: #646a73;
    font-weight: 400;
    font-size: 14px;
    line-height: 22px;
    display: flex;
    align-items: center;

    :deep(.el-icon i) {
      height: 12px;
    }

    .sub-title {
      color: #1f2329;
    }
  }
}
</style>
