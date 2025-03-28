<template>
  <LayoutContainer :header="$t('views.operateLog.title')">
    <div class="p-24">
      <div class="flex-between">
        <div>
          <el-select
            v-model="history_day"
            class="mr-12"
            @change="changeDayHandle"
            style="width: 180px"
          >
            <el-option
              v-for="item in dayOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
          <el-date-picker
            v-if="history_day === 'other'"
            v-model="daterangeValue"
            type="daterange"
            :start-placeholder="$t('views.applicationOverview.monitor.startDatePlaceholder')"
            :end-placeholder="$t('views.applicationOverview.monitor.endDatePlaceholder')"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="changeDayRangeHandle"
          />
        </div>

        <div style="display: flex">
          <div class="flex-between complex-search">
            <el-select
              v-model="filter_type"
              class="complex-search__left"
              @change="changeFilterHandle"
              style="width: 120px"
            >
              <el-option
                v-for="item in filterOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
            <el-select
              v-if="filter_type === 'status'"
              v-model="filter_status"
              @change="changeStatusHandle"
              style="width: 220px"
              clearable
            >
              <el-option
                v-for="item in statusOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
            <el-input
              v-else
              v-model="searchValue"
              @change="getList"
              :placeholder="$t('common.search')"
              prefix-icon="Search"
              style="width: 220px"
              clearable
            />
          </div>
          <el-button @click="exportLog" style="margin-left: 10px">{{
            $t('common.export')
          }}</el-button>
        </div>
      </div>

      <app-table
        class="mt-16"
        :data="tableData"
        :pagination-config="paginationConfig"
        @sizeChange="handleSizeChange"
        @changePage="getList"
        v-loading="loading"
      >
        <el-table-column prop="menu" :label="$t('views.operateLog.table.menu.label')" width="160">
          <template #header>
            <div>
              <span>{{ $t('views.operateLog.table.menu.label') }}</span>
              <el-popover :width="200" trigger="click" :visible="popoverVisible">
                <template #reference>
                  <el-button
                    style="margin-top: -2px"
                    :type="operateTypeArr && operateTypeArr.length > 0 ? 'primary' : ''"
                    link
                    @click="popoverVisible = !popoverVisible"
                  >
                    <el-icon>
                      <Filter />
                    </el-icon>
                  </el-button>
                </template>
                <div class="filter">
                  <div class="form-item mb-16">
                    <div @click.stop>
                      <el-scrollbar height="300" style="margin: 0 0 0 10px">
                        <el-checkbox-group
                          v-model="operateTypeArr"
                          style="display: flex; flex-direction: column"
                        >
                          <el-checkbox
                            v-for="item in operateOptions"
                            :key="item.value"
                            :label="item.label"
                            :value="item.value"
                          />
                        </el-checkbox-group>
                      </el-scrollbar>
                    </div>
                  </div>
                </div>
                <div class="text-right">
                  <el-button size="small" @click="filterChange('clear')">{{
                    $t('common.clear')
                  }}</el-button>
                  <el-button type="primary" @click="filterChange" size="small">{{
                    $t('common.confirm')
                  }}</el-button>
                </div>
              </el-popover>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="operate" :label="$t('views.operateLog.table.operate.detail')">
          <template #default="{ row }">
            <el-tooltip
              :content="
                row.operate + (row.operation_object?.name ? `【${row.operation_object.name}】` : '')
              "
              effect="dark"
              placement="top"
            >
              <span class="text-ellipsis">
                {{
                  row.operate +
                  (row.operation_object?.name ? `【${row.operation_object.name}】` : '')
                }}
              </span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column
          width="120"
          prop="user.username"
          :label="$t('views.operateLog.table.user.label')"
        />
        <el-table-column
          prop="status"
          :label="$t('views.operateLog.table.status.label')"
          width="100"
        >
          <template #default="{ row }">
            <span v-if="row.status === 200">{{ $t('views.operateLog.table.status.success') }}</span>
            <span v-else style="color: red">{{ $t('views.operateLog.table.status.fail') }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="ip_address"
          :label="$t('views.operateLog.table.ip_address.label')"
          width="160"
        ></el-table-column>
        <el-table-column :label="$t('views.operateLog.table.operateTime.label')" width="180">
          <template #default="{ row }">
            {{ datetimeFormat(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.operation')" width="110" align="left" fixed="right">
          <template #default="{ row }">
            <span class="mr-4">
              <el-button type="primary" text @click.stop="showDetails(row)" class="text-button">
                {{ $t('views.operateLog.table.opt.label') }}
              </el-button>
            </span>
          </template>
        </el-table-column>
      </app-table>
    </div>
    <DetailDialog ref="DetailDialogRef" />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import operateLog from '@/api/operate-log'
import DetailDialog from './component/DetailDialog.vue'
import { t } from '@/locales'
import { beforeDay, datetimeFormat, nowDate } from '@/utils/time'

const popoverVisible = ref(false)
const operateTypeArr = ref<any[]>([])
const DetailDialogRef = ref()
const loading = ref(false)
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})
const searchValue = ref('')
const tableData = ref<any[]>([])
const history_day = ref<number | string>(7)
const filter_type = ref<string>('user')
const filter_status = ref<string>('')
const daterange = ref({
  start_time: '',
  end_time: ''
})
const daterangeValue = ref('')
const dayOptions = [
  {
    value: 7,
    // @ts-ignore
    label: t('views.applicationOverview.monitor.pastDayOptions.past7Days') // 使用 t 方法来国际化显示文本
  },
  {
    value: 30,
    label: t('views.applicationOverview.monitor.pastDayOptions.past30Days')
  },
  {
    value: 90,
    label: t('views.applicationOverview.monitor.pastDayOptions.past90Days')
  },
  {
    value: 183,
    label: t('views.applicationOverview.monitor.pastDayOptions.past183Days')
  },
  {
    value: 'other',
    label: t('views.applicationOverview.monitor.pastDayOptions.other')
  }
]
const filterOptions = [
  {
    value: 'user',
    label: t('views.operateLog.table.user.label')
  },
  {
    value: 'status',
    label: t('views.operateLog.table.status.label')
  },
  {
    value: 'ip_address',
    label: t('views.operateLog.table.ip_address.label')
  }
]
const statusOptions = [
  {
    value: '200',
    label: t('views.operateLog.table.status.success')
  },
  {
    value: '500',
    label: t('views.operateLog.table.status.fail')
  }
]
const operateOptions = ref<any[]>([])

function filterChange(val: string) {
  if (val === 'clear') {
    operateTypeArr.value = []
  }
  getList()
  popoverVisible.value = false
}

function changeStatusHandle(val: string) {
  getList()
}

function changeFilterHandle(val: string) {
  filter_type.value = val
  if (searchValue.value) {
    getList()
  }
}

function changeDayHandle(val: number | string) {
  if (val !== 'other') {
    daterange.value.start_time = beforeDay(val)
    daterange.value.end_time = ''
    getList()
  }
}
function changeDayRangeHandle(val: string) {
  daterange.value.start_time = val[0]
  daterange.value.end_time = val[1]
  getList()
}

function showDetails(row: any) {
  DetailDialogRef.value.open(row)
}

function handleSizeChange() {
  paginationConfig.current_page = 1
  getList()
}

function getRequestParams() {
  let obj: any = {
    start_time: daterange.value.start_time,
    end_time: daterange.value.end_time
  }
  if (searchValue.value && filter_type.value !== 'status') {
    obj[filter_type.value] = searchValue.value
  }
  if (filter_type.value === 'status') {
    obj['status'] = filter_status.value
  }
  if (operateTypeArr.value.length > 0) {
    obj['menu'] = JSON.stringify(operateTypeArr.value)
  }
  return obj
}

function getList() {
  return operateLog.getOperateLog(paginationConfig, getRequestParams(), loading).then((res) => {
    tableData.value = res.data.records
    paginationConfig.total = res.data.total
  })
}

function getMenuList() {
  return operateLog.getMenuList().then((res) => {
    let arr: any[] = res.data
    arr
      .filter((item, index, self) => index === self.findIndex((i) => i['menu'] === item['menu']))
      .forEach((ele) => {
        operateOptions.value.push({ label: ele.menu_label, value: ele.menu })
      })
  })
}

const exportLog = () => {
  operateLog.exportOperateLog(getRequestParams(), loading)
}

onMounted(() => {
  getMenuList()
  changeDayHandle(history_day.value)
})
</script>
<style lang="scss" scoped>
.text-button {
  font-size: 14px;
}
.text-ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  display: block;
}
</style>
