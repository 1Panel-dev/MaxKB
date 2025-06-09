<template>
  <div class="paragraph p-12-24">
    <div class="flex align-center" style="width: 78%">
      <back-button to="-1" style="margin-left: -4px"></back-button>
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
      <el-button @click="addParagraph" type="primary" :disabled="loading" v-if="isBatch === false">
        {{ $t('views.paragraph.addParagraph') }}
      </el-button>
    </div>
    <el-card
      style="--el-card-padding: 0"
      class="paragraph__main mt-16"
      v-loading="(paginationConfig.current_page === 1 && loading) || changeStateloading"
    >
      <div class="flex-between p-12-16 border-b">
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
      <div class="flex">
        <div class="paragraph-sidebar p-16 border-r">
          <el-anchor
            direction="vertical"
            type="default"
            :offset="130"
            container=".paragraph-scollbar"
            @click="handleClick"
          >
            <template v-for="(item, index) in paragraphDetail" :key="item.id">
              <el-anchor-link :href="`#${item.id}`" :title="item.title" v-if="item.title" />
            </template>
          </el-anchor>
        </div>
        <div class="w-full">
          <el-empty v-if="paragraphDetail.length == 0" :description="$t('common.noData')" />
          <div v-else>
            <el-scrollbar class="paragraph-scollbar">
              <div class="paragraph-detail">
                <InfiniteScroll
                  :size="paragraphDetail.length"
                  :total="paginationConfig.total"
                  :page_size="paginationConfig.page_size"
                  v-model:current_page="paginationConfig.current_page"
                  @load="getParagraphList"
                  :loading="loading"
                >
                  <VueDraggable
                    ref="el"
                    v-bind:modelValue="paragraphDetail"
                    :disabled="isBatch === true"
                    handle=".handle"
                    :animation="150"
                    ghostClass="ghost"
                    @end="onEnd"
                  >
                    <el-checkbox-group v-model="multipleSelection">
                      <template v-for="(item, index) in paragraphDetail" :key="item.id">
                        <!-- 批量操作 -->
                        <div class="paragraph-card flex" :id="item.id" v-if="isBatch === true">
                          <el-checkbox :value="item.id" />
                          <ParagraphCard :data="item" class="mb-8 w-full" />
                        </div>
                        <!-- 非批量操作 -->
                        <div class="handle paragraph-card flex" :id="item.id" v-else>
                          <img
                            src="@/assets/sort.svg"
                            alt=""
                            height="15"
                            class="handle-img mr-8 mt-24 cursor"
                          />
                          <ParagraphCard
                            :data="item"
                            class="mb-8 w-full"
                            @changeState="changeState"
                            @deleteParagraph="deleteParagraph"
                          />
                        </div>
                      </template>
                    </el-checkbox-group>
                  </VueDraggable>
                </InfiniteScroll>
              </div>
            </el-scrollbar>
          </div>
        </div>
      </div>

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
    </el-card>
    <ParagraphDialog ref="ParagraphDialogRef" :title="title" @refresh="refresh" />
    <SelectDocumentDialog ref="SelectDocumentDialogRef" @refresh="refreshMigrateParagraph" />
    <GenerateRelatedDialog ref="GenerateRelatedDialogRef" @refresh="refresh" />
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep } from 'lodash'
import documentApi from '@/api/knowledge/document'
import paragraphApi from '@/api/knowledge/paragraph'
import ParagraphDialog from './component/ParagraphDialog.vue'
import ParagraphCard from './component/ParagraphCard.vue'
import SelectDocumentDialog from './component/SelectDocumentDialog.vue'
import GenerateRelatedDialog from '@/components/generate-related-dialog/index.vue'
import { VueDraggable } from 'vue-draggable-plus'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import useStore from '@/stores'
import { t } from '@/locales'
const { paragraph } = useStore()
const route = useRoute()
const {
  params: { id, documentId },
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

const handleClick = (e: MouseEvent) => {
  e.preventDefault()
}

// 批量操作
const isBatch = ref(false)
const multipleSelection = ref<any[]>([])

const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0,
})

function deleteParagraph(id: string) {
  const index = paragraphDetail.value.findIndex((v) => v.id === id)
  paragraphDetail.value.splice(index, 1)
}

function changeState(id: string) {
  const index = paragraphDetail.value.findIndex((v) => v.id === id)
  paragraphDetail.value[index].is_active = !paragraphDetail.value[index].is_active
}

function refreshMigrateParagraph() {
  paragraphDetail.value = paragraphDetail.value.filter(
    (v) => !multipleSelection.value.includes(v.id),
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
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      paragraphApi
        .putMulParagraph(id, documentId, multipleSelection.value, changeStateloading)
        .then(() => {
          paragraphDetail.value = paragraphDetail.value.filter(
            (v) => !multipleSelection.value.includes(v.id),
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

function addParagraph() {
  title.value = t('views.paragraph.addParagraph')
  ParagraphDialogRef.value.open()
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
      loading,
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

function onEnd(event?: any) {
  const { oldIndex, newIndex } = event
  if (oldIndex === undefined || newIndex === undefined) return
  const list = cloneDeep(paragraphDetail.value)
  if (oldIndex === list.length - 1 || newIndex === list.length - 1) {
    return
  }
  const newInstance = { ...list[oldIndex], type: list[newIndex].type, id: list[newIndex].id }
  const oldInstance = { ...list[newIndex], type: list[oldIndex].type, id: list[oldIndex].id }
  list[newIndex] = newInstance
  list[oldIndex] = oldInstance
  paragraphDetail.value = list
}

onMounted(() => {
  getDetail()
  getParagraphList()
})
</script>
<style lang="scss" scoped>
.paragraph {
  position: relative;
  .header-button {
    position: absolute;
    right: calc(var(--app-base-px) * 3);
    top: calc(var(--app-base-px) + 4px);
  }
  .paragraph-sidebar {
    width: 240px;
  }

  .paragraph-detail {
    height: calc(100vh - 215px);
    max-width: 1000px;
    margin: 16px auto;
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
  .paragraph-card {
    &.handle {
      .handle-img {
        visibility: hidden;
      }
      &:hover {
        .handle-img {
          visibility: visible;
        }
      }
    }
  }
}
</style>
