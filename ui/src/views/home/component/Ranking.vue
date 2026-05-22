<template>
  <el-skeleton :loading="loading" animated>
    <el-row :gutter="16">
      <el-col :xs="12" :sm="12" :md="12" :lg="8" :xl="8" class="mb-16">
        <el-card shadow="never" style="--el-card-padding: 24px">
          <div class="flex-between">
            <h4>
              Tokens
              {{ $t('layout.home.consume') }}
              Top
              {{ $t('views.application.title') }}
            </h4>
            <el-button link class="flex align-center lighter">
              <span class="mr-4"> {{ $t('common.detail') }}</span>
              <el-icon>
                <ArrowRight />
              </el-icon>
            </el-button>
          </div>
          <template v-for="(item, index) in tokensRankding" :key="index">
            <div class="flex-between mt-24">
              <div class="flex align-center">
                <span class="rank" :class="'rank-' + (index + 1)"> {{ index + 1 }}</span>
                <div class="ml-12">
                  <p>{{ item?.name }}</p>
                  <p class="color-secondary font-small lighter">
                    {{ $t('layout.home.chat') }} {{ numberFormat(item?.chat_record_count || 0) }}
                    {{ $t('views.system.time') }} <el-divider direction="vertical" />{{
                      $t('layout.home.average‌')
                    }}
                    {{ numberFormat(item?.total_tokens / item?.chat_record_count || 0) }} tokens
                  </p>
                </div>
              </div>
              <div class="text-right" style="width: 100px">
                <el-progress :percentage="0" :show-text="false" />
                <p class="color-secondary mt-4">{{ numberFormat(item?.total_tokens || 0) }}</p>
              </div>
            </div>
          </template>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="12" :lg="8" :xl="8" class="mb-16">
        <el-card shadow="never" style="--el-card-padding: 24px">
          <div class="flex-between">
            <h4>
              {{ $t('views.applicationOverview.monitor.charts.queryCount') }}
              Top
              {{ $t('views.application.title') }}
            </h4>
            <el-button link class="flex align-center lighter">
              <span class="mr-4"> {{ $t('common.detail') }}</span>
              <el-icon>
                <ArrowRight />
              </el-icon>
            </el-button>
          </div>
          <template v-for="(item, index) in questionRanking" :key="index">
            <div class="flex-between mt-24">
              <div class="flex align-center">
                <span class="rank" :class="'rank-' + (index + 1)"> {{ index + 1 }}</span>
                <div class="ml-12">
                  <p>{{ item?.name }}</p>
                  <p class="color-secondary font-small lighter">
                    {{ $t('layout.home.activeUsers') }}
                    {{ numberFormat(item?.chat_user_count || 0) }}
                    <el-divider direction="vertical" />{{ $t('layout.home.average‌') }}
                    {{
                      item?.chat_record_count / item?.chat_user_count > 1
                        ? numberFormat(item?.chat_record_count / item?.chat_user_count || 0)
                        : (item?.chat_record_count / item?.chat_user_count).toFixed(1)
                    }}
                    {{ $t('layout.home.wheel') }}/{{ $t('layout.home.person') }}
                  </p>
                </div>
              </div>
              <div class="text-right" style="width: 100px">
                <el-progress :percentage="0" :show-text="false" />
                <p class="color-secondary mt-4">{{ numberFormat(item?.chat_record_count || 0) }}</p>
              </div>
            </div>
          </template>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="12" :lg="8" :xl="8" class="mb-16">
        <el-card shadow="never" style="--el-card-padding: 24px">
          <div class="flex-between">
            <h4>
              Tokens
              {{ $t('layout.home.consume') }}
              Top
              {{ $t('views.chatLog.table.user') }}
            </h4>
            <el-button link class="flex align-center lighter">
              <span class="mr-4"> {{ $t('common.detail') }}</span>
              <el-icon>
                <ArrowRight />
              </el-icon>
            </el-button>
          </div>
          <template v-for="(item, index) in userTokensRanking" :key="index">
            <div class="flex-between mt-24">
              <div class="flex align-center">
                <span class="rank" :class="'rank-' + (index + 1)"> {{ index + 1 }}</span>
                <div class="ml-12">
                  <p>{{ item?.name }}</p>
                  <p class="color-secondary font-small lighter">
                    {{ $t('layout.home.questions') }}
                    {{ numberFormat(item?.chat_user_count || 0) }}
                    {{ $t('views.system.time') }}
                    <el-divider direction="vertical" />{{ $t('layout.home.average‌') }}
                    {{}}
                  </p>
                </div>
              </div>
              <div class="text-right" style="width: 100px">
                <el-progress :percentage="0" :show-text="false" />
                <p class="color-secondary mt-4">{{ numberFormat(item?.chat_record_count || 0) }}</p>
              </div>
            </div>
          </template>
        </el-card>
      </el-col>
    </el-row>
  </el-skeleton>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import homeApi from '@/api/home-page/home'
import { numberFormat } from '@/utils/common'
const loading = ref(true)
const tokensRankding = ref<any[]>([])
const questionRanking = ref<any[]>()
const userTokensRanking = ref<any[]>()
const paginationConfig = reactive({
  current_page: 1,
  page_size: 5,
  total: 0,
})

function getDetail() {
  homeApi.getTokensRanking(paginationConfig, loading).then((res: any) => {
    tokensRankding.value = res.data?.records
  })
  homeApi.getQuestionsRanking(paginationConfig, loading).then((res: any) => {
    questionRanking.value = res.data?.records
  })
  homeApi.getUserTokensRanking(paginationConfig, loading).then((res: any) => {
    userTokensRanking.value = res.data?.records
  })
}
onMounted(() => {
  getDetail()
})
</script>
<style lang="scss" scoped>
.rank {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500px;
  border: 2px solid #ffffff;
}
.rank-1 {
  color: #c85719;
  background: linear-gradient(180deg, #fee4b1 0%, #feca88 100%);
  border-color: #ffe89d;
}
.rank-2 {
  color: #2b5fd9;
  background: linear-gradient(180deg, #c6d7ff 0%, #b6d2f7 100%);
  border-color: #d6e2ff;
}
.rank-3 {
  color: #cc710a;
  background: linear-gradient(180deg, #ffe1cf 0%, #f4c5af 100%);
  border-color: #ffe7cc;
}
</style>
