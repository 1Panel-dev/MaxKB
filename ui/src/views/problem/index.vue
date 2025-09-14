<template>
  <div class="document p-16-24">
    <h2 class="mb-16">{{ $t('views.problem.title') }}</h2>
    <el-card style="--el-card-padding: 0">
      <div class="main-calc-height">
        <div class="p-24">
          <div class="flex-between">
            <div>
              <el-button
                type="primary"
                @click="createProblem"
                v-if="permissionPrecise.problem_create(id)"
              >
                {{ $t('views.problem.createProblem') }}
              </el-button>
              <el-button
                @click="relateProblem()"
                :disabled="multipleSelection.length === 0"
                v-if="permissionPrecise.problem_relate(id)"
              >
                {{ $t('views.problem.relateParagraph.title') }}
              </el-button>
              <el-button
                @click="deleteMulDocument"
                :disabled="multipleSelection.length === 0"
                v-if="permissionPrecise.problem_delete(id)"
              >
                {{ $t('views.problem.setting.batchDelete') }}
              </el-button>
            </div>

            <el-input
              v-model="filterText"
              :placeholder="$t('views.problem.searchBar.placeholder')"
              prefix-icon="Search"
              class="w-240"
              @change="getList"
              clearable
            />
          </div>
          <app-table
            ref="multipleTableRef"
            class="mt-16"
            :data="problemData"
            :pagination-config="paginationConfig"
            :quick-create="permissionPrecise.problem_create(id)"
            :quickCreateName="$t('views.problem.quickCreateName')"
            :quickCreatePlaceholder="$t('views.problem.quickCreateProblem')"
            :quickCreateMaxlength="256"
            @sizeChange="handleSizeChange"
            @changePage="getList"
            @cell-mouse-enter="cellMouseEnter"
            @cell-mouse-leave="cellMouseLeave"
            @creatQuick="creatQuickHandle"
            @row-click="rowClickHandle"
            @selection-change="handleSelectionChange"
            :row-class-name="setRowClass"
            v-loading="loading"
            :row-key="(row: any) => row.id"
          >
            <el-table-column type="selection" width="55" :reserve-selection="true" />
            <el-table-column prop="content" :label="$t('views.problem.title')" min-width="280">
              <template #default="{ row }">
                <ReadWrite
                  @change="editName($event, row.id)"
                  :data="row.content"
                  :showEditIcon="permissionPrecise.problem_edit(id) && row.id === currentMouseId"
                  :maxlength="256"
                />
              </template>
            </el-table-column>
            <el-table-column
              prop="paragraph_count"
              :label="$t('views.problem.table.paragraph_count')"
              align="right"
              min-width="100"
            >
              <template #default="{ row }">
                <el-link
                  type="primary"
                  @click.stop="rowClickHandle(row)"
                  v-if="row.paragraph_count"
                >
                  {{ row.paragraph_count }}
                </el-link>
                <span v-else>
                  {{ row.paragraph_count }}
                </span>
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
                  <span class="mr-4">
                    <el-tooltip
                      effect="dark"
                      :content="$t('views.problem.relateParagraph.title')"
                      placement="top"
                    >
                      <el-button
                        type="primary"
                        text
                        @click.stop="relateProblem(row)"
                        v-if="permissionPrecise.problem_relate(id)"
                      >
                        <AppIcon iconName="app-generate-question"></AppIcon>
                      </el-button>
                    </el-tooltip>
                  </span>
                  <span>
                    <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
                      <el-button
                        type="primary"
                        text
                        @click.stop="deleteProblem(row)"
                        v-if="permissionPrecise.problem_delete(id)"
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
    <CreateProblemDialog ref="CreateProblemDialogRef" @refresh="refresh" />
    <DetailProblemDrawer
      :next="nextChatRecord"
      :pre="preChatRecord"
      ref="DetailProblemRef"
      v-model:currentId="currentClickId"
      v-model:currentContent="currentContent"
      :pre_disable="pre_disable"
      :next_disable="next_disable"
      @refresh="refreshRelate"
    />
    <RelateProblemDialog ref="RelateProblemDialogRef" @refresh="refreshRelate" />
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElTable } from 'element-plus'
import CreateProblemDialog from './component/CreateProblemDialog.vue'
import DetailProblemDrawer from './component/DetailProblemDrawer.vue'
import RelateProblemDialog from './component/RelateProblemDialog.vue'
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

const RelateProblemDialogRef = ref()
const DetailProblemRef = ref()
const CreateProblemDialogRef = ref()
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
const problemData = ref<any[]>([])
const problemIndexMap = computed<Dict<number>>(() => {
  return problemData.value
    .map((row, index) => ({
      [row.id]: index,
    }))
    .reduce((pre, next) => ({ ...pre, ...next }), {})
})

const multipleTableRef = ref<InstanceType<typeof ElTable>>()
const multipleSelection = ref<any[]>([])

function relateProblem(row?: any) {
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

  RelateProblemDialogRef.value.open(arr)
}

function createProblem() {
  CreateProblemDialogRef.value.open()
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
  loadSharedApi({ type: 'problem', systemType: apiType.value })
    .postProblems(id, obj)
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
  loadSharedApi({ type: 'problem', systemType: apiType.value })
    .putMulProblem(id, arr, loading)
    .then(() => {
      MsgSuccess(t('views.document.delete.successMessage'))
      multipleTableRef.value?.clearSelection()
      getList()
    })
}

function deleteProblem(row: any) {
  loadSharedApi({ type: 'problem', systemType: apiType.value })
    .delProblems(id, row.id, loading)
    .then(() => {
      MsgSuccess(t('common.deleteSuccess'))
      getList()
    })
}

function editName(val: string, problemId: string) {
  if (val) {
    const obj = {
      content: val,
    }
    loadSharedApi({ type: 'problem', systemType: apiType.value })
      .putProblems(id, problemId, obj, loading)
      .then(() => {
        getList()
        MsgSuccess(t('common.modifySuccess'))
      })
  } else {
    MsgError(t('views.problem.tip.errorMessage'))
  }
}

function cellMouseEnter(row: any) {
  currentMouseId.value = row.id
}

function cellMouseLeave() {
  currentMouseId.value = ''
}

/**
 * 下一页
 */
const nextChatRecord = () => {
  let index = problemIndexMap.value[currentClickId.value] + 1
  if (index >= problemData.value.length) {
    if (
      index + (paginationConfig.current_page - 1) * paginationConfig.page_size >=
      paginationConfig.total - 1
    ) {
      return
    }
    paginationConfig.current_page = paginationConfig.current_page + 1
    getList().then(() => {
      index = 0
      currentClickId.value = problemData.value[index].id
      currentContent.value = problemData.value[index].content
    })
  } else {
    currentClickId.value = problemData.value[index].id
    currentContent.value = problemData.value[index].content
  }
}
const pre_disable = computed(() => {
  const index = problemIndexMap.value[currentClickId.value] - 1
  return index < 0 && paginationConfig.current_page <= 1
})

const next_disable = computed(() => {
  const index = problemIndexMap.value[currentClickId.value] + 1
  return (
    index >= problemData.value.length &&
    index + (paginationConfig.current_page - 1) * paginationConfig.page_size >=
      paginationConfig.total - 1
  )
})
/**
 * 上一页
 */
const preChatRecord = () => {
  let index = problemIndexMap.value[currentClickId.value] - 1

  if (index < 0) {
    if (paginationConfig.current_page <= 1) {
      return
    }
    paginationConfig.current_page = paginationConfig.current_page - 1
    getList().then(() => {
      index = paginationConfig.page_size - 1
      currentClickId.value = problemData.value[index].id
      currentContent.value = problemData.value[index].content
    })
  } else {
    currentClickId.value = problemData.value[index].id
    currentContent.value = problemData.value[index].content
  }
}

function rowClickHandle(row: any, column?: any) {
  if (column && column.type === 'selection') {
    return
  }
  if (route.path.includes('share/')) {
    return
  }
  if (row.paragraph_count) {
    currentClickId.value = row.id
    currentContent.value = row.content
    DetailProblemRef.value.open()
  }
}

const setRowClass = ({ row }: any) => {
  return currentClickId.value === row?.id ? 'highlight' : ''
}

function handleSizeChange() {
  paginationConfig.current_page = 1
  getList()
}

function getList() {
  return loadSharedApi({ type: 'problem', isShared: isShared.value, systemType: apiType.value })
    .getProblemsPage(
      id as string,
      paginationConfig,
      filterText.value && { content: filterText.value },
      loading,
    )
    .then((res: any) => {
      problemData.value = res.data.records
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
