<template>
  <div class="tool-shared">
    <ToolListContainer>
      <template #header>
        <el-breadcrumb separator-icon="ArrowRight">
          <el-breadcrumb-item>{{ t('views.system.shared.shared_resources') }}</el-breadcrumb-item>
          <el-breadcrumb-item>
            <h5 class="ml-4 color-text-primary">{{ t('views.tool.title') }}</h5>
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

<style lang="scss" scoped></style>
