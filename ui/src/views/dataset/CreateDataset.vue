<template>
  <LayoutContainer :header="isCreate ? '创建知识库' : '上传文档'" class="create-dataset">
    <template #backButton>
      <back-button @click="back"></back-button>
    </template>
    <!-- <template #header>
      <el-steps :active="active" finish-status="success" align-center class="create-dataset__steps">
        <el-step v-for="(item, index) in steps" :key="index">
          <template #icon>
            <div class="app-step flex align-center">
              <div class="el-step__icon is-text">
                <div class="el-step__icon-inner">
                  <el-icon v-if="active == index + 1" style="margin-top: 1px"><Select /></el-icon>
                  <span v-else> {{ index + 1 }}</span>
                </div>
              </div>
              <span class="ml-4">{{ item.name }}</span>
            </div>
          </template>
        </el-step>
      </el-steps>
    </template> -->
    <div class="create-dataset__main flex" v-loading="loading">
      <div class="create-dataset__component main-calc-height">
        <template v-if="active === 0">
          <StepFirst ref="StepFirstRef" />
        </template>
        <template v-else-if="active === 1">
          <StepSecond ref="StepSecondRef" />
        </template>
        <template v-else-if="active === 2">
          <ResultSuccess :data="successInfo" />
        </template>
      </div>
    </div>
    <div class="create-dataset__footer text-right border-t" v-if="active !== 2">
      <el-button @click="router.go(-1)" :disabled="loading">取消</el-button>
      <el-button @click="prev" v-if="active === 1" :disabled="loading">上一步</el-button>
      <el-button
        @click="next"
        type="primary"
        v-if="active === 0"
        :disabled="loading || StepFirstRef?.loading"
      >
        创建并导入
      </el-button>
      <el-button @click="submit" type="primary" v-if="active === 1" :disabled="loading">
        开始导入
      </el-button>
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import StepFirst from './step/StepFirst.vue'
import StepSecond from './step/StepSecond.vue'
import ResultSuccess from './step/ResultSuccess.vue'
import datasetApi from '@/api/dataset'
import type { datasetData } from '@/api/type/dataset'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

import useStore from '@/stores'
const { dataset, document } = useStore()
const baseInfo = computed(() => dataset.baseInfo)
const webInfo = computed(() => dataset.webInfo)
const documentsFiles = computed(() => dataset.documentsFiles)

const router = useRouter()
const route = useRoute()
const {
  params: { type },
  query: { id } // id为datasetID，有id的是上传文档
} = route
const isCreate = type === 'create'
// const steps = [
//   {
//     ref: 'StepFirstRef',
//     name: '上传文档',
//     component: StepFirst
//   },
//   {
//     ref: 'StepSecondRef',
//     name: '设置分段规则',
//     component: StepSecond
//   }
// ]

const StepFirstRef = ref()
const StepSecondRef = ref()

const loading = ref(false)
const disabled = ref(false)
const active = ref(0)
const successInfo = ref<any>(null)

async function next() {
  disabled.value = true
  if (await StepFirstRef.value?.onSubmit()) {
    if (active.value++ > 2) active.value = 0
  } else {
    disabled.value = false
  }
}
const prev = () => {
  active.value = 0
}

function clearStore() {
  dataset.saveBaseInfo(null)
  dataset.saveWebInfo(null)
  dataset.saveDocumentsFile([])
}
function submit() {
  loading.value = true
  const documents = [] as any
  StepSecondRef.value?.paragraphList.map((item: any) => {
    documents.push({
      name: item.name,
      paragraphs: item.content
    })
  })
  const obj = { ...baseInfo.value, documents } as datasetData
  if (id) {
    // 上传文档
    document
      .asyncPostDocument(id as string, documents)
      .then(() => {
        MsgSuccess('提交成功')
        clearStore()
        router.push({ path: `/dataset/${id}/document` })
      })
      .catch(() => {
        loading.value = false
      })
  } else {
    datasetApi.postDateset(obj, loading).then((res) => {
      successInfo.value = res.data
      active.value = 2
      clearStore()
    })
  }
}
function back() {
  if (baseInfo.value || webInfo.value || documentsFiles.value?.length > 0) {
    MsgConfirm(`提示`, `当前的更改尚未保存，确认退出吗?`, {
      confirmButtonText: '确认',
      type: 'warning'
    })
      .then(() => {
        router.go(-1)
        clearStore()
      })
      .catch(() => {})
  } else {
    router.go(-1)
  }
}
onUnmounted(() => {
  clearStore()
})
</script>
<style lang="scss" scoped>
.create-dataset {
  &__steps {
    min-width: 450px;
    max-width: 800px;
    width: 80%;
    margin: 0 auto;
    padding-right: 60px;

    :deep(.el-step__line) {
      left: 64% !important;
      right: -33% !important;
    }
  }

  &__component {
    width: 100%;
    margin: 0 auto;
    overflow: hidden;
  }
  &__footer {
    padding: 16px 24px;
    position: fixed;
    bottom: 0;
    left: 0;
    background: #ffffff;
    width: 100%;
    box-sizing: border-box;
  }
}
</style>
