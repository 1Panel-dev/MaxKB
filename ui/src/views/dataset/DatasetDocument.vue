<template>
  <LayoutContainer header="文档">
    <div class="main-calc-height">
      <div class="p-24">
        <div class="flex-between">
          <el-button type="primary" @click="router.push({ path: '/dataset/upload' })"
            >上传文档</el-button
          >
          <el-input
            v-model="filterText"
            placeholder="按 文档名称 搜索"
            prefix-icon="Search"
            class="w-240"
          />
        </div>
        <app-table
          class="mt-16"
          :data="documentData"
          :pagination-config="paginationConfig"
          quick-create
          @sizeChange="handleSizeChange"
          @changePage="handleCurrentChange"
          @cell-mouse-enter="cellMouseEnter"
          @cell-mouse-leave="cellMouseLeave"
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
              {{ toThousands(row.char_length) }}
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
          <el-table-column prop="name" label="启动状态">
            <template #default="{ row }">
              <el-switch v-model="row.is_active" @change="changeState($event, row)" />
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
          <el-table-column prop="name" label="操作" align="center">
            <template #default="{ row }">
              <span>
                <el-tooltip effect="dark" content="刷新" placement="top">
                  <el-button type="primary" text>
                    <el-icon><RefreshRight /></el-icon>
                  </el-button>
                </el-tooltip>
              </span>
              <span class="ml-4">
                <el-tooltip effect="dark" content="删除" placement="top">
                  <el-button type="primary" text @click="deleteDocument(row)">
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
import { ref, onMounted, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import datasetApi from '@/api/dataset'
import { toThousands } from '@/utils/utils'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
const router = useRouter()
const route = useRoute()
const { params } = route
const { datasetId } = params as any

const loading = ref(false)
const filterText = ref('')
const documentData = ref<any[]>([])
const currentMouseId = ref(null)

const paginationConfig = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

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
      datasetApi
        .delDocument(datasetId, row.id)
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

function updateData(documentId: string, data: any) {
  loading.value = true
  datasetApi
    .putDocument(datasetId, documentId, data)
    .then((res) => {
      const index = documentData.value.findIndex((v) => v.id === documentId)
      documentData.value.splice(index, 1, res.data)
      MsgSuccess('修改成功')
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
  currentMouseId.value && updateData(row.id, obj)
}

function editName(val: string) {
  const obj = {
    name: val
  }
  currentMouseId.value && updateData(currentMouseId.value, obj)
}

function cellMouseEnter(row: any) {
  currentMouseId.value = row.id
}
function cellMouseLeave() {
  currentMouseId.value = null
}

function handleSizeChange(val: number) {
  console.log(`${val} items per page`)
}
function handleCurrentChange(val: number) {
  console.log(`current page: ${val}`)
}

function getList() {
  loading.value = true
  datasetApi
    .getDocument(datasetId as string, filterText.value)
    .then((res) => {
      documentData.value = res.data
      paginationConfig.total = res.data.length
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

onMounted(() => {
  getList()
})
</script>
<style lang="scss" scoped></style>
