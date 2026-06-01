<template>
  <div class="document p-16-24">
    <h2 class="flex align-center mb-16">
      {{ $t('views.knowledge.customSegmentation.title') }}
      <el-tooltip
        effect="dark"
        :content="$t('views.knowledge.customSegmentation.tip')"
        placement="right"
      >
        <AppIcon iconName="app-problems" class="color-secondary ml-4"></AppIcon>
      </el-tooltip>
    </h2>
    <el-card style="--el-card-padding: 0">
      <div class="main-calc-height">
        <div class="p-24">
          <div class="flex-between">
            <div>
              <el-button
                type="primary"
                @click="createTermbase"
                v-if="permissionPrecise.termbase_create(id)"
              >
                {{ $t('views.knowledge.customSegmentation.create') }}
              </el-button>
              <el-button
                @click="deleteMulDocument"
                :disabled="multipleSelection.length === 0"
                v-if="permissionPrecise.termbase_delete(id)"
              >
                {{ $t('views.problem.setting.batchDelete') }}
              </el-button>
              <el-button @click="exportMulTermbase" :disabled="multipleSelection.length === 0">
                {{ $t('common.export') }}
              </el-button>
            </div>

            <el-input
              v-model="filterText"
              :placeholder="$t('common.searchBar.placeholder')"
              prefix-icon="Search"
              class="w-240"
              @change="getList"
              clearable
            />
          </div>
          <app-table
            ref="multipleTableRef"
            class="mt-16"
            :data="termbaseData"
            :pagination-config="paginationConfig"
            :quick-create="permissionPrecise.termbase_create(id)"
            :quickCreateName="$t('views.knowledge.customSegmentation.quickCreate')"
            :quickCreatePlaceholder="$t('views.knowledge.customSegmentation.quickCreate')"
            :quickCreateMaxlength="256"
            @sizeChange="handleSizeChange"
            @changePage="getList"
            @cell-mouse-enter="cellMouseEnter"
            @cell-mouse-leave="cellMouseLeave"
            @creatQuick="creatQuickHandle"
            @selection-change="handleSelectionChange"
            :row-class-name="setRowClass"
            v-loading="loading"
            :row-key="(row: any) => row.id"
          >
            <el-table-column type="selection" width="55" :reserve-selection="true" />
            <el-table-column
              prop="content"
              :label="$t('views.knowledge.customSegmentation.word')"
              min-width="280"
            >
              <template #default="{ row }">
                <ReadWrite
                  @change="editName($event, row.id)"
                  :data="row.content"
                  :showEditIcon="permissionPrecise.termbase_edit(id) && row.id === currentMouseId"
                  :maxlength="256"
                />
              </template>
            </el-table-column>
            <el-table-column prop="create_time" :label="$t('common.createTime')" width="170">
              <template #default="{ row }">
                {{ datetimeFormat(row.create_time) }}
              </template>
            </el-table-column>
            <el-table-column
              prop="update_time"
              :label="$t('views.problem.table.updateTime')"
              width="170"
            >
              <template #default="{ row }">
                {{ datetimeFormat(row.update_time) }}
              </template>
            </el-table-column>
            <el-table-column :label="$t('common.operation')" align="left" fixed="right">
              <template #default="{ row }">
                <div>
                  <span>
                    <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
                      <el-button
                        type="primary"
                        text
                        @click.stop="deleteTermbase(row)"
                        v-if="permissionPrecise.termbase_delete(id)"
                      >
                        <AppIcon iconName="app-delete"></AppIcon>
                      </el-button>
                    </el-tooltip>
                  </span>
                </div>
              </template>
            </el-table-column>
          </app-table>
        </div>
      </div>
    </el-card>
    <CreateTermBaseDialog ref="CreateTermbaseDialogRef" @refresh="refresh" />
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { TableInstance } from 'element-plus'
import CreateTermBaseDialog from './component/CreateTermbaseDialog.vue'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import type { Dict } from '@/api/type/common'
import { t } from '@/locales'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import permissionMap from '@/permission'

const route = useRoute()
const {
  params: { id, folderId }, // 知识库id
} = route as any

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else if (route.path.includes('share/')) {
    return 'workspaceShare'
  } else {
    return 'workspace'
  }
})
const permissionPrecise = computed(() => {
  return permissionMap['knowledge'][apiType.value]
})

const isShared = computed(() => {
  return folderId === 'share'
})

const CreateTermbaseDialogRef = ref()
const loading = ref(false)

// 当前需要修改问题的id
const currentMouseId = ref('')
// 当前点击打开drawer的id
const currentClickId = ref('')
const currentContent = ref('')

const paginationConfig = reactive({
  current_page: 1,
  page_size: 10,
  total: 0,
  page_sizes: [10, 20, 50, 100, 1000],
})

const filterText = ref('')
const termbaseData = ref<any[]>([])

const multipleTableRef = ref<TableInstance>()
const multipleSelection = ref<any[]>([])

function exportMulTermbase(row?: any) {
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  loadSharedApi({ type: 'termbase', systemType: apiType.value })
    .exportMulTermbase(id, arr, loading)
    .then((res: any) => {
      const blob = new Blob([res.data], { type: 'text/plain;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'termbase_export.txt'
      a.click()
      URL.revokeObjectURL(url)
      multipleTableRef.value?.clearSelection()
    })
}

function createTermbase() {
  CreateTermbaseDialogRef.value.open()
}

const handleSelectionChange = (val: any[]) => {
  multipleSelection.value = val
}

/*
  快速创建空白文档
*/
function creatQuickHandle(val: string) {
  loading.value = true
  const obj = [val]
  loadSharedApi({ type: 'termbase', systemType: apiType.value })
    .postTermbase(id, obj)
    .then(() => {
      getList()
      MsgSuccess(t('common.createSuccess'))
    })
    .catch(() => {
      loading.value = false
    })
}

function deleteMulDocument() {
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  loadSharedApi({ type: 'termbase', systemType: apiType.value })
    .putMulTermbase(id, arr, loading)
    .then(() => {
      MsgSuccess(t('views.document.delete.successMessage'))
      multipleTableRef.value?.clearSelection()
      getList()
    })
}

function deleteTermbase(row: any) {
  loadSharedApi({ type: 'termbase', systemType: apiType.value })
    .delTermbase(id, row.id, loading)
    .then(() => {
      MsgSuccess(t('common.deleteSuccess'))
      getList()
    })
}

function editName(val: string, termbaseId: string) {
  if (val) {
    const obj = {
      content: val,
    }
    loadSharedApi({ type: 'termbase', systemType: apiType.value })
      .putTermbase(id, termbaseId, obj, loading)
      .then(() => {
        getList()
        MsgSuccess(t('common.modifySuccess'))
      })
  } else {
    MsgError(t('views.problem.tip.errorMessage'))
  }
}

function cellMouseEnter(row: any, column: any) {
  if (column && column.property === 'content') {
    currentMouseId.value = row.id
  }
}

function cellMouseLeave() {
  currentMouseId.value = ''
}

const setRowClass = ({ row }: any) => {
  return currentClickId.value === row?.id ? 'highlight' : ''
}

function handleSizeChange() {
  paginationConfig.current_page = 1
  getList()
}

function getList() {
  return loadSharedApi({ type: 'termbase', isShared: isShared.value, systemType: apiType.value })
    .getTermbasePage(
      id as string,
      paginationConfig,
      filterText.value && { content: filterText.value },
      loading,
    )
    .then((res: any) => {
      termbaseData.value = res.data.records
      paginationConfig.total = res.data.total
    })
}

function refreshRelate() {
  getList()
  multipleTableRef.value?.clearSelection()
}

function refresh() {
  paginationConfig.current_page = 1
  getList()
}

onMounted(() => {
  getList()
})

onBeforeUnmount(() => {})
</script>
<style lang="scss" scoped></style>
