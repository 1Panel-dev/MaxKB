<template>
  <el-dialog
    title="关联分段"
    v-model="dialogVisible"
    width="80%"
    class="paragraph-dialog"
    destroy-on-close
  >
    <el-row v-loading="loading">
      <el-col :span="6">
        <el-scrollbar height="500" wrap-class="paragraph-scrollbar">
          <div class="bold title align-center p-24 pb-0">选择文档</div>
          <div class="p-8" style="padding-bottom: 8px">
            <common-list
              :data="documentList"
              class="mt-8"
              @click="clickDocumentHandle"
              :default-active="currentDocument"
            >
              <template #default="{ row }">
                <span class="flex-between lighter">
                  <auto-tooltip :content="row.name">
                    {{ row.name }}
                  </auto-tooltip>
                  <AppAvatar
                    v-if="associationCount(row.id)"
                    :size="17"
                    style="margin-right: -10px; font-size: 12px"
                  >
                    {{ associationCount(row.id) }}</AppAvatar
                  >
                </span>
              </template>
            </common-list>
          </div>
        </el-scrollbar>
      </el-col>
      <el-col :span="18" class="border-l">
        <el-scrollbar height="500" wrap-class="paragraph-scrollbar">
          <div class="p-24" style="padding-bottom: 8px; padding-top: 16px">
            <div class="flex-between mb-16">
              <div class="bold title align-center">
                选择分段
                <el-text> （已选分段：{{ associationCount(currentDocument) }} 个） </el-text>
              </div>
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
            <el-empty v-if="paragraphList.length == 0" description="暂无数据" />

            <InfiniteScroll
              v-else
              :size="paragraphList.length"
              :total="paginationConfig.total"
              :page_size="paginationConfig.page_size"
              v-model:current_page="paginationConfig.current_page"
              @load="getParagraphList"
              :loading="loading"
            >
              <template v-for="(item, index) in paragraphList" :key="index">
                <CardBox
                  shadow="hover"
                  :title="item.title || '-'"
                  :description="item.content"
                  class="paragraph-card cursor mb-16"
                  :class="isAssociation(item.id) ? 'active' : ''"
                  :showIcon="false"
                  @click="associationClick(item)"
                >
                </CardBox>
              </template>
            </InfiniteScroll>
          </div>
        </el-scrollbar>
      </el-col>
    </el-row>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { useRoute } from 'vue-router'
import problemApi from '@/api/problem'
import paragraphApi from '@/api/paragraph'
import useStore from '@/stores'

const { problem, document } = useStore()

const route = useRoute()
const {
  params: { id } // datasetId
} = route as any

const emit = defineEmits(['refresh'])

const dialogVisible = ref<boolean>(false)

const loading = ref(false)
const documentList = ref<any[]>([])
const paragraphList = ref<any[]>([])
const currentProblemId = ref<String>('')

// 回显
const associationParagraph = ref<any[]>([])

const currentDocument = ref<String>('')
const search = ref('')
const searchType = ref('title')

const paginationConfig = reactive({
  current_page: 1,
  page_size: 50,
  total: 0
})

function associationClick(item: any) {
  if (isAssociation(item.id)) {
    problem
      .asyncDisassociationProblem(
        id,
        item.document_id,
        item.id,
        currentProblemId.value as string,
        loading
      )
      .then(() => {
        getRecord(currentProblemId.value)
      })
  } else {
    problem
      .asyncAssociationProblem(
        id,
        item.document_id,
        item.id,
        currentProblemId.value as string,
        loading
      )
      .then(() => {
        getRecord(currentProblemId.value)
      })
  }
}

function searchHandle() {
  paginationConfig.current_page = 1
  paragraphList.value = []
  getParagraphList(currentDocument.value)
}

function clickDocumentHandle(item: any) {
  currentDocument.value = item.id
  getParagraphList(item.id)
}

function getDocument() {
  document.asyncGetAllDocument(id, loading).then((res: any) => {
    documentList.value = res.data
    currentDocument.value = documentList.value?.length > 0 ? documentList.value[0].id : ''
    getParagraphList(currentDocument.value)
  })
}

function getParagraphList(documentId: String) {
  paragraphApi
    .getParagraph(
      id,
      (documentId || currentDocument.value) as string,
      paginationConfig,
      search.value && { [searchType.value]: search.value },
      loading
    )
    .then((res) => {
      paragraphList.value = [...paragraphList.value, ...res.data.records]
      paginationConfig.total = res.data.total
    })
}

// 已关联分段
function getRecord(problemId: String) {
  problemApi.getDetailProblems(id as string, problemId as string, loading).then((res) => {
    associationParagraph.value = res.data
  })
}

function associationCount(documentId: String) {
  return associationParagraph.value.filter((item) => item.document_id === documentId).length
}
function isAssociation(paragraphId: String) {
  return associationParagraph.value.some((option) => option.id === paragraphId)
}

watch(dialogVisible, (bool) => {
  if (!bool) {
    documentList.value = []
    paragraphList.value = []
    associationParagraph.value = []

    currentDocument.value = ''
    search.value = ''
    searchType.value = 'title'
  }
})

const open = (problemId: string) => {
  currentProblemId.value = problemId
  getDocument()
  getRecord(problemId)
  dialogVisible.value = true
}

defineExpose({ open })
</script>
<style lang="scss" scope>
.paragraph-card {
  position: relative;
  &.active {
    border: 1px solid var(--el-color-primary);
    &:before {
      content: '';
      position: absolute;
      right: 0;
      top: 0;
      border: 14px solid var(--el-color-primary);
      border-bottom-color: transparent;
      border-left-color: transparent;
    }

    &:after {
      content: '';
      width: 3px;
      height: 6px;
      position: absolute;
      right: 5px;
      top: 2px;
      border: 2px solid #fff;
      border-top-color: transparent;
      border-left-color: transparent;
      transform: rotate(35deg);
    }
  }
}
</style>
