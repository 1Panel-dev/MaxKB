<template>
  <LayoutContainer back-to="-1" class="document-detail">
    <template #header>
      <div style="width: 78%">
        <h3 style="display: inline-block">{{ documentDetail?.name }}</h3>
        <el-text type="info" v-if="documentDetail?.type === '1'"
          >（{{ $t('views.document.form.source_url.label') }}：<el-link
            :href="documentDetail?.meta?.source_url"
            target="_blank"
          >
            <span class="break-all">{{ documentDetail?.meta?.source_url }} </span></el-link
          >）
        </el-text>
      </div>
      <div class="header-button">
        <el-button @click="batchSelectedHandle(true)" v-if="isBatch === false">
          {{ $t('views.paragraph.setting.batchSelected') }}
        </el-button>
        <el-button @click="batchSelectedHandle(false)" v-if="isBatch === true">
          {{ $t('views.paragraph.setting.cancelSelected') }}
        </el-button>
        <el-button
          @click="addParagraph"
          type="primary"
          :disabled="loading"
          v-if="isBatch === false"
        >
          {{ $t('views.paragraph.addParagraph') }}
        </el-button>
      </div>
    </template>
    <div
      class="document-detail__main p-16"
      v-loading="(paginationConfig.current_page === 1 && loading) || changeStateloading"
    >
      <div class="flex-between p-8">
        <span>{{ paginationConfig.total }} {{ $t('views.paragraph.paragraph_count') }}</span>
        <el-input
          v-model="search"
          :placeholder="$t('common.search')"
          class="input-with-select"
          style="width: 260px"
          @change="searchHandle"
          clearable
        >
          <template #prepend>
            <el-select v-model="searchType" placeholder="Select" style="width: 80px">
              <el-option :label="$t('common.title')" value="title" />
              <el-option :label="$t('common.content')" value="content" />
            </el-select>
          </template>
        </el-input>
      </div>
      <el-scrollbar>
        <div class="document-detail-height">
          <el-empty v-if="paragraphDetail.length == 0" :description="$t('common.noData')" />

          <InfiniteScroll
            v-else
            :size="paragraphDetail.length"
            :total="paginationConfig.total"
            :page_size="paginationConfig.page_size"
            v-model:current_page="paginationConfig.current_page"
            @load="getParagraphList"
            :loading="loading"
          >
            <el-row>
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
                <!-- 批量操作card -->
                <CardBox
                  v-if="isBatch === true"
                  shadow="hover"
                  :title="item.title || '-'"
                  :description="item.content"
                  class="document-card cursor"
                  :class="multipleSelection.includes(item.id) ? 'selected' : ''"
                  :showIcon="false"
                  @click="selectHandle(item.id)"
                >
                  <div class="active-button" @click.stop></div>

                  <template #footer>
                    <div class="footer-content flex-between">
                      <span>
                        {{ numberFormat(item?.content.length) || 0 }}
                        {{ $t('views.paragraph.character_count') }}
                      </span>
                    </div>
                  </template>
                </CardBox>
                <!-- 非批量操作card -->
                <CardBox
                  v-else
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
                      :loading="loading"
                      v-model="item.is_active"
                      :before-change="() => changeState(item)"
                      size="small"
                    />
                  </div>

                  <template #footer>
                    <div class="footer-content flex-between">
                      <span>
                        {{ numberFormat(item?.content.length) || 0 }}
                        {{ $t('views.paragraph.character_count') }}
                      </span>

                      <span @click.stop>
                        <el-dropdown trigger="click">
                          <el-button text>
                            <el-icon><MoreFilled /></el-icon>
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item @click="openGenerateDialog(item)">
                                <el-icon><Connection /></el-icon>
                                {{
                                  $t('views.document.generateQuestion.title')
                                }}</el-dropdown-item
                              >
                              <el-dropdown-item @click="openSelectDocumentDialog(item)">
                                <AppIcon iconName="app-migrate"></AppIcon>
                                {{ $t('views.document.setting.migration') }}</el-dropdown-item
                              >
                              <el-dropdown-item icon="Delete" @click.stop="deleteParagraph(item)">{{
                                $t('common.delete')
                              }}</el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </span>
                    </div>
                  </template>
                </CardBox>
              </el-col>
            </el-row>
          </InfiniteScroll>
        </div>
      </el-scrollbar>

      <div class="mul-operation border-t w-full" v-if="isBatch === true">
        <el-button :disabled="multipleSelection.length === 0" @click="openGenerateDialog()">
          {{ $t('views.document.generateQuestion.title') }}
        </el-button>
        <el-button :disabled="multipleSelection.length === 0" @click="openSelectDocumentDialog()">
          {{ $t('views.document.setting.migration') }}
        </el-button>

        <el-button :disabled="multipleSelection.length === 0" @click="deleteMulParagraph">
          {{ $t('common.delete') }}
        </el-button>
        <span class="ml-8">
          {{ $t('views.document.selected') }} {{ multipleSelection.length }}
          {{ $t('views.document.items') }}
        </span>
      </div>
    </div>
    <ParagraphDialog ref="ParagraphDialogRef" :title="title" @refresh="refresh" />
    <SelectDocumentDialog ref="SelectDocumentDialogRef" @refresh="refreshMigrateParagraph" />
    <GenerateRelatedDialog ref="GenerateRelatedDialogRef" @refresh="refresh" />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import documentApi from '@/api/document'
import paragraphApi from '@/api/paragraph'
import ParagraphDialog from './component/ParagraphDialog.vue'
import SelectDocumentDialog from './component/SelectDocumentDialog.vue'
import GenerateRelatedDialog from '@/components/generate-related-dialog/index.vue'
import { numberFormat } from '@/utils/utils'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import useStore from '@/stores'
import { t } from '@/locales'
const { paragraph } = useStore()
const route = useRoute()
const {
  params: { id, documentId }
} = route as any

const SelectDocumentDialogRef = ref()
const ParagraphDialogRef = ref()
const loading = ref(false)
const changeStateloading = ref(false)
const documentDetail = ref<any>({})
const paragraphDetail = ref<any[]>([])
const title = ref('')
const search = ref('')
const searchType = ref('title')

// 批量操作
const isBatch = ref(false)
const multipleSelection = ref<any[]>([])

const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0
})

function refreshMigrateParagraph() {
  paragraphDetail.value = paragraphDetail.value.filter(
    (v) => !multipleSelection.value.includes(v.id)
  )
  multipleSelection.value = []
  MsgSuccess(t('views.document.tip.migrationSuccess'))
}

function openSelectDocumentDialog(row?: any) {
  if (row) {
    multipleSelection.value = [row.id]
  }
  SelectDocumentDialogRef.value.open(multipleSelection.value)
}
function deleteMulParagraph() {
  MsgConfirm(
    `${t('views.document.delete.confirmTitle1')} ${multipleSelection.value.length} ${t('views.document.delete.confirmTitle2')}`,
    t('views.paragraph.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      paragraphApi
        .delMulParagraph(id, documentId, multipleSelection.value, changeStateloading)
        .then(() => {
          paragraphDetail.value = paragraphDetail.value.filter(
            (v) => !multipleSelection.value.includes(v.id)
          )
          multipleSelection.value = []
          MsgSuccess(t('views.document.delete.successMessage'))
        })
    })
    .catch(() => {})
}

function batchSelectedHandle(bool: boolean) {
  isBatch.value = bool
  multipleSelection.value = []
}

function selectHandle(id: string) {
  if (multipleSelection.value.includes(id)) {
    multipleSelection.value.splice(multipleSelection.value.indexOf(id), 1)
  } else {
    multipleSelection.value.push(id)
  }
}

function searchHandle() {
  paginationConfig.current_page = 1
  paragraphDetail.value = []
  getParagraphList()
}

function changeState(row: any) {
  const obj = {
    is_active: !row.is_active
  }
  paragraph
    .asyncPutParagraph(id, documentId, row.id, obj, changeStateloading)
    .then((res) => {
      const index = paragraphDetail.value.findIndex((v) => v.id === row.id)
      paragraphDetail.value[index].is_active = !paragraphDetail.value[index].is_active
      return true
    })
    .catch(() => {
      return false
    })
}

function deleteParagraph(row: any) {
  MsgConfirm(
    `${t('views.paragraph.delete.confirmTitle')} ${row.title || '-'} ?`,
    t('views.paragraph.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      paragraph.asyncDelParagraph(id, documentId, row.id, loading).then(() => {
        const index = paragraphDetail.value.findIndex((v) => v.id === row.id)
        paragraphDetail.value.splice(index, 1)
        MsgSuccess(t('common.deleteSuccess'))
      })
    })
    .catch(() => {})
}

function addParagraph() {
  title.value = t('views.paragraph.addParagraph')
  ParagraphDialogRef.value.open()
}
function editParagraph(row: any) {
  title.value = t('views.paragraph.paragraphDetail') 
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
      paginationConfig,
      search.value && { [searchType.value]: search.value },
      loading
    )
    .then((res) => {
      paragraphDetail.value = [...paragraphDetail.value, ...res.data.records]
      paginationConfig.total = res.data.total
    })
}

function refresh(data: any) {
  if (data) {
    const index = paragraphDetail.value.findIndex((v) => v.id === data.id)
    paragraphDetail.value.splice(index, 1, data)
  } else {
    paginationConfig.current_page = 1
    paragraphDetail.value = []
    getParagraphList()
  }
}

const GenerateRelatedDialogRef = ref()
function openGenerateDialog(row?: any) {
  const arr: string[] = []
  if (row) {
    arr.push(row.id)
  } else {
    multipleSelection.value.map((v) => {
      if (v) {
        arr.push(v)
      }
    })
  }

  GenerateRelatedDialogRef.value.open(arr, 'paragraph')
}

onMounted(() => {
  getDetail()
  getParagraphList()
})
</script>
<style lang="scss" scoped>
.document-detail {
  .header-button {
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
    &.selected {
      background: #ffffff;
      &:hover {
        background: #ffffff;
      }
    }
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
    :deep(.content) {
      -webkit-line-clamp: 5 !important;
      height: 110px !important;
    }
    .active-button {
      position: absolute;
      right: 16px;
      top: 16px;
    }
  }

  &__main {
    position: relative;
    box-sizing: border-box;
    .mul-operation {
      position: absolute;
      bottom: 0;
      left: 0;
      padding: 16px 24px;
      box-sizing: border-box;
      background: #ffffff;
    }
  }
}
</style>
