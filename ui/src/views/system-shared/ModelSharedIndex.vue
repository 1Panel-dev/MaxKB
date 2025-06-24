<template>
  <ContentContainer>
    <template #header>
      <el-breadcrumb separator-icon="ArrowRight">
        <el-breadcrumb-item>{{ t('views.system.shared.shared_resources') }}</el-breadcrumb-item>
        <el-breadcrumb-item>
          <h5 class="ml-4 color-text-primary">{{ t('views.model.title') }}</h5>
        </el-breadcrumb-item>
      </el-breadcrumb>
    </template>
    <el-card style="--el-card-padding: 0">
      <modelListContainer />
    </el-card>
  </ContentContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, computed } from 'vue'
import { t } from '@/locales'
import modelListContainer from '@/views/model/index.vue'

onMounted(() => {})
</script>

<style lang="scss" scoped></style>
