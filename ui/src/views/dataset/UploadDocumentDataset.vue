<template>
  <LayoutContainer header="上传文档" class="create-dataset">
    <template #backButton>
      <back-button @click="back"></back-button>
    </template>
    <div class="create-dataset__main flex" v-loading="loading">
      <div class="create-dataset__component main-calc-height">
        <el-scrollbar>
          <template v-if="active === 0">
            <div class="upload-document p-24">
              <!-- 上传文档 -->
              <UploadComponent ref="UploadComponentRef" />
            </div>
          </template>
          <template v-else-if="active === 1">
            <SetRules ref="SetRulesRef" />
          </template>
          <template v-else-if="active === 2">
            <ResultSuccess :data="successInfo" />
          </template>
        </el-scrollbar>
      </div>
    </div>
    <div class="create-dataset__footer text-right border-t" v-if="active !== 2">
      <el-button @click="router.go(-1)" :disabled="loading">取消</el-button>
      <el-button @click="prev" v-if="active === 1" :disabled="loading">上一步</el-button>
      <el-button @click="next" type="primary" v-if="active === 0" :disabled="loading">
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
import SetRules from './component/SetRules.vue'
import ResultSuccess from './component/ResultSuccess.vue'
import UploadComponent from './component/UploadComponent.vue'
import datasetApi from '@/api/dataset'
import documentApi from '@/api/document'
import type { datasetData } from '@/api/type/dataset'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

import useStore from '@/stores'
const { dataset, document } = useStore()
const documentsFiles = computed(() => dataset.documentsFiles)
const documentsType = computed(() => dataset.documentsType)

const router = useRouter()
const route = useRoute()
const {
  query: { id } // id为datasetID，有id的是上传文档
} = route

const SetRulesRef = ref()
const UploadComponentRef = ref()

const loading = ref(false)
const disabled = ref(false)
const active = ref(0)
const successInfo = ref<any>(null)
async function next() {
  disabled.value = true
  if (await UploadComponentRef.value.validate()) {
    if (documentsType.value === 'QA') {
      let fd = new FormData()
      documentsFiles.value.forEach((item: any) => {
        if (item?.raw) {
          fd.append('file', item?.raw)
        }
      })
      if (id) {
        // QA文档上传
        documentApi.postQADocument(id as string, fd, loading).then((res) => {
          MsgSuccess('提交成功')
          clearStore()
          router.push({ path: `/dataset/${id}/document` })
        })
      }
    } else {
      if (active.value++ > 2) active.value = 0
    }
  } else {
    disabled.value = false
  }
}
const prev = () => {
  active.value = 0
}

function clearStore() {
  dataset.saveDocumentsFile([])
  dataset.saveDocumentsType('')
}
function submit() {
  loading.value = true
  const documents = [] as any
  SetRulesRef.value?.paragraphList.map((item: any) => {
    if (!SetRulesRef.value?.checkedConnect) {
      item.content.map((v: any) => {
        delete v['problem_list']
      })
    }
    documents.push({
      name: item.name,
      paragraphs: item.content
    })
  })

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
  }
}
function back() {
  if (documentsFiles.value?.length > 0) {
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
  .upload-document {
    width: 70%;
    margin: 0 auto;
    margin-bottom: 20px;
  }
}
</style>
