<template>
  <LayoutContainer header="对话日志">
    <div class="p-24">
      <div class="mb-16">
        <el-select v-model="history_day" class="mr-12">
          <el-option
            v-for="item in dayOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-input v-model="search" placeholder="搜索" prefix-icon="Search" style="width: 240px" />
      </div>

      <app-table
        :data="tableData"
        :pagination-config="paginationConfig"
        @sizeChange="handleSizeChange"
        @changePage="handleCurrentChange"

      >
        <el-table-column prop="abstract" label="摘要" />
        <el-table-column prop="chat_record_count" label="对话提问数" align="right" />
        <el-table-column prop="star_num" label="用户反馈" align="right">
          <template #default="{ row }">
            <div>
              <AppIcon iconName="app-like-color"></AppIcon>
              {{ row.star_num }}
              <AppIcon iconName="app-oppose-color"></AppIcon>
              {{ row.trample_num }}
            </div>
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
              <el-button type="primary" text>
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
import { ref, onMounted, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import applicationApi from '@/api/application'
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
    value: 188,
    label: '过去半年'
  }
]
const loading = ref(false)
const paginationConfig = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})
const tableData = ref([])
const history_day = ref(7)
const search = ref('')

function handleSizeChange(val: number) {
  console.log(`${val} items per page`)
}
function handleCurrentChange(val: number) {
  console.log(`current page: ${val}`)
}

function getList() {
  applicationApi.getChatLog(id as string, history_day.value, loading).then((res) => {
    tableData.value = res.data
    paginationConfig.total = res.data.length
  })
}

onMounted(() => {
  getList()
})
</script>
<style lang="scss" scoped></style>
