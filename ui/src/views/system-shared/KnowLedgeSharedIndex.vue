<template>
  <div class="tool-shared">
    <KnowledgeListContainer>
      <template #header>
        <el-breadcrumb separator-icon="ArrowRight">
          <el-breadcrumb-item>{{ t('views.shared.shared_resources') }}</el-breadcrumb-item>
          <el-breadcrumb-item>
            <h5 class="ml-4 color-text-primary">{{ t('views.knowledge.title') }}</h5>
          </el-breadcrumb-item>
        </el-breadcrumb>
      </template>
    </KnowledgeListContainer>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, computed } from 'vue'

import KnowledgeListContainer from '@/views/knowledge/component/KnowledgeListContainer.vue'

import { t } from '@/locales'

onMounted(() => {})
</script>

<style lang="scss" scoped></style>
