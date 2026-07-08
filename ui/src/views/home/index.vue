<template>
  <el-scrollbar>
    <div class="home p-16">
      <el-card style="--el-card-padding: 24px">
        <h4 class="mb-16">
          {{ $t('home.quickCreate') }}
        </h4>
        <QuickCreate />
      </el-card>

      <el-card style="--el-card-padding: 24px" class="mt-16">
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
</style>
