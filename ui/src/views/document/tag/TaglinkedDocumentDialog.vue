<template>
  <el-dialog v-model="dialogVisible" :before-close="close" append-to-body destroy-on-close>
    <template #header>
      <h4>{{ $t('views.document.tag.tagLinkTitle') }}</h4>
    </template>
    <div>
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane :label="$t('views.document.tag.relatedDoc')" name="linked" />
        <el-tab-pane :label="$t('views.document.tag.unrelatedDoc')" name="unlinked" />
      </el-tabs>
    </div>
    <div class="flex-between">
      <el-button :disabled="multipleSelection.length === 0 || loading" @click="batchOperate">{{
        activeTab === 'linked' ? $t('views.document.tag.unrelate') : $t('views.document.tag.relate')
      }}</el-button>

      <el-input
        v-model="filterText"
        prefix-icon="Search"
        class="w-240"
        @change="handleSearch"
        clearable
        :placeholder="$t('common.search')"
      />
    </div>
    <app-table
      ref="multipleTableRef"
      :pagination-config="paginationConfig"
      @sizeChange="handleSizeChange"
      @changePage="getList"
      :data="tableData"
      :row-key="(row: any) => row.id"
      class="mt-16 document-table"
      @selection-change="handleSelectionChange"
      v-loading="loading"
    >
      <el-table-column type="selection" width="55" :reserve-selection="true" v-if="!isShared" />
      <el-table-column prop="name" :label="$t('views.document.table.name')" min-width="280">
        <template #default="{ row }">
          <span>{{ row.name }}</span>
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
                    >{{ $t('common.status.all') }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    :class="filterMethod['is_active'] === true ? 'is-active' : ''"
                    class="justify-center"
                    :command="beforeCommand('is_active', true)"
                    >{{ $t('common.status.enabled') }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    :class="filterMethod['is_active'] === false ? 'is-active' : ''"
                    class="justify-center"
                    :command="beforeCommand('is_active', false)"
                    >{{ $t('common.status.disabled') }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </template>
        <template #default="{ row }">
          <div v-if="row.is_active" class="flex align-center">
            <el-icon class="color-success mr-8" style="font-size: 16px">
              <SuccessFilled />
            </el-icon>
            <span class="color-text-primary">
              {{ $t('common.status.enabled') }}
            </span>
          </div>
          <div v-else class="flex align-center">
            <AppIcon iconName="app-disabled" class="color-secondary mr-8"></AppIcon>
            <span class="color-text-primary">
              {{ $t('common.status.disabled') }}
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" :label="$t('common.createTime')" width="175" sortable>
        <template #default="{ row }">
          {{ datetimeFormat(row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column
        :label="$t('common.operation')"
        align="left"
        width="80"
        fixed="right"
        v-if="!isShared"
      >
        <template #default="{ row }">
          <el-tooltip
            v-if="activeTab === 'linked'"
            effect="dark"
            :content="$t('views.document.tag.unrelate')"
            placement="top"
          >
            <span class="mr-4">
              <el-button type="primary" text @click.stop="rowOperate(row)">
                <AppIcon iconName="app-unlink"></AppIcon>
              </el-button>
            </span>
          </el-tooltip>
          <el-tooltip
            v-else
            effect="dark"
            :content="$t('views.document.tag.relate')"
            placement="top"
          >
            <span class="mr-4">
              <el-button type="primary" text @click.stop="rowOperate(row)">
                <AppIcon iconName="app-generate-question"></AppIcon>
              </el-button>
            </span>
          </el-tooltip>
        </template>
      </el-table-column>
    </app-table>
  </el-dialog>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api.ts'
import { cloneDeep } from 'lodash'
import type { ElTable } from 'element-plus'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import type { TabPaneName } from 'element-plus'

const route = useRoute()
const {
  params: { id, folderId, type }, // id为knowledgeID
} = route as any
const emit = defineEmits(['refresh'])

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const isShared = computed(() => {
  return folderId === 'share'
})
const loading = ref(false)
const dialogVisible = ref<boolean>(false)

type TabType = 'linked' | 'unlinked'

const activeTab = ref<TabType>('linked')

function handleTabChange(tabName: TabPaneName) {
  activeTab.value = (tabName as TabType) || 'linked'
  resetPage()
  multipleSelection.value = []
  multipleTableRef.value?.clearSelection()
  filterMethod.value = {}
  filterText.value = ''
  getList()
}

function handleSearch() {
  resetPage()
  getList()
}

const paginationConfig = ref({
  current_page: 1,
  page_size: 10,
  total: 0,
})
const filterText = ref<string>('')
const currentTag = ref<any>({})
const tableData = ref<Array<any>>([])
const multipleSelection = ref<any[]>([])
const multipleTableRef = ref<InstanceType<typeof ElTable>>()

const filterMethod = ref<any>({})
const orderBy = ref<string>('')

function dropdownHandle(obj: any) {
  filterMethod.value = {
    ...filterMethod.value,
    [obj.attr]: obj.command,
  }
  resetPage()
  getList()
}

function beforeCommand(attr: string, val: any, task_type?: number) {
  return {
    attr: attr,
    command: val,
    task_type,
  }
}

const handleSelectionChange = (val: any[]) => {
  multipleSelection.value = val
}

function afterOperateSuccess() {
  multipleSelection.value = []
  multipleTableRef.value?.clearSelection()
  resetPage()
  getList()
  emit('refresh')
}

function operate(docIds: string[]) {
  if (!currentTag.value?.id || docIds.length === 0) return

  const res = activeTab.value === 'linked' ? unrelateDocuments(docIds) : relateDocuments(docIds)
  res.then(() => {
    MsgSuccess(t('common.settingSuccess'))
    afterOperateSuccess()
  })
}

function handleSizeChange() {
  paginationConfig.value.current_page = 1
  getList()
}

function batchOperate() {
  if (!currentTag.value.id || multipleSelection.value.length === 0) return

  const docIds = multipleSelection.value.map((item: any) => item.id)
  operate(docIds)
}

function rowOperate(row: any) {
  if (!currentTag.value?.id) return
  operate([row.id])
}

function relateDocuments(doc_ids: string[]) {
  return loadSharedApi({
    type: 'document',
    isShared: isShared.value,
    systemType: apiType.value,
  }).postMulDocumentTags(
    id as string,
    { tag_ids: [currentTag.value.id], document_ids: doc_ids },
    loading,
  )
}

function unrelateDocuments(doc_ids: string[]) {
  return loadSharedApi({
    type: 'document',
    isShared: isShared.value,
    systemType: apiType.value,
  }).delDocsTag(id as string, currentTag.value.id, doc_ids, loading)
}

function resetPage() {
  paginationConfig.value.current_page = 1
}

function getList() {
  if (!currentTag.value?.id) {
    tableData.value = []
    paginationConfig.value.total = 0
    return
  }
  multipleSelection.value = []
  const params = {
    ...filterMethod.value,
    folder_id: folderId,
    order_by: orderBy.value,
    'tags[]': [currentTag.value.id],
  }
  if (filterText.value) {
    params.name = filterText.value
  }
  if (activeTab.value === 'unlinked') {
    params.tag_exclude = true
  }

  loadSharedApi({ type: 'document', isShared: isShared.value, systemType: apiType.value })
    .getDocumentPage(id as string, paginationConfig.value, params, loading)
    .then((res: any) => {
      tableData.value = res?.data?.records || []
      paginationConfig.value.total = res?.data?.total || 0
    })
}

const open = (row?: any) => {
  filterText.value = ''
  filterMethod.value = {}
  activeTab.value = 'linked'
  orderBy.value = ''
  tableData.value = []
  multipleSelection.value = []
  multipleTableRef.value?.clearSelection()
  paginationConfig.value = {
    current_page: 1,
    page_size: 10,
    total: 0,
  }
  currentTag.value = cloneDeep(row || {})
  dialogVisible.value = true
  getList()
}

const close = () => {
  multipleSelection.value = []
  multipleTableRef.value?.clearSelection()
  dialogVisible.value = false
}

defineExpose({ open, close })
</script>
<style lang="scss" scoped>
.tag-list-max-list {
  max-height: calc(100vh - 260px);
}
</style>
