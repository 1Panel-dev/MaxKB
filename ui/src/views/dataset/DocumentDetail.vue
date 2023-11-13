<template>
  <LayoutContainer :header="documentDetail?.name" back-to="-1" class="document-detail">
    <template #header>
      <div class="document-detail__header">
        <el-button @click="addParagraph" type="primary" :disabled="loading"> 添加分段 </el-button>
      </div>
    </template>
    <div class="document-detail__main p-16">
      <div class="flex-between p-8">
        <span>{{ paragraphDetail.length }} 段落</span>
        <el-input
          v-model="search"
          placeholder="搜索"
          class="input-with-select"
          style="width: 260px"
        >
          <template #prepend>
            <el-select v-model="searchType" placeholder="Select" style="width: 80px">
              <el-option label="标题" value="title" />
              <el-option label="内容" value="content" />
            </el-select>
          </template>
        </el-input>
      </div>
      <el-scrollbar>
        <div class="document-detail-height" v-loading="loading">
          <el-row>
            <el-col
              :xs="24"
              :sm="12"
              :md="8"
              :lg="6"
              :xl="4"
              v-for="(item, index) in paragraphDetail"
              :key="index"
              class="p-8"
            >
              <CardBox
                shadow="hover"
                :title="item.title"
                :description="item.content"
                class="document-card cursor"
                :class="item.is_active ? '' : 'disabled'"
                :showIcon="false"
                @click="editParagraph(item)"
              >
                <div class="active-button">
                  <el-switch v-model="item.is_active" @change="changeState($event, item)" />
                </div>

                <template #footer>
                  <div class="footer-content flex-between">
                    <span> {{ numberFormat(item?.content.length) || 0 }} 个 字符 </span>
                    <el-tooltip effect="dark" content="删除" placement="top">
                      <el-button text @click.stop="deleteParagraph(item)" class="delete-button">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </el-tooltip>
                  </div>
                </template>
              </CardBox>
            </el-col>
          </el-row>
        </div>
      </el-scrollbar>
    </div>
    <ParagraphDialog ref="ParagraphDialogRef" :title="title" />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import datasetApi from '@/api/dataset'
import ParagraphDialog from './component/ParagraphDialog.vue'
import { numberFormat } from '@/utils/utils'
import { MsgSuccess, MsgConfirm } from '@/utils/message'

const router = useRouter()
const route = useRoute()
const {
  params: { datasetId, documentId }
} = route as any

const ParagraphDialogRef = ref()
const loading = ref(false)
const documentDetail = ref<any>({})
const paragraphDetail = ref<any[]>([])
const title = ref('')
const search = ref('')
const searchType = ref('title')

function changeState(bool: Boolean, row: any) {
  const obj = {
    is_active: bool
  }
  loading.value = true
  datasetApi
    .putParagraph(datasetId, documentId, row.id, obj)
    .then((res) => {
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function deleteParagraph(row: any) {
  MsgConfirm(`是否删除段落：${row.title} ?`, `删除后无法恢复，请谨慎操作。`, {
    confirmButtonText: '删除',
    confirmButtonClass: 'danger'
  })
    .then(() => {
      loading.value = true
      datasetApi
        .delParagraph(datasetId, documentId, row.id)
        .then(() => {
          MsgSuccess('删除成功')
          getParagraphDetail()
        })
        .catch(() => {
          loading.value = false
        })
    })
    .catch(() => {})
}

function addParagraph() {
  title.value = '添加分段'
  ParagraphDialogRef.value.open()
}
function editParagraph(row: any) { 
  title.value = '分段详情'
  ParagraphDialogRef.value.open(row)
}

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
.document-detail {
  &__header {
    position: absolute;
    right: calc(var(--app-base-px) * 3);
  }

  .document-detail-height {
    height: calc(var(--app-main-height) - 75px);
  }
  .document-card {
    height: 210px;
    background: var(--app-layout-bg-color);
    border: 1px solid var(--app-layout-bg-color);
    &:hover {
      background: #ffffff;
      border: 1px solid var(--el-border-color);
    }
    &.disabled {
      background: var(--app-layout-bg-color);
      border: 1px solid var(--app-layout-bg-color);
      :deep(.description) {
        color: var(--app-border-color-dark);
      }
      :deep(.title) {
        color: var(--app-border-color-dark);
      }
    }
    :deep(.description) {
      -webkit-line-clamp: 5 !important;
      height: 110px;
    }
    .active-button {
      position: absolute;
      right: 16px;
      top: 16px;
    }
  }
}
</style>
