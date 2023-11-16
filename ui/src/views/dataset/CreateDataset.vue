<template>
  <LayoutContainer header="创建数据集" back-to="-1" class="create-dataset">
    <template #header>
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
    </template>
    <div class="create-dataset__main flex" v-loading="loading">
      <div class="create-dataset__component main-calc-height">
        <template v-if="steps[active]?.component">
          <component :is="steps[active].component" :ref="steps[active]?.ref" />
        </template>
        <template v-else-if="active === 2">
          <el-result icon="success" title="🎉 数据集创建成功 🎉">
            <template #sub-title>
              <div class="mt-8">
                <span class="bold">{{ successInfo?.document_count || 0 }}</span>
                <el-text type="info" class="ml-4">文档</el-text>
                <el-divider direction="vertical" />
                <span class="bold">{{ successInfo?.document_list.length || 0 }}</span>
                <el-text type="info" class="ml-4">分段</el-text>
                <el-divider direction="vertical" />
                <span class="bold">{{ toThousands(successInfo?.char_length) || 0 }}</span>
                <el-text type="info" class="ml-4">字符</el-text>
              </div>
            </template>
            <template #extra>
              <el-button @click="router.push({ path: `/dataset` })">返回数据集列表</el-button>
              <el-button
                type="primary"
                @click="router.push({ path: `/dataset/${successInfo?.id}/document` })"
                >前往文档</el-button
              >
            </template>
          </el-result>
        </template>
      </div>
    </div>
    <div class="create-dataset__footer text-right border-t" v-if="active !== 2">
      <el-button @click="router.go(-1)" :disabled="loading">取 消</el-button>
      <el-button @click="prev" v-if="active === 1" :disabled="loading">上一步</el-button>
      <el-button @click="next" type="primary" v-if="active === 0" :disabled="loading"
        >下一步</el-button
      >
      <el-button @click="submit" type="primary" v-if="active === 1" :disabled="loading">
        开始导入
      </el-button>
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import StepFirst from './step/StepFirst.vue'
import StepSecond from './step/StepSecond.vue'
import datasetApi from '@/api/dataset'
import type { datasetData } from '@/api/type/dataset'
import { MsgSuccess } from '@/utils/message'
import { toThousands } from '@/utils/utils'
import useStore from '@/stores'
const { dataset } = useStore()
const baseInfo = computed(() => dataset.baseInfo)

const router = useRouter()
const route = useRoute()
const {
  query: { id }
} = route as any

const steps = [
  {
    ref: 'StepFirstRef',
    name: '上传文档',
    component: StepFirst
  },
  {
    ref: 'StepSecondRef',
    name: '设置分段规则',
    component: StepSecond
  }
]

const StepFirstRef = ref()
const StepSecondRef = ref()

const loading = ref(false)
const active = ref(0)
const successInfo = ref<any>(null)

async function next() {
  if (await StepFirstRef.value.onSubmit()) {
    if (active.value++ > 2) active.value = 0
  }
}
const prev = () => {
  active.value = 0
}

function clearStore() {
  dataset.saveBaseInfo(null)
  dataset.saveDocumentsFile([])
}
function submit() {
  loading.value = true
  const documents = [] as any[]
  StepSecondRef.value.paragraphList.map((item: any) => {
    documents.push({
      name: item.name,
      paragraphs: item.content
    })
  })
  const obj = { ...baseInfo.value, documents } as datasetData
  if (id) {
    datasetApi
      .postDocument(id, documents)
      .then((res) => {
        MsgSuccess('提交成功')
        clearStore()
        router.push({ path: `/dataset/${id}/document` })
      })
      .catch(() => {
        loading.value = false
      })
  } else {
    datasetApi
      .postDateset(obj)
      .then((res) => {
        successInfo.value = res.data
        active.value = 2
        clearStore()
        loading.value = false
      })
      .catch(() => {
        loading.value = false
      })
  }
}
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
