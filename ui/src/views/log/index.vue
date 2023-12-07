<template>
  <LayoutContainer header="对话日志">
    <div class="p-24">
      <div class="mb-16">
        <el-select v-model="history_day" class="mr-12" @change="changeHandle">
          <el-option
            v-for="item in dayOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-input
          v-model="search"
          @change="getList"
          placeholder="搜索"
          prefix-icon="Search"
          class="w-240"
        />
      </div>

      <app-table
        :data="tableData"
        :pagination-config="paginationConfig"
        @sizeChange="handleSizeChange"
        @changePage="getList"
        @row-click="rowClickHandle"
        v-loading="loading"
      >
        <el-table-column prop="abstract" label="摘要" show-overflow-tooltip />
        <el-table-column prop="chat_record_count" label="对话提问数" align="right" />
        <el-table-column prop="star_num" label="用户反馈" align="right">
          <template #default="{ row }">
            <span v-if="!row.trample_num && !row.trample_num"> - </span>
            <span v-else>
              <span v-if="row.star_num">
                <AppIcon iconName="app-like-color"></AppIcon>
                {{ row.star_num }}
              </span>
              <span v-if="row.trample_num" class="ml-4">
                <AppIcon iconName="app-oppose-color"></AppIcon>
                {{ row.trample_num }}
              </span>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="mark_sum" label="改进标注" align="right" />
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            {{ datetimeFormat(row.create_time) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="70" align="center">
          <template #default="{ row }">
            <el-tooltip effect="dark" content="删除" placement="top">
              <el-button type="primary" text @click.stop="deleteLog(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </app-table>
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import logApi from '@/api/log'
import { datetimeFormat } from '@/utils/time'
const route = useRoute()
const {
  params: { id }
} = route

const dayOptions = [
  {
    value: 7,
    label: '过去7天'
  },
  {
    value: 30,
    label: '过去30天'
  },
  {
    value: 90,
    label: '过去90天'
  },
  {
    value: 183,
    label: '过去半年'
  }
]
const loading = ref(false)
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})
const tableData = ref([])

const history_day = ref(7)
const search = ref('')

function rowClickHandle(row: any) {
  // router.push({ path: `/dataset/${id}/${row.id}` })
}

function deleteLog(row: any) {
  MsgConfirm(`是否删除对话：${row.abstract} ?`, `删除后无法恢复，请谨慎操作。`, {
    confirmButtonText: '删除',
    confirmButtonClass: 'danger'
  })
    .then(() => {
      loading.value = true
      logApi.delChatLog(id as string, row.id, loading).then(() => {
        MsgSuccess('删除成功')
        getList()
      })
    })
    .catch(() => {})
}

function handleSizeChange() {
  paginationConfig.current_page = 1
  getList()
}

function changeHandle(val: number) {
  history_day.value = val
  paginationConfig.current_page = 1
  getList()
}

function getList() {
  let obj: any = {
    history_day: history_day.value
  }
  if (search.value) {
    obj = { ...obj, search: search.value }
  }
  logApi.getChatLog(id as string, paginationConfig, obj, loading).then((res) => {
    tableData.value = res.data.records
    paginationConfig.total = res.data.total
  })
}

onMounted(() => {
  getList()
})
</script>
<style lang="scss" scoped></style>
