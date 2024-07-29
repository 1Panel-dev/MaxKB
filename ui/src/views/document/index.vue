<template>
  <LayoutContainer header="文档">
    <div class="main-calc-height">
      <div class="p-24">
        <div class="flex-between">
          <div>
            <el-button
              v-if="datasetDetail.type === '0'"
              type="primary"
              @click="router.push({ path: '/dataset/upload', query: { id: id } })"
              >上传文档</el-button
            >
            <el-button v-if="datasetDetail.type === '1'" type="primary" @click="importDoc"
              >导入文档</el-button
            >
            <el-button @click="syncDataset" v-if="datasetDetail.type === '1'">同步知识库</el-button>
            <el-button
              @click="syncMulDocument"
              :disabled="multipleSelection.length === 0"
              v-if="datasetDetail.type === '1'"
              >同步文档</el-button
            >
            <el-button @click="openDatasetDialog()" :disabled="multipleSelection.length === 0">
              迁移
            </el-button>
            <el-button @click="openBatchEditDocument" :disabled="multipleSelection.length === 0">
              设置
            </el-button>
            <el-button @click="deleteMulDocument" :disabled="multipleSelection.length === 0">
              删除
            </el-button>
          </div>

          <el-input
            v-model="filterText"
            placeholder="按 文档名称 搜索"
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
          v-loading="loading"
          :row-key="(row: any) => row.id"
          :storeKey="storeKey"
        >
          <el-table-column type="selection" width="55" :reserve-selection="true" />
          <el-table-column prop="name" label="文件名称" min-width="280">
            <template #default="{ row }">
              <ReadWrite
                @change="editName($event, row.id)"
                :data="row.name"
                :showEditIcon="row.id === currentMouseId"
              />
            </template>
          </el-table-column>
          <el-table-column prop="char_length" label="字符数" align="right">
            <template #default="{ row }">
              {{ numberFormat(row.char_length) }}
            </template>
          </el-table-column>
          <el-table-column prop="paragraph_count" label="分段" align="right" />
          <el-table-column prop="status" label="文件状态" min-width="90">
            <template #default="{ row }">
              <el-text v-if="row.status === '1'">
                <el-icon class="success"><SuccessFilled /></el-icon> 成功
              </el-text>
              <el-text v-else-if="row.status === '2'">
                <el-icon class="danger"><CircleCloseFilled /></el-icon> 失败
              </el-text>
              <el-text v-else-if="row.status === '0'">
                <el-icon class="is-loading primary"><Loading /></el-icon> 索引中
              </el-text>
              <el-text v-else-if="row.status === '3'">
                <el-icon class="is-loading primary"><Loading /></el-icon>排队中
              </el-text>
            </template>
          </el-table-column>
          <el-table-column label="启用状态">
            <template #default="{ row }">
              <div @click.stop>
                <el-switch
                  size="small"
                  v-model="row.is_active"
                  @change="changeState($event, row)"
                />
              </div>
            </template>
          </el-table-column>
          <el-table-column width="130">
            <template #header>
              <div>
                <span>命中处理方式</span>
                <el-dropdown trigger="click" @command="dropdownHandle">
                  <el-button style="margin-top: 1px" link :type="filterMethod ? 'primary' : ''">
                    <el-icon><Filter /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu style="width: 100px">
                      <el-dropdown-item
                        :class="filterMethod ? '' : 'is-active'"
                        command=""
                        class="justify-center"
                        >全部</el-dropdown-item
                      >
                      <template v-for="(value, key) of hitHandlingMethod" :key="key">
                        <el-dropdown-item
                          :class="filterMethod === key ? 'is-active' : ''"
                          class="justify-center"
                          :command="key"
                          >{{ value }}</el-dropdown-item
                        >
                      </template>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
            <template #default="{ row }">
              {{ hitHandlingMethod[row.hit_handling_method as keyof typeof hitHandlingMethod] }}
            </template>
          </el-table-column>
          <el-table-column prop="create_time" label="创建时间" width="175">
            <template #default="{ row }">
              {{ datetimeFormat(row.create_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="update_time" label="更新时间" width="175">
            <template #default="{ row }">
              {{ datetimeFormat(row.update_time) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" align="left" width="110" fixed="right">
            <template #default="{ row }">
              <div v-if="datasetDetail.type === '0'">
                <span class="mr-4">
                  <el-tooltip effect="dark" content="重新向量化" placement="top">
                    <el-button type="primary" text @click.stop="refreshDocument(row)">
                      <AppIcon iconName="app-document-refresh" style="font-size: 16px"></AppIcon>
                    </el-button>
                  </el-tooltip>
                </span>
                <span @click.stop>
                  <el-dropdown trigger="click">
                    <el-button text>
                      <el-icon><MoreFilled /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item @click="settingDoc(row)">
                          <el-icon><Setting /></el-icon>
                          设置
                        </el-dropdown-item>
                        <el-dropdown-item @click="openDatasetDialog(row)">
                          <AppIcon iconName="app-migrate"></AppIcon>
                          迁移
                        </el-dropdown-item>
                        <el-dropdown-item @click="exportDocument(row)">
                          <AppIcon iconName="app-export"></AppIcon>
                          导出
                        </el-dropdown-item>
                        <el-dropdown-item icon="Delete" @click.stop="deleteDocument(row)"
                          >删除</el-dropdown-item
                        >
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </span>
              </div>
              <div v-if="datasetDetail.type === '1'">
                <el-tooltip effect="dark" content="同步" placement="top">
                  <el-button type="primary" text @click.stop="syncDocument(row)">
                    <el-icon><Refresh /></el-icon>
                  </el-button>
                </el-tooltip>
                <span @click.stop>
                  <el-dropdown trigger="click">
                    <el-button text>
                      <el-icon><MoreFilled /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item @click="refreshDocument(row)">
                          <AppIcon
                            iconName="app-document-refresh"
                            style="font-size: 16px"
                          ></AppIcon>
                          重新向量化</el-dropdown-item
                        >
                        <el-dropdown-item icon="Setting" @click="settingDoc(row)"
                          >设置</el-dropdown-item
                        >
                        <el-dropdown-item @click="openDatasetDialog(row)">
                          <AppIcon iconName="app-migrate"></AppIcon>
                          迁移</el-dropdown-item
                        >
                        <el-dropdown-item @click="exportDocument(row)">
                          <AppIcon iconName="app-export"></AppIcon>
                          导出
                        </el-dropdown-item>
                        <el-dropdown-item icon="Delete" @click.stop="deleteDocument(row)"
                          >删除</el-dropdown-item
                        >
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
    </div>
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
const router = useRouter()
const route = useRoute()
const {
  params: { id } // id为datasetID
} = route as any

const { common, dataset, document } = useStore()

const storeKey = 'documents'

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

const SyncWebDialogRef = ref()
const loading = ref(false)
let interval: any
const filterText = ref('')
const filterMethod = ref<string | number>('')
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
    MsgSuccess('导出成功')
  })
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

function dropdownHandle(val: string) {
  filterMethod.value = val
  getList()
}

function syncDataset() {
  SyncWebDialogRef.value.open(id)
}

function importDoc() {
  title.value = '导入文档'
  ImportDocumentDialogRef.value.open()
}
function settingDoc(row: any) {
  title.value = '设置'
  ImportDocumentDialogRef.value.open(row)
}

const handleSelectionChange = (val: any[]) => {
  multipleSelection.value = val
}

function openBatchEditDocument() {
  title.value = '设置'
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
  if (row.meta?.source_url) {
    MsgConfirm(`确认同步文档?`, `同步将删除已有数据重新获取新数据，请谨慎操作。`, {
      confirmButtonText: '同步',
      confirmButtonClass: 'danger'
    })
      .then(() => {
        documentApi.putDocumentSync(row.dataset_id, row.id).then(() => {
          getList()
        })
      })
      .catch(() => {})
  } else {
    MsgConfirm(`提示`, `无法同步，请先去设置文档 URL地址`, {
      confirmButtonText: '确认',
      type: 'warning'
    })
      .then(() => {})
      .catch(() => {})
  }
}
function refreshDocument(row: any) {
  documentApi.putDocumentRefresh(row.dataset_id, row.id).then(() => {
    getList()
  })
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
      MsgSuccess('创建成功')
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
    MsgSuccess('同步文档成功')
    getList()
  })
}

function deleteMulDocument() {
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  documentApi.delMulDocument(id, arr, loading).then(() => {
    MsgSuccess('批量删除成功')
    multipleTableRef.value?.clearSelection()
    getList()
  })
}

function deleteDocument(row: any) {
  MsgConfirm(
    `是否删除文档：${row.name} ?`,
    `此文档下的 ${row.paragraph_count} 个分段都会被删除，请谨慎操作。`,
    {
      confirmButtonText: '删除',
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      documentApi.delDocument(id, row.id, loading).then(() => {
        MsgSuccess('删除成功')
        getList()
      })
    })
    .catch(() => {})
}

/*
  更新名称或状态
*/
function updateData(documentId: string, data: any, msg: string) {
  documentApi.putDocument(id, documentId, data, loading).then((res) => {
    const index = documentData.value.findIndex((v) => v.id === documentId)
    documentData.value.splice(index, 1, res.data)
    MsgSuccess(msg)
  })
}

function changeState(bool: Boolean, row: any) {
  const obj = {
    is_active: bool
  }
  const str = bool ? '启用成功' : '禁用成功'
  currentMouseId.value && updateData(row.id, obj, str)
}

function editName(val: string, id: string) {
  if (val) {
    const obj = {
      name: val
    }
    updateData(id, obj, '修改成功')
  } else {
    MsgError('文件名称不能为空！')
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

function getList(bool?: boolean) {
  const param = {
    ...(filterText.value && { name: filterText.value }),
    ...(filterMethod.value && { hit_handling_method: filterMethod.value })
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
<style lang="scss" scoped></style>
