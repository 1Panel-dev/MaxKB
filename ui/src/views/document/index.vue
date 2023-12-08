<template>
  <LayoutContainer header="文档">
    <div class="main-calc-height">
      <div class="p-24">
        <div class="flex-between">
          <el-button
            type="primary"
            @click="router.push({ path: '/dataset/upload', query: { id: id } })"
            >上传文档</el-button
          >
          <el-input
            v-model="filterText"
            placeholder="按 文档名称 搜索"
            prefix-icon="Search"
            class="w-240"
            @change="getList"
          />
        </div>
        <app-table
          class="mt-16"
          :data="documentData"
          :pagination-config="paginationConfig"
          quick-create
          @sizeChange="handleSizeChange"
          @changePage="getList"
          @cell-mouse-enter="cellMouseEnter"
          @cell-mouse-leave="cellMouseLeave"
          @creatQuick="creatQuickHandle"
          @row-click="rowClickHandle"
          v-loading="loading"
        >
          <el-table-column prop="name" label="文件名称" min-width="280">
            <template #default="{ row }">
              <ReadWrite
                @change="editName"
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
                <el-icon class="is-loading primary"><Loading /></el-icon> 导入中
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
          <el-table-column label="操作" align="center">
            <template #default="{ row }">
              <span v-if="row.status === 2">
                <el-tooltip effect="dark" content="刷新" placement="top">
                  <el-button type="primary" text>
                    <el-icon><RefreshRight /></el-icon>
                  </el-button>
                </el-tooltip>
              </span>
              <span class="ml-4">
                <el-tooltip effect="dark" content="删除" placement="top">
                  <el-button type="primary" text @click.stop="deleteDocument(row)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </span>
            </template>
          </el-table-column>
        </app-table>
      </div>
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import documentApi from '@/api/document'
import { numberFormat } from '@/utils/utils'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
const router = useRouter()
const route = useRoute()
const {
  params: { id }
} = route as any

const loading = ref(false)
const filterText = ref('')
const documentData = ref<any[]>([])
const currentMouseId = ref(null)

const paginationConfig = reactive({
  current_page: 1,
  page_size: 10,
  total: 0
})

function rowClickHandle(row: any) {
  router.push({ path: `/dataset/${id}/${row.id}` })
}

/*
  快速创建空白文档
*/
function creatQuickHandle(val: string) {
  loading.value = true
  const obj = { name: val }
  documentApi
    .postDocument(id, obj)
    .then((res) => {
      getList()
      MsgSuccess('创建成功')
    })
    .catch(() => {
      loading.value = false
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
      loading.value = true
      documentApi
        .delDocument(id, row.id)
        .then(() => {
          MsgSuccess('删除成功')
          getList()
        })
        .catch(() => {
          loading.value = false
        })
    })
    .catch(() => {})
}

/*
  更新名称或状态
*/
function updateData(documentId: string, data: any, msg: string) {
  loading.value = true
  documentApi
    .putDocument(id, documentId, data)
    .then((res) => {
      const index = documentData.value.findIndex((v) => v.id === documentId)
      documentData.value.splice(index, 1, res.data)
      MsgSuccess(msg)
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function changeState(bool: Boolean, row: any) {
  const obj = {
    is_active: bool
  }
  const str = bool ? '启用成功' : '禁用成功'
  currentMouseId.value && updateData(row.id, obj, str)
}

function editName(val: string) {
  const obj = {
    name: val
  }
  currentMouseId.value && updateData(currentMouseId.value, obj, '修改成功')
}

function cellMouseEnter(row: any) {
  currentMouseId.value = row.id
}
function cellMouseLeave() {
  currentMouseId.value = null
}

function handleSizeChange() {
  paginationConfig.current_page = 1
  getList()
}

function getList() {
  documentApi
    .getDocument(
      id as string,
      paginationConfig,
      filterText.value && { name: filterText.value },
      loading
    )
    .then((res) => {
      documentData.value = res.data.records
      paginationConfig.total = res.data.total
    })
}

onMounted(() => {
  getList()
})
</script>
<style lang="scss" scoped></style>
