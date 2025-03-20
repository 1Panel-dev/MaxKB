<template>
  <LayoutContainer :header="$t('common.fileUpload.document')" class="document-main">
    <div class="main-calc-height">
      <div class="p-24">
        <div class="flex-between">
          <div>
            <el-button
              v-if="datasetDetail.type === '0'"
              type="primary"
              @click="router.push({ path: '/dataset/upload', query: { id: id } })"
              >{{ $t('views.document.uploadDocument') }}
            </el-button>
            <el-button v-if="datasetDetail.type === '1'" type="primary" @click="importDoc"
              >{{ $t('views.document.importDocument') }}
            </el-button>
            <el-button
              @click="syncMulDocument"
              :disabled="multipleSelection.length === 0"
              v-if="datasetDetail.type === '1'"
              >{{ $t('views.document.syncDocument') }}
            </el-button>
            <el-button
              v-if="datasetDetail.type === '2'"
              type="primary"
              @click="
                router.push({
                  path: '/dataset/import',
                  query: { id: id, folder_token: datasetDetail.meta.folder_token }
                })
              "
              >{{ $t('views.document.importDocument') }}
            </el-button>
            <el-button
              @click="syncLarkMulDocument"
              :disabled="multipleSelection.length === 0"
              v-if="datasetDetail.type === '2'"
              >{{ $t('views.document.syncDocument') }}
            </el-button>
            <el-button @click="openDatasetDialog()" :disabled="multipleSelection.length === 0">
              {{ $t('views.document.setting.migration') }}
            </el-button>
            <el-button @click="batchRefresh" :disabled="multipleSelection.length === 0">
              {{ $t('views.dataset.setting.vectorization') }}
            </el-button>
            <el-button @click="openGenerateDialog()" :disabled="multipleSelection.length === 0">
              {{ $t('views.document.generateQuestion.title') }}
            </el-button>
            <el-button @click="openBatchEditDocument" :disabled="multipleSelection.length === 0">
              {{ $t('common.setting') }}
            </el-button>
            <el-button @click="deleteMulDocument" :disabled="multipleSelection.length === 0">
              {{ $t('common.delete') }}
            </el-button>
          </div>

          <el-input
            v-model="filterText"
            :placeholder="$t('views.document.searchBar.placeholder')"
            prefix-icon="Search"
            class="w-240"
            @change="getList"
            clearable
          />
        </div>
        <app-table
          ref="multipleTableRef"
          class="mt-16"
          :data="documentData"
          :pagination-config="paginationConfig"
          :quick-create="datasetDetail.type === '0'"
          @sizeChange="handleSizeChange"
          @changePage="getList"
          @cell-mouse-enter="cellMouseEnter"
          @cell-mouse-leave="cellMouseLeave"
          @creatQuick="creatQuickHandle"
          @row-click="rowClickHandle"
          @selection-change="handleSelectionChange"
          @sort-change="handleSortChange"
          v-loading="loading"
          :row-key="(row: any) => row.id"
          :storeKey="storeKey"
        >
          <el-table-column type="selection" width="55" :reserve-selection="true" />
          <el-table-column prop="name" :label="$t('views.document.table.name')" min-width="280">
            <template #default="{ row }">
              <ReadWrite
                @change="editName($event, row.id)"
                :data="row.name"
                :showEditIcon="row.id === currentMouseId"
              />
            </template>
          </el-table-column>
          <el-table-column
            prop="char_length"
            :label="$t('views.document.table.char_length')"
            align="right"
            min-width="90"
            sortable
          >
            <template #default="{ row }">
              {{ numberFormat(row.char_length) }}
            </template>
          </el-table-column>
          <el-table-column
            prop="paragraph_count"
            :label="$t('views.document.table.paragraph')"
            align="right"
            min-width="90"
            sortable
          />
          <el-table-column prop="status" :label="$t('views.document.fileStatus.label')" width="130">
            <template #header>
              <div>
                <span>{{ $t('views.document.fileStatus.label') }}</span>
                <el-dropdown trigger="click" @command="dropdownHandle">
                  <el-button
                    style="margin-top: 1px"
                    link
                    :type="filterMethod['status'] ? 'primary' : ''"
                  >
                    <el-icon>
                      <Filter />
                    </el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu style="width: 100px">
                      <el-dropdown-item
                        :class="filterMethod['status'] ? '' : 'is-active'"
                        :command="beforeCommand('status', '')"
                        class="justify-center"
                        >{{ $t('views.document.table.all') }}
                      </el-dropdown-item>
                      <el-dropdown-item
                        :class="filterMethod['status'] === State.SUCCESS ? 'is-active' : ''"
                        class="justify-center"
                        :command="beforeCommand('status', State.SUCCESS)"
                        >{{ $t('views.document.fileStatus.SUCCESS') }}
                      </el-dropdown-item>
                      <el-dropdown-item
                        :class="filterMethod['status'] === State.FAILURE ? 'is-active' : ''"
                        class="justify-center"
                        :command="beforeCommand('status', State.FAILURE)"
                        >{{ $t('views.document.fileStatus.FAILURE') }}
                      </el-dropdown-item>
                      <el-dropdown-item
                        :class="
                          filterMethod['status'] === State.STARTED &&
                          filterMethod['task_type'] == TaskType.EMBEDDING
                            ? 'is-active'
                            : ''
                        "
                        class="justify-center"
                        :command="beforeCommand('status', State.STARTED, TaskType.EMBEDDING)"
                        >{{ $t('views.document.fileStatus.EMBEDDING') }}
                      </el-dropdown-item>
                      <el-dropdown-item
                        :class="filterMethod['status'] === State.PENDING ? 'is-active' : ''"
                        class="justify-center"
                        :command="beforeCommand('status', State.PENDING)"
                        >{{ $t('views.document.fileStatus.PENDING') }}
                      </el-dropdown-item>
                      <el-dropdown-item
                        :class="
                          filterMethod['status'] === State.STARTED &&
                          filterMethod['task_type'] === TaskType.GENERATE_PROBLEM
                            ? 'is-active'
                            : ''
                        "
                        class="justify-center"
                        :command="beforeCommand('status', State.STARTED, TaskType.GENERATE_PROBLEM)"
                        >{{ $t('views.document.fileStatus.GENERATE') }}
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
            <template #default="{ row }">
              <StatusVlue :status="row.status" :status-meta="row.status_meta"></StatusVlue>
            </template>
          </el-table-column>
          <el-table-column width="130">
            <template #header>
              <div>
                <span>{{ $t('views.document.enableStatus.label') }}</span>
                <el-dropdown trigger="click" @command="dropdownHandle">
                  <el-button
                    style="margin-top: 1px"
                    link
                    :type="filterMethod['is_active'] ? 'primary' : ''"
                  >
                    <el-icon>
                      <Filter />
                    </el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu style="width: 100px">
                      <el-dropdown-item
                        :class="filterMethod['is_active'] === '' ? 'is-active' : ''"
                        :command="beforeCommand('is_active', '')"
                        class="justify-center"
                        >{{ $t('views.document.table.all') }}
                      </el-dropdown-item>
                      <el-dropdown-item
                        :class="filterMethod['is_active'] === true ? 'is-active' : ''"
                        class="justify-center"
                        :command="beforeCommand('is_active', true)"
                        >{{ $t('views.document.enableStatus.enable') }}
                      </el-dropdown-item>
                      <el-dropdown-item
                        :class="filterMethod['is_active'] === false ? 'is-active' : ''"
                        class="justify-center"
                        :command="beforeCommand('is_active', false)"
                        >{{ $t('views.document.enableStatus.close') }}
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
            <template #default="{ row }">
              <div @click.stop>
                <el-switch
                  :loading="loading"
                  size="small"
                  v-model="row.is_active"
                  :before-change="() => changeState(row)"
                />
              </div>
            </template>
          </el-table-column>
          <el-table-column width="170">
            <template #header>
              <div>
                <span>{{ $t('views.document.form.hit_handling_method.label') }}</span>
                <el-dropdown trigger="click" @command="dropdownHandle">
                  <el-button
                    style="margin-top: 1px"
                    link
                    :type="filterMethod['hit_handling_method'] ? 'primary' : ''"
                  >
                    <el-icon>
                      <Filter />
                    </el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu style="width: 150px">
                      <el-dropdown-item
                        :class="filterMethod['hit_handling_method'] ? '' : 'is-active'"
                        :command="beforeCommand('hit_handling_method', '')"
                        class="justify-center"
                        >{{ $t('views.document.table.all') }}
                      </el-dropdown-item>
                      <template v-for="(value, key) of hitHandlingMethod" :key="key">
                        <el-dropdown-item
                          :class="filterMethod['hit_handling_method'] === key ? 'is-active' : ''"
                          class="justify-center"
                          :command="beforeCommand('hit_handling_method', key)"
                          >{{ $t(value) }}
                        </el-dropdown-item>
                      </template>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
            <template #default="{ row }">
              {{ $t(hitHandlingMethod[row.hit_handling_method as keyof typeof hitHandlingMethod]) }}
            </template>
          </el-table-column>
          <el-table-column prop="create_time" :label="$t('common.createTime')" width="175" sortable>
            <template #default="{ row }">
              {{ datetimeFormat(row.create_time) }}
            </template>
          </el-table-column>
          <el-table-column
            prop="update_time"
            :label="$t('views.document.table.updateTime')"
            width="175"
            sortable
          >
            <template #default="{ row }">
              {{ datetimeFormat(row.update_time) }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('common.operation')" align="left" width="110" fixed="right">
            <template #default="{ row }">
              <div v-if="datasetDetail.type === '0'">
                <span class="mr-4">
                  <el-tooltip
                    effect="dark"
                    v-if="
                      ([State.STARTED, State.PENDING] as Array<string>).includes(
                        getTaskState(row.status, TaskType.EMBEDDING)
                      )
                    "
                    :content="$t('views.document.setting.cancelVectorization')"
                    placement="top"
                  >
                    <el-button
                      type="primary"
                      text
                      @click.stop="cancelTask(row, TaskType.EMBEDDING)"
                    >
                      <AppIcon iconName="app-close" style="font-size: 16px"></AppIcon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip
                    v-else
                    effect="dark"
                    :content="$t('views.dataset.setting.vectorization')"
                    placement="top"
                  >
                    <el-button type="primary" text @click.stop="refreshDocument(row)">
                      <AppIcon iconName="app-document-refresh" style="font-size: 16px"></AppIcon>
                    </el-button>
                  </el-tooltip>
                </span>
                <span class="mr-4">
                  <el-tooltip effect="dark" :content="$t('common.setting')" placement="top">
                    <el-button type="primary" text @click.stop="settingDoc(row)">
                      <el-icon><Setting /></el-icon>
                    </el-button>
                  </el-tooltip>
                </span>
                <span @click.stop>
                  <el-dropdown trigger="click">
                    <el-button text type="primary">
                      <el-icon><MoreFilled /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item
                          v-if="
                            ([State.STARTED, State.PENDING] as Array<string>).includes(
                              getTaskState(row.status, TaskType.GENERATE_PROBLEM)
                            )
                          "
                          @click="cancelTask(row, TaskType.GENERATE_PROBLEM)"
                        >
                          <el-icon><Connection /></el-icon>
                          {{ $t('views.document.setting.cancelGenerateQuestion') }}
                        </el-dropdown-item>
                        <el-dropdown-item v-else @click="openGenerateDialog(row)">
                          <el-icon><Connection /></el-icon>
                          {{ $t('views.document.generateQuestion.title') }}
                        </el-dropdown-item>
                        <el-dropdown-item @click="openDatasetDialog(row)">
                          <AppIcon iconName="app-migrate"></AppIcon>
                          {{ $t('views.document.setting.migration') }}
                        </el-dropdown-item>
                        <el-dropdown-item @click="exportDocument(row)">
                          <AppIcon iconName="app-export"></AppIcon>
                          {{ $t('views.document.setting.export') }} Excel
                        </el-dropdown-item>
                        <el-dropdown-item @click="exportDocumentZip(row)">
                          <AppIcon iconName="app-export"></AppIcon>
                          {{ $t('views.document.setting.export') }} Zip
                        </el-dropdown-item>
                        <el-dropdown-item icon="Delete" @click.stop="deleteDocument(row)">{{
                          $t('common.delete')
                        }}</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </span>
              </div>
              <div v-if="datasetDetail.type === '1' || datasetDetail.type === '2'">
                <span class="mr-4">
                  <el-tooltip
                    effect="dark"
                    :content="$t('views.dataset.setting.sync')"
                    placement="top"
                  >
                    <el-button type="primary" text @click.stop="syncDocument(row)">
                      <el-icon><Refresh /></el-icon>
                    </el-button>
                  </el-tooltip>
                </span>
                <span class="mr-4">
                  <el-tooltip
                    effect="dark"
                    v-if="
                      ([State.STARTED, State.PENDING] as Array<string>).includes(
                        getTaskState(row.status, TaskType.EMBEDDING)
                      )
                    "
                    :content="$t('views.document.setting.cancelVectorization')"
                    placement="top"
                  >
                    <el-button
                      type="primary"
                      text
                      @click.stop="cancelTask(row, TaskType.EMBEDDING)"
                    >
                      <AppIcon iconName="app-close" style="font-size: 16px"></AppIcon>
                    </el-button>
                  </el-tooltip>

                  <el-tooltip
                    effect="dark"
                    v-else
                    :content="$t('views.dataset.setting.vectorization')"
                    placement="top"
                  >
                    <el-button type="primary" text @click.stop="refreshDocument(row)">
                      <AppIcon iconName="app-document-refresh" style="font-size: 16px"></AppIcon>
                    </el-button>
                  </el-tooltip>
                </span>

                <span @click.stop>
                  <el-dropdown trigger="click">
                    <el-button text type="primary">
                      <el-icon><MoreFilled /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item icon="Setting" @click="settingDoc(row)">{{
                          $t('common.setting')
                        }}</el-dropdown-item>
                        <el-dropdown-item
                          v-if="
                            ([State.STARTED, State.PENDING] as Array<string>).includes(
                              getTaskState(row.status, TaskType.GENERATE_PROBLEM)
                            )
                          "
                          @click="cancelTask(row, TaskType.GENERATE_PROBLEM)"
                        >
                          <el-icon><Connection /></el-icon>
                          {{ $t('views.document.setting.cancelGenerateQuestion') }}
                        </el-dropdown-item>
                        <el-dropdown-item v-else @click="openGenerateDialog(row)">
                          <el-icon><Connection /></el-icon>
                          {{ $t('views.document.generateQuestion.title') }}
                        </el-dropdown-item>
                        <el-dropdown-item @click="openDatasetDialog(row)">
                          <AppIcon iconName="app-migrate"></AppIcon>
                          {{ $t('views.document.setting.migration') }}</el-dropdown-item
                        >
                        <el-dropdown-item @click="exportDocument(row)">
                          <AppIcon iconName="app-export"></AppIcon>
                          {{ $t('views.document.setting.export') }} Excel
                        </el-dropdown-item>
                        <el-dropdown-item @click="exportDocumentZip(row)">
                          <AppIcon iconName="app-export"></AppIcon>
                          {{ $t('views.document.setting.export') }} Zip
                        </el-dropdown-item>
                        <el-dropdown-item icon="Delete" @click.stop="deleteDocument(row)">{{
                          $t('common.delete')
                        }}</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </span>
              </div>
            </template>
          </el-table-column>
        </app-table>
      </div>

      <ImportDocumentDialog ref="ImportDocumentDialogRef" :title="title" @refresh="refresh" />
      <SyncWebDialog ref="SyncWebDialogRef" @refresh="refresh" />
      <!-- 选择知识库 -->
      <SelectDatasetDialog ref="SelectDatasetDialogRef" @refresh="refreshMigrate" />
      <GenerateRelatedDialog ref="GenerateRelatedDialogRef" @refresh="getList" />
    </div>
    <div class="mul-operation w-full flex" v-if="multipleSelection.length !== 0">
      <el-button :disabled="multipleSelection.length === 0" @click="cancelTaskHandle(1)">
        {{ $t('views.document.setting.cancelVectorization') }}
      </el-button>
      <el-button :disabled="multipleSelection.length === 0" @click="cancelTaskHandle(2)">
        {{ $t('views.document.setting.cancelGenerate') }}
      </el-button>
      <el-text type="info" class="secondary ml-24">
        {{ $t('views.document.selected') }} {{ multipleSelection.length }}
        {{ $t('views.document.items') }}
      </el-text>
      <el-button class="ml-16" type="primary" link @click="clearSelection">
        {{ $t('common.clear') }}
      </el-button>
    </div>
    <EmbeddingContentDialog ref="embeddingContentDialogRef"></EmbeddingContentDialog>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute, onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'
import { ElTable } from 'element-plus'
import documentApi from '@/api/document'
import ImportDocumentDialog from './component/ImportDocumentDialog.vue'
import SyncWebDialog from '@/views/dataset/component/SyncWebDialog.vue'
import SelectDatasetDialog from './component/SelectDatasetDialog.vue'
import { numberFormat } from '@/utils/utils'
import { datetimeFormat } from '@/utils/time'
import { hitHandlingMethod } from '@/enums/document'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import useStore from '@/stores'
import StatusVlue from '@/views/document/component/Status.vue'
import GenerateRelatedDialog from '@/components/generate-related-dialog/index.vue'
import EmbeddingContentDialog from '@/views/document/component/EmbeddingContentDialog.vue'
import { TaskType, State } from '@/utils/status'
import { t } from '@/locales'

const router = useRouter()
const route = useRoute()
const {
  params: { id } // id为datasetID
} = route as any

const { common, dataset, document } = useStore()
const storeKey = 'documents'
const getTaskState = (status: string, taskType: number) => {
  const statusList = status.split('').reverse()
  return taskType - 1 > statusList.length + 1 ? 'n' : statusList[taskType - 1]
}
onBeforeRouteUpdate(() => {
  common.savePage(storeKey, null)
  common.saveCondition(storeKey, null)
})
onBeforeRouteLeave((to: any) => {
  if (to.name !== 'Paragraph') {
    common.savePage(storeKey, null)
    common.saveCondition(storeKey, null)
  } else {
    common.saveCondition(storeKey, {
      filterText: filterText.value,
      filterMethod: filterMethod.value
    })
  }
})
const beforePagination = computed(() => common.paginationConfig[storeKey])
const beforeSearch = computed(() => common.search[storeKey])
const embeddingContentDialogRef = ref<InstanceType<typeof EmbeddingContentDialog>>()
const SyncWebDialogRef = ref()
const loading = ref(false)
let interval: any
const filterText = ref('')
const filterMethod = ref<any>({})
const orderBy = ref<string>('')
const documentData = ref<any[]>([])
const currentMouseId = ref(null)
const datasetDetail = ref<any>({})

const paginationConfig = ref({
  current_page: 1,
  page_size: 10,
  total: 0
})

const ImportDocumentDialogRef = ref()
const multipleTableRef = ref<InstanceType<typeof ElTable>>()
const multipleSelection = ref<any[]>([])
const title = ref('')

const SelectDatasetDialogRef = ref()

const exportDocument = (document: any) => {
  documentApi.exportDocument(document.name, document.dataset_id, document.id, loading).then(() => {
    MsgSuccess(t('common.exportSuccess'))
  })
}
const exportDocumentZip = (document: any) => {
  documentApi
    .exportDocumentZip(document.name, document.dataset_id, document.id, loading)
    .then(() => {
      MsgSuccess(t('common.exportSuccess'))
    })
}

function cancelTaskHandle(val: any) {
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  const obj = {
    id_list: arr,
    type: val
  }
  documentApi.batchCancelTask(id, obj, loading).then(() => {
    MsgSuccess(t('views.document.tip.cancelSuccess'))
    multipleTableRef.value?.clearSelection()
  })
}

function clearSelection() {
  multipleTableRef.value?.clearSelection()
}

function openDatasetDialog(row?: any) {
  const arr: string[] = []
  if (row) {
    arr.push(row.id)
  } else {
    multipleSelection.value.map((v) => {
      if (v) {
        arr.push(v.id)
      }
    })
  }

  SelectDatasetDialogRef.value.open(arr)
}

function dropdownHandle(obj: any) {
  filterMethod.value[obj.attr] = obj.command
  if (obj.attr == 'status') {
    filterMethod.value['task_type'] = obj.task_type
  }

  getList()
}

function beforeCommand(attr: string, val: any, task_type?: number) {
  return {
    attr: attr,
    command: val,
    task_type
  }
}

const cancelTask = (row: any, task_type: number) => {
  documentApi.cancelTask(row.dataset_id, row.id, { type: task_type }).then(() => {
    MsgSuccess(t('views.document.tip.sendMessage'))
  })
}

function importDoc() {
  title.value = t('views.document.importDocument')
  ImportDocumentDialogRef.value.open()
}

function settingDoc(row: any) {
  title.value = t('common.setting')
  ImportDocumentDialogRef.value.open(row)
}

const handleSelectionChange = (val: any[]) => {
  multipleSelection.value = val
}

function openBatchEditDocument() {
  title.value = t('common.setting')
  const arr: string[] = multipleSelection.value.map((v) => v.id)
  ImportDocumentDialogRef.value.open(null, arr)
}

/**
 * 初始化轮询
 */
const initInterval = () => {
  interval = setInterval(() => {
    getList(true)
  }, 6000)
}

/**
 * 关闭轮询
 */
const closeInterval = () => {
  if (interval) {
    clearInterval(interval)
  }
}

function syncDocument(row: any) {
  console.log('row', row)
  if (row.type === '1') {
    syncWebDocument(row)
  } else {
    syncLarkDocument(row)
  }
}

function syncLarkDocument(row: any) {
  MsgConfirm(t('views.document.sync.confirmTitle'), t('views.document.sync.confirmMessage1'), {
    confirmButtonText: t('views.document.sync.label'),
    confirmButtonClass: 'danger'
  })
    .then(() => {
      documentApi.putLarkDocumentSync(id, row.id).then(() => {
        getList()
      })
    })
    .catch(() => {})
}

function syncWebDocument(row: any) {
  if (row.meta?.source_url) {
    MsgConfirm(t('views.document.sync.confirmTitle'), t('views.document.sync.confirmMessage1'), {
      confirmButtonText: t('views.document.sync.label'),
      confirmButtonClass: 'danger'
    })
      .then(() => {
        documentApi.putDocumentSync(row.dataset_id, row.id).then(() => {
          getList()
        })
      })
      .catch(() => {})
  } else {
    MsgConfirm(t('common.tip'), t('views.document.sync.confirmMessage2'), {
      confirmButtonText: t('common.confirm'),
      type: 'warning'
    })
      .then(() => {})
      .catch(() => {})
  }
}

function refreshDocument(row: any) {
  const embeddingDocument = (stateList: Array<string>) => {
    return documentApi.putDocumentRefresh(row.dataset_id, row.id, stateList).then(() => {
      getList()
    })
  }
  embeddingContentDialogRef.value?.open(embeddingDocument)
}

function rowClickHandle(row: any, column: any) {
  if (column && column.type === 'selection') {
    return
  }

  router.push({ path: `/dataset/${id}/${row.id}` })
}

/*
  快速创建空白文档
*/
function creatQuickHandle(val: string) {
  loading.value = true
  const obj = [{ name: val }]
  document
    .asyncPostDocument(id, obj)
    .then(() => {
      getList()
      MsgSuccess(t('common.createSuccess'))
    })
    .catch(() => {
      loading.value = false
    })
}

function syncMulDocument() {
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  documentApi.delMulSyncDocument(id, arr, loading).then(() => {
    MsgSuccess(t('views.document.sync.successMessage'))
    getList()
  })
}

function syncLarkMulDocument() {
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  documentApi.delMulLarkSyncDocument(id, arr, loading).then(() => {
    MsgSuccess(t('views.document.sync.successMessage'))
    getList()
  })
}

function deleteMulDocument() {
  MsgConfirm(
    `${t('views.document.delete.confirmTitle1')} ${multipleSelection.value.length} ${t('views.document.delete.confirmTitle2')}`,
    t('views.document.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      const arr: string[] = []
      multipleSelection.value.map((v) => {
        if (v) {
          arr.push(v.id)
        }
      })
      documentApi.delMulDocument(id, arr, loading).then(() => {
        MsgSuccess(t('views.document.delete.successMessage'))
        multipleTableRef.value?.clearSelection()
        getList()
      })
    })
    .catch(() => {})
}

function batchRefresh() {
  const arr: string[] = multipleSelection.value.map((v) => v.id)
  const embeddingBatchDocument = (stateList: Array<string>) => {
    documentApi.batchRefresh(id, arr, stateList, loading).then(() => {
      MsgSuccess(t('views.document.tip.vectorizationSuccess'))
      multipleTableRef.value?.clearSelection()
    })
  }
  embeddingContentDialogRef.value?.open(embeddingBatchDocument)
}

function deleteDocument(row: any) {
  MsgConfirm(
    `${t('views.document.delete.confirmTitle3')} ${row.name} ?`,
    `${t('views.document.delete.confirmMessage1')} ${row.paragraph_count} ${t('views.document.delete.confirmMessage2')}`,
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      documentApi.delDocument(id, row.id, loading).then(() => {
        MsgSuccess(t('common.deleteSuccess'))
        getList()
      })
    })
    .catch(() => {})
}

/*
  更新名称或状态
*/
function updateData(documentId: string, data: any, msg: string) {
  documentApi
    .putDocument(id, documentId, data, loading)
    .then((res) => {
      const index = documentData.value.findIndex((v) => v.id === documentId)
      documentData.value.splice(index, 1, res.data)
      MsgSuccess(msg)
      return true
    })
    .catch(() => {
      return false
    })
}

function changeState(row: any) {
  const obj = {
    is_active: !row.is_active
  }
  const str = !row.is_active ? t('common.status.enableSuccess') : t('common.status.disableSuccess')
  currentMouseId.value && updateData(row.id, obj, str)
}

function editName(val: string, id: string) {
  if (val) {
    const obj = {
      name: val
    }
    updateData(id, obj, t('common.modifySuccess'))
  } else {
    MsgError(t('views.document.tip.nameMessage'))
  }
}

function cellMouseEnter(row: any) {
  currentMouseId.value = row.id
}

function cellMouseLeave() {
  currentMouseId.value = null
}

function handleSizeChange() {
  paginationConfig.value.current_page = 1
  getList()
}

function handleSortChange({ prop, order }: { prop: string; order: string }) {
  orderBy.value = order === 'ascending' ? prop : `-${prop}`
  getList()
}

function getList(bool?: boolean) {
  const param = {
    ...(filterText.value && { name: filterText.value }),
    ...filterMethod.value,
    order_by: orderBy.value
  }
  documentApi
    .getDocument(id as string, paginationConfig.value, param, bool ? undefined : loading)
    .then((res) => {
      documentData.value = res.data.records
      paginationConfig.value.total = res.data.total
    })
}

function getDetail() {
  dataset.asyncGetDatasetDetail(id, loading).then((res: any) => {
    datasetDetail.value = res.data
  })
}

function refreshMigrate() {
  multipleTableRef.value?.clearSelection()
  getList()
}

function refresh() {
  paginationConfig.value.current_page = 1
  getList()
}

const GenerateRelatedDialogRef = ref()

function openGenerateDialog(row?: any) {
  const arr: string[] = []
  if (row) {
    arr.push(row.id)
  } else {
    multipleSelection.value.map((v) => {
      if (v) {
        arr.push(v.id)
      }
    })
  }

  GenerateRelatedDialogRef.value.open(arr, 'document')
}

onMounted(() => {
  getDetail()
  if (beforePagination.value) {
    paginationConfig.value = beforePagination.value
  }
  if (beforeSearch.value) {
    filterText.value = beforeSearch.value['filterText']
    filterMethod.value = beforeSearch.value['filterMethod']
  }
  getList()
  // 初始化定时任务
  initInterval()
})

onBeforeUnmount(() => {
  // 清除定时任务
  closeInterval()
})
</script>
<style lang="scss" scoped>
.document-main {
  box-sizing: border-box;

  .mul-operation {
    position: fixed;
    margin-left: var(--sidebar-width);
    bottom: 0;
    right: 24px;
    width: calc(100% - var(--sidebar-width) - 48px);
    padding: 16px 24px;
    box-sizing: border-box;
    background: #ffffff;
    z-index: 22;
    box-shadow: 0px -2px 4px 0px rgba(31, 35, 41, 0.08);
  }
}
</style>
