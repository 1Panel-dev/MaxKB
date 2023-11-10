<template>
  <LayoutContainer :header="documentDetail?.name" back-to="-1" class="dataset-detail">
    <template #header>
      <!-- <el-steps :active="active" finish-status="success" align-center class="create-dataset__steps">
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
      </el-steps> -->
    </template>
    <div class="dataset-detail__main main-calc-height p-24">
      <el-row :gutter="15">
        <el-col
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
          :xl="4"
          v-for="(item, index) in paragraphDetail"
          :key="index"
          class="mt-8"
        >
          <CardBox
            shadow="hover"
            :title="item.title"
            :description="item.content"
            class="cursor"
            :showIcon="false"
          >
            <!-- <template #footer>
              <div class="footer-content">
                <span class="bold">{{ item?.document_count || 0 }}</span>
                文档<el-divider direction="vertical" />
                <span class="bold">{{ numberFormat(item?.char_length) || 0 }}</span>
                字符<el-divider direction="vertical" />
                <span class="bold">{{ item?.char_length || 0 }}</span>
                关联应用
              </div>
            </template> -->
          </CardBox>
        </el-col>
      </el-row>
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import datasetApi from '@/api/dataset'

const router = useRouter()
const route = useRoute()
const {
  params: { datasetId, documentId }
} = route as any

const loading = ref(false)
const documentDetail = ref<any>({})
const paragraphDetail = ref<any[]>([])

function getDetail() {
  loading.value = true
  datasetApi
    .getDocumentDetail(datasetId, documentId)
    .then((res) => {
      documentDetail.value = res.data
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function getParagraphDetail() {
  loading.value = true
  datasetApi
    .getParagraph(datasetId, documentId)
    .then((res) => {
      paragraphDetail.value = res.data
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

onMounted(() => {
  getDetail()
  getParagraphDetail()
})
</script>
<style lang="scss" scoped>
.dataset-detail {
  &__main{
    box-sizing: border-box;
  }
}
</style>
