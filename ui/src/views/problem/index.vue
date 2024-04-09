<template>
  <LayoutContainer header="问题">
    <div class="main-calc-height">
      <div class="p-24">
        <div class="flex-between">
          <div>
            <el-button type="primary" @click="createProblem">创建问题</el-button>
            <el-button @click="deleteMulDocument" :disabled="multipleSelection.length === 0"
              >批量删除</el-button
            >
          </div>

          <el-input
            v-model="filterText"
            placeholder="搜索内容"
            prefix-icon="Search"
            class="w-240"
            @change="getList"
          />
        </div>
        <app-table
          ref="multipleTableRef"
          class="mt-16"
          :data="problemData"
          :pagination-config="paginationConfig"
          quick-create
          quickCreateName="问题"
          quickCreatePlaceholder="快速创建问题"
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
          <el-table-column prop="content" label="问题" min-width="280">
            <template #default="{ row }">
              <ReadWrite
                @change="editName"
                :data="row.content"
                :showEditIcon="row.id === currentMouseId"
                :maxlength="256"
              />
            </template>
          </el-table-column>
          <el-table-column prop="paragraph_count" label="关联分段数" align="right" min-width="100">
            <template #default="{ row }">
              <el-link type="primary" @click.stop="rowClickHandle(row)" v-if="row.paragraph_count">
                {{ row.paragraph_count }}
              </el-link>
              <span v-else>
                {{ row.paragraph_count }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="create_time" label="创建时间" width="170">
            <template #default="{ row }">
              {{ datetimeFormat(row.create_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="update_time" label="更新时间" width="170">
            <template #default="{ row }">
              {{ datetimeFormat(row.update_time) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" align="left">
            <template #default="{ row }">
              <div>
                <span class="mr-4">
                  <el-tooltip effect="dark" content="关联分段" placement="top">
                    <el-button type="primary" text @click.stop="relateProblem(row)">
                      <el-icon><Connection /></el-icon>
                    </el-button>
                  </el-tooltip>
                </span>
                <span>
                  <el-tooltip effect="dark" content="删除" placement="top">
                    <el-button type="primary" text @click.stop="deleteProblem(row)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-tooltip>
                </span>
              </div>
            </template>
          </el-table-column>
        </app-table>
      </div>
    </div>
    <CreateProblemDialog ref="CreateProblemDialogRef" @refresh="refresh" />
    <DetailProblemDrawer
      :next="nextChatRecord"
      :pre="preChatRecord"
      ref="DetailProblemRef"
      v-model:currentId="currentClickId"
      v-model:currentContent="currentContent"
      :pre_disable="pre_disable"
      :next_disable="next_disable"
      @refresh="refresh"
    />
    <RelateProblemDialog ref="RelateProblemDialogRef" @refresh="refresh" />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElTable } from 'element-plus'
import problemApi from '@/api/problem'
import CreateProblemDialog from './component/CreateProblemDialog.vue'
import DetailProblemDrawer from './component/DetailProblemDrawer.vue'
import RelateProblemDialog from './component/RelateProblemDialog.vue'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import type { Dict } from '@/api/type/common'
import useStore from '@/stores'

const route = useRoute()
const {
  params: { id }
} = route as any

const { problem } = useStore()

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
  total: 0
})

const filterText = ref('')
const problemData = ref<any[]>([])
const problemIndexMap = computed<Dict<number>>(() => {
  return problemData.value
    .map((row, index) => ({
      [row.id]: index
    }))
    .reduce((pre, next) => ({ ...pre, ...next }), {})
})

const multipleTableRef = ref<InstanceType<typeof ElTable>>()
const multipleSelection = ref<any[]>([])

function relateProblem(row: any) {
  RelateProblemDialogRef.value.open(row.id)
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
  problem
    .asyncPostProblem(id, obj)
    .then((res) => {
      getList()
      MsgSuccess('创建成功')
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
  problemApi.delMulProblem(id, arr, loading).then(() => {
    MsgSuccess('批量删除成功')
    getList()
  })
}

function deleteProblem(row: any) {
  MsgConfirm(
    `是否删除问题：${row.content} ?`,
    `删除问题关联的 ${row.paragraph_count} 个分段会被取消关联，请谨慎操作。`,
    {
      confirmButtonText: '删除',
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      problemApi.delProblems(id, row.id, loading).then(() => {
        MsgSuccess('删除成功')
        getList()
      })
    })
    .catch(() => {})
}

function editName(val: string) {
  if (val) {
    const obj = {
      content: val
    }
    problemApi.putProblems(id, currentMouseId.value, obj, loading).then(() => {
      getList()
      MsgSuccess('修改成功')
    })
  } else {
    MsgError('问题不能为空！')
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
  let index = problemIndexMap.value[currentClickId.value] - 1
  return index < 0 && paginationConfig.current_page <= 1
})

const next_disable = computed(() => {
  let index = problemIndexMap.value[currentClickId.value] + 1
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
    getList().then((ok) => {
      index = paginationConfig.page_size - 1
      currentClickId.value = problemData.value[index].id
      currentContent.value = problemData.value[index].content
    })
  } else {
    currentClickId.value = problemData.value[index].id
    currentContent.value = problemData.value[index].content
  }
}

function rowClickHandle(row: any) {
  if (row.paragraph_count) {
    currentClickId.value = row.id
    currentContent.value = row.content
    DetailProblemRef.value.open()
  }
}

const setRowClass = ({ row }: any) => {
  return currentClickId.value === row?.id ? 'hightlight' : ''
}

function handleSizeChange() {
  paginationConfig.current_page = 1
  getList()
}

function getList() {
  return problem
    .asyncGetProblem(
      id as string,
      paginationConfig,
      filterText.value && { content: filterText.value },
      loading
    )
    .then((res: any) => {
      problemData.value = res.data.records
      paginationConfig.total = res.data.total
    })
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
