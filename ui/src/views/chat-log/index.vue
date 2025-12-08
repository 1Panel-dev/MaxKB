<template>
  <div class="p-16-24">
    <h2 class="mb-16">{{ $t('views.chatLog.title') }}</h2>

    <el-card style="--el-card-padding: 24px">
      <div class="mb-16 flex-between">
        <div class="flex align-center">
          <div class="flex-between complex-search">
            <el-select
              v-model="search_type"
              class="complex-search__left"
              @change="search_type_change"
              style="width: 75px"
            >
              <el-option :label="$t('views.chatLog.table.abstract')" value="abstract" />
              <el-option :label="$t('views.chatLog.table.username')" value="username" />
            </el-select>
            <el-input
              v-model="search_form[search_type]"
              @change="getList"
              :placeholder="$t('common.search')"
              class="w-240"
              clearable
            />
          </div>
          <el-select
            v-model="history_day"
            class="ml-12"
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
            style="width: 240px"
            class="mr-12"
          />
        </div>
        <div style="display: flex; align-items: center" class="float-right">
          <el-button @click="dialogVisible = true" v-if="permissionPrecise.chat_log_clear(id)">
            {{ $t('views.chatLog.buttons.clearStrategy') }}
          </el-button>
          <el-button @click="exportLog" v-if="permissionPrecise.chat_log_export(id)">
            {{ $t('common.export') }}
          </el-button>
          <el-button
            @click="openDocumentDialog"
            :disabled="multipleSelection.length === 0"
            v-if="permissionPrecise.chat_log_add_knowledge(id)"
            >{{ $t('views.chatLog.addToKnowledge') }}
          </el-button>
        </div>
      </div>

      <app-table
        :data="tableData"
        :pagination-config="paginationConfig"
        @sizeChange="getList"
        @changePage="getList"
        @row-click="rowClickHandle"
        v-loading="loading"
        :row-class-name="setRowClass"
        @selection-change="handleSelectionChange"
        class="log-table"
        ref="multipleTableRef"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column
          prop="abstract"
          :label="$t('views.chatLog.table.abstract')"
          show-overflow-tooltip
        />
        <el-table-column
          prop="chat_record_count"
          :label="$t('views.chatLog.table.chat_record_count')"
          align="right"
        />
        <el-table-column prop="star_num" align="right">
          <template #header>
            <div>
              <span>{{ $t('views.chatLog.table.feedback.label') }}</span>
              <el-popover :width="200" trigger="click" :visible="popoverVisible">
                <template #reference>
                  <el-button
                    style="margin-top: -2px"
                    :type="filter.min_star || filter.min_trample ? 'primary' : ''"
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
                      {{ $t('views.chatLog.table.feedback.star') }} >=
                      <el-input-number
                        v-model="filter.min_star"
                        :min="0"
                        :step="1"
                        :value-on-clear="0"
                        controls-position="right"
                        style="width: 80px"
                        size="small"
                        step-strictly
                      />
                    </div>
                  </div>
                  <div class="form-item mb-16">
                    <div @click.stop>
                      {{ $t('views.chatLog.table.feedback.trample') }} >=
                      <el-input-number
                        v-model="filter.min_trample"
                        :min="0"
                        :step="1"
                        :value-on-clear="0"
                        controls-position="right"
                        style="width: 80px"
                        size="small"
                        step-strictly
                      />
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
          <template #default="{ row }">
            <span class="mr-8" v-if="!row.trample_num && !row.star_num"> - </span>
            <span class="mr-8" v-else>
              <span v-if="row.star_num">
                <AppIcon iconName="app-like-color"></AppIcon>
                {{ row.star_num }}
              </span>
              <span v-if="row.trample_num" class="ml-8">
                <AppIcon iconName="app-oppose-color"></AppIcon>
                {{ row.trample_num }}
              </span>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="mark_sum" :label="$t('views.chatLog.table.mark')" align="right" />
        <el-table-column prop="asker" :label="$t('views.chatLog.table.user')">
          <template #default="{ row }">
            {{ row.asker?.username }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('views.chatLog.table.recenTimes')" width="180">
          <template #default="{ row }">
            {{ datetimeFormat(row.update_time) }}
          </template>
        </el-table-column>
      </app-table>
    </el-card>
    <ChatRecordDrawer
      :next="nextChatRecord"
      :pre="preChatRecord"
      ref="ChatRecordRef"
      v-model:chatId="currentChatId"
      v-model:currentAbstract="currentAbstract"
      :application="detail"
      :pre_disable="pre_disable"
      :next_disable="next_disable"
      @refresh="refresh"
    />
    <el-dialog
      :title="$t('views.chatLog.buttons.clearStrategy')"
      v-model="dialogVisible"
      width="25%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <span>{{ $t('common.delete') }}</span>
      <el-input-number
        v-model="days"
        controls-position="right"
        :min="1"
        :max="100000"
        :value-on-clear="0"
        step-strictly
        style="width: 110px; margin-left: 8px; margin-right: 8px"
      ></el-input-number>
      <span>{{ $t('views.chatLog.daysText') }}</span>
      <template #footer>
        <div class="dialog-footer" style="margin-top: 16px">
          <el-button @click="dialogVisible = false">{{ $t('common.cancel') }} </el-button>
          <el-button type="primary" @click="saveCleanTime">
            {{ $t('common.save') }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      :title="$t('views.chatLog.addToKnowledge')"
      v-model="documentDialogVisible"
      width="50%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <SelectKnowledgeDocument
        :post-knowledge-handler="postKnowledgeHandler"
        ref="SelectKnowledgeDocumentRef"
        :apiType="apiType"
        :workspace-id="detail.workspace_id"
      />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click.prevent="documentDialogVisible = false">
            {{ $t('common.cancel') }}
          </el-button>
          <el-button type="primary" @click="submitForm" :loading="documentLoading">
            {{ $t('common.save') }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, type Ref, onMounted, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep } from 'lodash'
import ChatRecordDrawer from './component/ChatRecordDrawer.vue'
import SelectKnowledgeDocument from '@/components/select-knowledge-document/index.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { beforeDay, datetimeFormat, nowDate } from '@/utils/time'
import type { Dict } from '@/api/type/common'
import { t } from '@/locales'
import { ElTable } from 'element-plus'
import permissionMap from '@/permission'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { Permission } from '@/utils/permission/type'
import { hasPermission } from '@/utils/permission'
import { PermissionConst, RoleConst } from '@/utils/permission/data'

const route = useRoute()

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const permissionPrecise = computed(() => {
  return permissionMap['application'][apiType.value]
})

const {
  params: { id },
} = route as any

const emit = defineEmits(['refresh'])

const search_type = ref('abstract')
const search_form = ref<any>({
  abstract: '',
  username: '',
})

const search_type_change = () => {
  search_form.value = { abstract: '', username: '' }
}

const dayOptions = [
  {
    value: 7,
    label: t('views.applicationOverview.monitor.pastDayOptions.past7Days'), // 使用 t 方法来国际化显示文本
  },
  {
    value: 30,
    label: t('views.applicationOverview.monitor.pastDayOptions.past30Days'),
  },
  {
    value: 90,
    label: t('views.applicationOverview.monitor.pastDayOptions.past90Days'),
  },
  {
    value: 183,
    label: t('views.applicationOverview.monitor.pastDayOptions.past183Days'),
  },
  {
    value: 'other',
    label: t('common.custom'),
  },
]
const daterangeValue = ref('')
// 提交日期时间
const daterange = ref({
  start_time: '',
  end_time: '',
})

const multipleTableRef = ref<InstanceType<typeof ElTable>>()
const multipleSelection = ref<any[]>([])

const ChatRecordRef = ref()
const loading = ref(false)
const documentLoading = ref(false)
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})
const dialogVisible = ref(false)
const documentDialogVisible = ref(false)
const days = ref<number>(180)
const tableData = ref<any[]>([])
const tableIndexMap = computed<Dict<number>>(() => {
  return tableData.value
    .map((row, index) => ({
      [row.id]: index,
    }))
    .reduce((pre, next) => ({ ...pre, ...next }), {})
})
const history_day = ref<number | string>(7)

const detail = ref<any>(null)

const currentChatId = ref<string>('')
const currentAbstract = ref<string>('')
const popoverVisible = ref(false)
const defaultFilter = {
  min_star: 0,
  min_trample: 0,
  comparer: 'and',
}
const filter = ref<any>({
  min_star: 0,
  min_trample: 0,
  comparer: 'and',
})
const postKnowledgeHandler = (knowledgeList: Array<any>) => {
  return knowledgeList.filter(item => {
    if (apiType.value === 'workspace') {
      if (item.resource_type === 'folder') {
        return true
      }
      if (item.resource_type === 'knowledge') {
        return hasPermission([RoleConst.WORKSPACE_MANAGE.getWorkspaceRole(),
            new Permission("KNOWLEDGE_DOCUMENT:READ+EDIT").getWorkspacePermissionWorkspaceManageRole,
            new Permission("KNOWLEDGE_DOCUMENT:READ+EDIT").getWorkspaceResourcePermission('KNOWLEDGE', item.id)], 'OR')
      }
    } else if (apiType.value === 'systemManage') {
      return hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_KNOWLEDGE_DOCUMENT_EDIT],'OR')
    }
  })

}
function filterChange(val: string) {
  if (val === 'clear') {
    filter.value = cloneDeep(defaultFilter)
  }
  getList()
  popoverVisible.value = false
}

/**
 * 下一页
 */
const nextChatRecord = () => {
  let index = tableIndexMap.value[currentChatId.value] + 1
  if (index >= tableData.value.length) {
    if (
      index + (paginationConfig.current_page - 1) * paginationConfig.page_size >=
      paginationConfig.total - 1
    ) {
      return
    }
    paginationConfig.current_page = paginationConfig.current_page + 1
    getList().then(() => {
      index = 0
      currentChatId.value = tableData.value[index].id
      currentAbstract.value = tableData.value[index].abstract
    })
  } else {
    currentChatId.value = tableData.value[index].id
    currentAbstract.value = tableData.value[index].abstract
  }
}
const pre_disable = computed(() => {
  const index = tableIndexMap.value[currentChatId.value] - 1
  return index < 0 && paginationConfig.current_page <= 1
})

const next_disable = computed(() => {
  const index = tableIndexMap.value[currentChatId.value] + 1
  return (
    index >= tableData.value.length &&
    index + (paginationConfig.current_page - 1) * paginationConfig.page_size >=
      paginationConfig.total - 1
  )
})
/**
 * 上一页
 */
const preChatRecord = () => {
  let index = tableIndexMap.value[currentChatId.value] - 1

  if (index < 0) {
    if (paginationConfig.current_page <= 1) {
      return
    }
    paginationConfig.current_page = paginationConfig.current_page - 1
    getList().then(() => {
      index = paginationConfig.page_size - 1
      currentChatId.value = tableData.value[index].id
      currentAbstract.value = tableData.value[index].abstract
    })
  } else {
    currentChatId.value = tableData.value[index].id
    currentAbstract.value = tableData.value[index].abstract
  }
}

function rowClickHandle(row: any, column?: any) {
  if (column && column.type === 'selection') {
    return
  }
  currentChatId.value = row.id
  currentAbstract.value = row.abstract
  ChatRecordRef.value.open()
}

const setRowClass = ({ row }: any) => {
  return currentChatId.value === row?.id ? 'highlight' : ''
}

const handleSelectionChange = (val: any[]) => {
  multipleSelection.value = val
}

function getList() {
  const obj: any = {
    start_time: daterange.value.start_time,
    end_time: daterange.value.end_time,
    ...filter.value,
  }
  if (search_form.value[search_type.value]) {
    obj[search_type.value] = search_form.value[search_type.value]
  }
  return loadSharedApi({ type: 'chatLog', systemType: apiType.value })
    .getChatLog(id as string, paginationConfig, obj, loading)
    .then((res: any) => {
      tableData.value = res.data.records
      if (currentChatId.value) {
        currentChatId.value = tableData.value[0]?.id
      }
      paginationConfig.total = res.data.total
    })
}

function getDetail(isLoading = false) {
  loadSharedApi({ type: 'application', systemType: apiType.value })
    .getApplicationDetail(id as string, isLoading ? loading : undefined)
    .then((res: any) => {
      detail.value = res.data
      days.value = res.data.clean_time
    })
}

const exportLog = () => {
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  if (detail.value) {
    const obj: any = {
      start_time: daterange.value.start_time,
      end_time: daterange.value.end_time,
      ...filter.value,
    }
    if (search_form.value[search_type.value]) {
      obj[search_type.value] = search_form.value[search_type.value]
    }
    loadSharedApi({ type: 'chatLog', systemType: apiType.value }).postExportChatLog(
      detail.value.id,
      detail.value.name,
      obj,
      { select_ids: arr },
      loading,
    )
  }
}

function refresh() {
  getList()
}

function changeDayRangeHandle(val: string) {
  daterange.value.start_time = val[0]
  daterange.value.end_time = val[1]
  getList()
}

function changeDayHandle(val: number | string) {
  if (val !== 'other') {
    daterange.value.start_time = beforeDay(val)
    daterange.value.end_time = nowDate
    getList()
  }
}

function saveCleanTime() {
  const obj = {
    clean_time: days.value,
  }
  loadSharedApi({ type: 'application', systemType: apiType.value })
    .putApplication(id as string, obj, loading)
    .then(() => {
      MsgSuccess(t('common.saveSuccess'))
      dialogVisible.value = false
      getDetail(true)
    })
    .catch(() => {
      dialogVisible.value = false
    })
}

const SelectKnowledgeDocumentRef = ref()
const submitForm = async () => {
  if (await SelectKnowledgeDocumentRef.value?.validate()) {
    const arr: string[] = []
    multipleSelection.value.map((v) => {
      if (v) {
        arr.push(v.id)
      }
    })
    const obj = {
      ...SelectKnowledgeDocumentRef.value.form,
      chat_ids: arr,
    }
    loadSharedApi({ type: 'chatLog', systemType: apiType.value })
      .postChatLogAddKnowledge(id, obj, documentLoading)
      .then((res: any) => {
        multipleTableRef.value?.clearSelection()
        documentDialogVisible.value = false
      })
  }
}

function openDocumentDialog() {
  SelectKnowledgeDocumentRef.value?.clearValidate()
  documentDialogVisible.value = true
}

onMounted(() => {
  changeDayHandle(history_day.value)
  getDetail()
})
</script>
<style lang="scss" scoped>
.log-table {
  :deep(tr) {
    cursor: pointer;
  }
}
</style>
