<template>
  <el-scrollbar>
    <div class="home p-16">
      <el-card style="--el-card-padding: 24px" class="home-card">
        <h4 class="mb-16">
          {{ $t('home.quickCreate') }}
        </h4>
        <QuickCreate />
      </el-card>

      <el-card style="--el-card-padding: 24px" class="mt-16 home-card">
        <h4 class="mb-16">
          {{ $t('home.resource') }}
        </h4>
        <ResourceAggregation />
      </el-card>
      <!-- 监听 -->
      <StatisticsCharts />
      <!-- 排行榜 -->
      <Ranking />

      <br />
    </div>
  </el-scrollbar>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, shallowRef, nextTick } from 'vue'
import { useRoute } from 'vue-router'

import StatisticsCharts from './component/StatisticsCharts.vue'
import QuickCreate from './component/QuickCreate.vue'
import ResourceAggregation from './component/ResourceAggregation.vue'
import Ranking from './component/Ranking.vue'

const route = useRoute()
const {
  params: { id },
} = route as any

onMounted(() => {})
</script>
<style lang="scss" scoped>
.home {
  max-width: 1280px;
  margin: 0 auto;
  height: calc(var(--app-main-height) + 74px);
  box-sizing: border-box;
}

.home-card {
  background: var(--bg-card);
  backdrop-filter: var(--blur-card);
  -webkit-backdrop-filter: var(--blur-card);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: var(--app-border-radius-large);
  box-shadow: var(--shadow-card);
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-card-hover);
  }
}

[data-theme="dark"] .home-card {
  border-color: rgba(255, 255, 255, 0.08);
}
</style>
