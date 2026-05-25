<template>
  <div class="home p-16">
    <el-scrollbar>
      <div class="home-calc-height p-8 pt-0">
        <el-card style="--el-card-padding: 24px">
          <h4 class="mb-16">
            {{ $t('layout.home.quickCreate') }}
          </h4>
          <QuickCreate />
        </el-card>

        <el-card style="--el-card-padding: 24px" class="mt-16">
          <h4 class="mb-16">
            {{ $t('layout.home.resource') }}
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
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, shallowRef, nextTick } from 'vue'
import { useRoute } from 'vue-router'

import StatisticsCharts from './component/StatisticsCharts.vue'
import QuickCreate from './component/QuickCreate.vue'
import ResourceAggregation from './component/ResourceAggregation.vue'
import Ranking from './component/Ranking.vue'

import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

const route = useRoute()
const {
  params: { id },
} = route as any

const detail = ref<any>(null)

const loading = ref(false)

const statisticsLoading = ref(false)
const statisticsData = ref([])
const tokenUsage = ref([])
const topQuestions = ref([])

const apiInputParams = ref([])

function getDetail() {
  loadSharedApi({ type: 'application', systemType: apiType.value })
    .getApplicationDetail(id, loading)
    .then((res: any) => {
      detail.value = res.data
      detail.value.work_flow?.nodes
        ?.filter((v: any) => v.id === 'base-node')
        .map((v: any) => {
          apiInputParams.value = v.properties.api_input_field_list
            ? v.properties.api_input_field_list.map((v: any) => {
                return {
                  name: v.variable,
                  value: v.default_value,
                }
              })
            : v.properties.input_field_list
              ? v.properties.input_field_list
                  .filter((v: any) => v.assignment_method === 'api_input')
                  .map((v: any) => {
                    return {
                      name: v.variable,
                      value: v.default_value,
                    }
                  })
              : []
        })
    })
}

onMounted(() => {
  // getDetail()
  // changeDayHandle(history_day.value)
})
</script>
<style lang="scss" scoped>
.home {
  max-width: 1280px;
  margin: 0 auto;
  .home-calc-height {
    height: calc(var(--app-main-height) + 52px);
    box-sizing: border-box;
  }
}
</style>
