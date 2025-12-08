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
    <div class="header-button" v-if="!shareDisabled && permissionPrecise.doc_edit(id)">
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
            <el-select
              v-model="searchType"
              placeholder="Select"
              style="width: 80px"
              @change="searchTypeChange"
            >
              <el-option :label="$t('common.title')" value="title" />
              <el-option :label="$t('common.content')" value="content" />
            </el-select>
          </template>
        </el-input>
      </div>
      <LayoutContainer showCollapse>
        <template #left>
          <div class="paragraph-sidebar p-16">
            <el-scrollbar class="paragraph-scrollbar">
              <el-anchor
                direction="vertical"
                type="default"
                :offset="130"
                container=".paragraph-scrollbar"
                @click="handleClick"
              >
                <template v-for="item in paragraphDetail" :key="item.id">
                  <el-anchor-link :href="`#m${item.id}`" :title="item.title" v-if="item.title">
                    <span :title="item.title">
                      {{ item.title }}
                    </span>
                  </el-anchor-link>
                </template>
              </el-anchor>
            </el-scrollbar>
          </div>
        </template>
        <div class="w-full">
          <el-empty v-if="paragraphDetail.length == 0" :description="$t('common.noData')" />
          <div v-else>
            <el-scrollbar class="paragraph-scrollbar">
              <div class="paragraph-detail">
                <el-checkbox-group v-model="multipleSelection">
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
                      v-model="paragraphDetail"
                      :disabled="
                        isBatch === true ||
                        shareDisabled ||
                        dialogVisible ||
                        !permissionPrecise.doc_edit(id)
                      "
                      handle=".handle"
                      :animation="150"
                      ghostClass="ghost"
                      @end="onEnd"
                    >
                      <template v-for="(item, index) in paragraphDetail" :key="item.id">
                        <div :id="`m${item.id}`" class="flex mb-16">
                          <!-- 批量操作 -->
                          <div class="paragraph-card flex w-full" v-if="isBatch === true">
                            <el-checkbox :value="item.id" />
                            <ParagraphCard
                              :data="item"
                              class="mb-8 w-full"
                              :class="{
                                'is-selected': multipleSelection.includes(item.id),
                              }"
                              :disabled="true"
                              @clickCard="toggleSelect(item.id)"
                            />
                          </div>
                          <!-- 非批量操作 -->
                          <div class="handle paragraph-card flex w-full" :id="item.id" v-else>
                            <img
                              src="@/assets/sort.svg"
                              alt=""
                              height="15"
                              class="handle-img mr-8 mt-24 cursor"
                            />

                            <ParagraphCard
                              :data="item"
                              :showMoveUp="index !== 0"
                              :showMoveDown="index < paragraphDetail.length - 1"
                              class="mb-8 w-full"
                              @changeState="changeState"
                              @deleteParagraph="deleteParagraph"
                              @move="
                                (val: string) =>
                                  onEnd(
                                    null,
                                    {
                                      paragraph_id: item.id,
                                      new_position: val === 'up' ? index - 1 : index + 1,
                                    },
                                    index,
                                  )
                              "
                              @refresh="refresh"
                              @refreshMigrateParagraph="refreshMigrateParagraph"
                              :disabled="shareDisabled"
                              @dialogVisibleChange="dialogVisibleChange"
                            />
                          </div>
                        </div>
                      </template>
                    </VueDraggable>
                  </InfiniteScroll>
                </el-checkbox-group>
              </div>
            </el-scrollbar>
          </div>
        </div>
      </LayoutContainer>

      <div class="mul-operation border-t w-full flex align-center" v-if="isBatch === true">
        <el-button :disabled="multipleSelection.length === 0" @click="openGenerateDialog()">
          {{ $t('views.document.generateQuestion.title') }}
        </el-button>
        <el-button :disabled="multipleSelection.length === 0" @click="openSelectDocumentDialog()">
          {{ $t('views.document.setting.migration') }}
        </el-button>

        <el-button :disabled="multipleSelection.length === 0" @click="deleteMulParagraph">
          {{ $t('common.delete') }}
        </el-button>
        <span class="color-secondary ml-24 mr-16">
          {{ $t('common.selected') }} {{ multipleSelection.length }}
          {{ $t('views.document.items') }}
        </span>
        <el-button
          link
          type="primary"
          v-if="multipleSelection.length > 0"
          @click="multipleSelection = []"
        >
          {{ $t('common.clear') }}
        </el-button>
      </div>
    </el-card>
    <ParagraphDialog
      ref="ParagraphDialogRef"
      :title="title"
      :apiType="apiType"
      @refresh="refresh"
    />
    <SelectDocumentDialog
      ref="SelectDocumentDialogRef"
      @refresh="refreshMigrateParagraph"
      :apiType="apiType"
      :workspaceId="knowledgeDetail.workspace_id"
    />
    <GenerateRelatedDialog ref="GenerateRelatedDialogRef" @refresh="refresh" :apiType="apiType" />
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import ParagraphDialog from './component/ParagraphDialog.vue'
import ParagraphCard from './component/ParagraphCard.vue'
import SelectDocumentDialog from './component/SelectDocumentDialog.vue'
import GenerateRelatedDialog from '@/components/generate-related-dialog/index.vue'
import { VueDraggable } from 'vue-draggable-plus'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import permissionMap from '@/permission'
import { t } from '@/locales'
import { cloneDeep } from 'lodash'
const route = useRoute()
const {
  params: { id, documentId },
  query: { from, isShared },
} = route as any

const apiType = computed(() => {
  return from as 'systemShare' | 'workspace' | 'systemManage'
})
const shareDisabled = computed(() => {
  return isShared === 'true'
})
const permissionPrecise = computed(() => {
  return permissionMap['knowledge'][apiType.value]
})

const SelectDocumentDialogRef = ref()
const ParagraphDialogRef = ref()
const loading = ref(false)
const changeStateloading = ref(false)
const documentDetail = ref<any>({})
const knowledgeDetail = ref<any>({})
const paragraphDetail = ref<any[]>([])
const title = ref('')
const search = ref('')
const searchType = ref('title')

const searchTypeChange = () => {
  search.value = ''
}

const dialogVisible = ref(false)
watch(
  () => ParagraphDialogRef.value?.dialogVisible,
  (val: boolean) => {
    dialogVisible.value = val
  },
)
function dialogVisibleChange(val: boolean) {
  dialogVisible.value = val
}

const handleClick = (e: MouseEvent, ele: any) => {
  e.preventDefault()
  document.querySelector(`${ele}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

// 批量操作
const isBatch = ref(false)
const multipleSelection = ref<any[]>([])

function toggleSelect(id: number) {
  const index = multipleSelection.value.indexOf(id)
  if (index === -1) {
    multipleSelection.value.push(id)
  } else {
    multipleSelection.value.splice(index, 1)
  }
}

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

function refreshMigrateParagraph(data: any) {
  if (data) {
    multipleSelection.value = [data.id]
  }
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
      loadSharedApi({ type: 'paragraph', systemType: apiType.value })
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
  loadSharedApi({ type: 'document', isShared: shareDisabled.value, systemType: apiType.value })
    .getDocumentDetail(id, documentId, loading)
    .then((res: any) => {
      documentDetail.value = res.data
    })

  loadSharedApi({ type: 'knowledge', isShared: shareDisabled.value, systemType: apiType.value })
    .getKnowledgeDetail(id, loading)
    .then((res: any) => {
      knowledgeDetail.value = res.data
    })
}

function getParagraphList() {
  loadSharedApi({ type: 'paragraph', isShared: shareDisabled.value, systemType: apiType.value })
    .getParagraphPage(
      id,
      documentId,
      paginationConfig,
      search.value && { [searchType.value]: search.value },
      loading,
    )
    .then((res: any) => {
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

function onEnd(event?: any, params?: any, index?: number) {
  // console.log('onEnd', event, params, index)
  const p = cloneDeep(params)
  if (p) {
    p.new_position = p.new_position + 1 // 由于拖拽时会将当前段落位置作为新位置，所以需要加1
  }
  const obj = p ?? {
    paragraph_id: paragraphDetail.value[event.newIndex].id, // 当前拖动的段落ID
    new_position: paragraphDetail.value[event.newIndex + 1]?.position || paragraphDetail.value.length, // 新位置的段落位置
  }
  // console.log(paragraphDetail.value[event.newIndex], obj)
  loadSharedApi({ type: 'paragraph', systemType: apiType.value }).putAdjustPosition(
    id,
    documentId,
    obj,
    loading,
  )
  if (params) {
    const movedItem = paragraphDetail.value.splice(index as number, 1)[0]
    paragraphDetail.value.splice(params.new_position, 0, movedItem)
  }
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
    width: 100%;
    height: calc(100vh - 215px);
    box-sizing: border-box;
  }

  .paragraph-detail {
    height: calc(100vh - 215px);
    max-width: 1000px;
    margin: 16px auto;

    .el-checkbox-group {
      font-size: inherit;
      line-height: inherit;
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
  .paragraph-card {
    .is-selected {
      border: 1px solid var(--el-color-primary);
    }
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
