<template>
  <LayoutContainer :header="documentDetail?.name" back-to="-1" class="document-detail">
    <template #header>
      <div class="document-detail__header">
        <el-button @click="addParagraph" type="primary" :disabled="loading"> 添加分段 </el-button>
      </div>
    </template>
    <div class="document-detail__main p-16" v-loading="pageConfig.current_page === 1 && loading">
      <div class="flex-between p-8">
        <span>{{ pageConfig.total }} 段落</span>
        <el-input
          v-model="search"
          placeholder="搜索"
          class="input-with-select"
          style="width: 260px"
          @change="searchHandle"
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
        <div class="document-detail-height">
          <el-empty v-if="paragraphDetail.length == 0" description="暂无数据" />
          <el-row v-else v-infinite-scroll="loadDataset" :infinite-scroll-disabled="disabledScroll">
            <el-col
              :xs="24"
              :sm="12"
              :md="8"
              :lg="6"
              :xl="6"
              v-for="(item, index) in paragraphDetail"
              :key="index"
              class="p-8"
            >
              <CardBox
                shadow="hover"
                :title="item.title || '-'"
                :description="item.content"
                class="document-card cursor"
                :class="item.is_active ? '' : 'disabled'"
                :showIcon="false"
                @click="editParagraph(item)"
              >
                <div class="active-button" @click.stop>
                  <el-switch
                    v-model="item.is_active"
                    @change="changeState($event, item)"
                    size="small"
                  />
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
          <div style="padding: 16px 10px">
            <el-divider v-if="paragraphDetail.length > 0 && loading">
              <el-text type="info"> 加载中...</el-text>
            </el-divider>
            <el-divider v-if="noMore">
              <el-text type="info"> 到底啦！</el-text>
            </el-divider>
          </div>
        </div>
      </el-scrollbar>
    </div>
    <ParagraphDialog ref="ParagraphDialogRef" :title="title" @refresh="refresh" />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import documentApi from '@/api/document'
import paragraphApi from '@/api/paragraph'
import ParagraphDialog from './component/ParagraphDialog.vue'
import { numberFormat } from '@/utils/utils'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import useStore from '@/stores'
const { paragraph } = useStore()
const route = useRoute()
const {
  params: { id, documentId }
} = route as any

const ParagraphDialogRef = ref()
const loading = ref(false)
const documentDetail = ref<any>({})
const paragraphDetail = ref<any[]>([])
const title = ref('')
const search = ref('')
const searchType = ref('title')

const pageConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})

const noMore = computed(
  () =>
    paragraphDetail.value.length > 0 &&
    paragraphDetail.value.length === pageConfig.total &&
    pageConfig.total > 20 &&
    !loading.value
)
const disabledScroll = computed(
  () => paragraphDetail.value.length > 0 && (loading.value || noMore.value)
)

function loadDataset() {
  if (pageConfig.total > pageConfig.page_size) {
    pageConfig.current_page += 1
    getParagraphList()
  }
}

function searchHandle() {
  pageConfig.current_page = 1
  paragraphDetail.value = []
  getParagraphList()
}

function changeState(bool: Boolean, row: any) {
  const obj = {
    is_active: bool
  }
  loading.value = true
  paragraph
    .asyncPutParagraph(id, documentId, row.id, obj)
    .then((res) => {
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function deleteParagraph(row: any) {
  MsgConfirm(`是否删除段落：${row.title || '-'} ?`, `删除后无法恢复，请谨慎操作。`, {
    confirmButtonText: '删除',
    confirmButtonClass: 'danger'
  })
    .then(() => {
      paragraphApi.delParagraph(id, documentId, row.id, loading).then(() => {
        const index = paragraphDetail.value.findIndex((v) => v.id === row.id)
        paragraphDetail.value.splice(index, 1)
        MsgSuccess('删除成功')
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
  documentApi
    .getDocumentDetail(id, documentId)
    .then((res) => {
      documentDetail.value = res.data
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function getParagraphList() {
  paragraphApi
    .getParagraph(
      id,
      documentId,
      pageConfig,
      search.value && { [searchType.value]: search.value },
      loading
    )
    .then((res) => {
      paragraphDetail.value = [...paragraphDetail.value, ...res.data.records]
      pageConfig.total = res.data.total
    })
}

function refresh(data: any) {
  if (data) {
    const index = paragraphDetail.value.findIndex((v) => v.id === data.id)
    paragraphDetail.value.splice(index, 1, data)
  } else {
    pageConfig.current_page = 1
    paragraphDetail.value = []
    getParagraphList()
  }
}

onMounted(() => {
  getDetail()
  getParagraphList()
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
