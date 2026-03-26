<template>
  <el-drawer
    v-model="drawer"
    :title="$t('common.ExecutionRecord.title')"
    direction="rtl"
    size="800px"
    :before-close="close"
  >
    <div class="flex-between mb-16">
      <div class="flex-between complex-search">
        <el-select
          class="complex-search__left"
          v-model="searchType"
          @change="changeFilterHandle"
          style="width: 100px"
        >
          <el-option :label="$t('views.trigger.triggerSource')" value="source_name" />
          <el-option :label="$t('common.type')" value="source_type" />
          <el-option :label="$t('common.status.label')" value="state" />
        </el-select>
        <el-input
          v-if="searchType === 'source_name'"
          v-model="query.source_name"
          :placeholder="$t('common.search')"
          style="width: 220px"
          clearable
          @change="getList(true)"
        />
        <el-select
          v-else-if="searchType === 'state'"
          v-model="query.state"
          @change="getList(true)"
          filterable
          clearable
          :reserve-keyword="false"
          collapse-tags
          collapse-tags-tooltip
          style="width: 220px"
          :placeholder="$t('common.search')"
        >
          <el-option :label="$t('common.status.success')" value="SUCCESS" />
          <el-option :label="$t('common.status.STARTED')" value="STARTED" />
          <el-option :label="$t('common.status.fail')" value="FAILURE" />
        </el-select>
        <el-select
          v-else
          v-model="query.source_type"
          @change="getList(true)"
          filterable
          clearable
          :reserve-keyword="false"
          collapse-tags
          collapse-tags-tooltip
          style="width: 220px"
          :placeholder="$t('common.search')"
        >
          <el-option :label="$t('views.application.title')" value="APPLICATION" />
          <el-option :label="$t('views.knowledge.title')" value="KNOWLEDGE" />
          <el-option :label="$t('views.trigger.title')" value="TRIGGER" />
        </el-select>
      </div>
    </div>

    <app-table
      ref="multipleTableRef"
      class="mt-16"
      :data="tableData"
      :pagination-config="paginationConfig"
      @sizeChange="changeSize"
      @changePage="getList(true)"
      :default-sort="{ prop: 'create_time', order: 'descending' }"
      @sort-change="handleSortChange"
      :maxTableHeight="200"
      :row-key="(row: any) => row.id"
      v-loading="loading"
    >
      <el-table-column
        prop="name"
        :label="$t('views.trigger.triggerSource')"
        min-width="130"
        show-overflow-tooltip
      >
        <template #default="{ row }">
          <el-space :size="8">
            <KnowledgeIcon :size="22" v-if="row.source_type === 'KNOWLEDGE'" :type="4" />
            <TriggerIcon
              v-else-if="row.source_type === 'TRIGGER'"
              :type="row.trigger_type"
              :size="22"
            />
            <el-avatar shape="square" :size="22" style="background: none" v-else>
              <img :src="resetUrl(row?.source_icon, resetUrl('./favicon.ico'))" alt="" />
            </el-avatar>
            <span class="ellipsis">{{ row.source_name }}</span>
          </el-space>
        </template>
      </el-table-column>
      <el-table-column
        prop="source_type"
        width="100"
        show-overflow-tooltip
        :label="$t('common.type')"
      >
        <template #default="{ row }">
          <span v-if="row.source_type === 'APPLICATION'">{{ $t('views.application.title') }}</span>
          <span v-else-if="row.source_type === 'KNOWLEDGE'">{{ $t('views.knowledge.title') }}</span>
          <span v-else>{{ $t('views.trigger.title') }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="state" :label="$t('common.status.label')" width="100">
        <template #default="{ row }">
          <el-text class="color-text-primary" v-if="row.state === 'SUCCESS'">
            <el-icon class="color-success"><SuccessFilled /></el-icon>
            {{ $t('common.status.success') }}
          </el-text>
          <el-text class="color-text-primary" v-else-if="row.state === 'FAILURE'">
            <el-icon class="color-danger"><CircleCloseFilled /></el-icon>
            {{ $t('common.status.fail') }}
          </el-text>
          <el-text class="color-text-primary" v-else-if="row.state === 'REVOKED'">
            <el-icon class="color-danger"><CircleCloseFilled /></el-icon>
            {{ $t('common.status.REVOKED') }}
          </el-text>
          <el-text class="color-text-primary" v-else-if="row.state === 'REVOKE'">
            <el-icon class="is-loading color-primary"><Loading /></el-icon>
            {{ $t('common.status.REVOKE') }}
          </el-text>
          <el-text class="color-text-primary" v-else>
            <el-icon class="is-loading color-primary"><Loading /></el-icon>
            {{ $t('common.status.STARTED') }}
          </el-text>
        </template>
      </el-table-column>
      <el-table-column prop="run_time" :label="$t('chat.KnowledgeSource.consumeTime')">
        <template #default="{ row }">
          {{ row.run_time != undefined ? row.run_time?.toFixed(2) + 's' : '-' }}
        </template>
      </el-table-column>
      <el-table-column
        v-if="apiType === 'systemShare'"
        prop="workspace_name"
        :label="$t('views.workspace.title')"
      >
        <template #default="{ row }">
          {{ row.workspace_name }}
        </template>
      </el-table-column>
      <el-table-column
        sortable
        prop="create_time"
        :label="$t('chat.executionDetails.createTime')"
        width="180"
      >
        <template #default="{ row }">
          {{ datetimeFormat(row.create_time) }}
        </template>
      </el-table-column>

      <el-table-column :label="$t('common.operation')" width="90">
        <template #default="{ row }">
          <div class="flex">
            <el-tooltip effect="dark" :content="$t('chat.executionDetails.title')" placement="top">
              <el-button type="primary" text @click.stop="toDetails(row)">
                <AppIcon iconName="app-operate-log"></AppIcon>
              </el-button>
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
    </app-table>

    <ExecutionDetailDrawer
      ref="ExecutionDetailDrawerRef"
      v-model:currentId="currentId"
      v-model:currentContent="currentContent"
      :next="nextRecord"
      :pre="preRecord"
      :pre_disable="pre_disable"
      :next_disable="next_disable"
    />
  </el-drawer>
</template>
<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { isAppIcon, resetUrl } from '@/utils/common'
import { datetimeFormat } from '@/utils/time'
import type { Dict } from '@/api/type/common'
import ExecutionDetailDrawer from './ExecutionDetailDrawer.vue'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api.ts'
import { useRoute } from 'vue-router'
const route = useRoute()
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const searchType = ref<string>('source_name')
const drawer = ref<boolean>(false)
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})
const tableData = ref<Array<any>>([])
const query = ref<any>({
  state: '',
  name: '',
  order: '',
})
const loading = ref<boolean>(false)
const current_trigger_id = ref<string>()

const ExecutionDetailDrawerRef = ref<any>()

const currentId = ref<string>('')
const currentContent = ref<string>('')

const toDetails = (row: any) => {
  currentContent.value = row
  currentId.value = row.id
  ExecutionDetailDrawerRef.value?.open(row)
}

const changeFilterHandle = () => {
  query.value = { name: '', statu: '' }
}
const changeSize = () => {
  paginationConfig.current_page = 1
  getList()
}
function handleSortChange({ prop, order }: { prop: string; order: string }) {
  query.value.order = order === 'ascending' ? `ett.${prop}` : `-ett.${prop}`
  getList()
}

const getList = (isLoading?: boolean) => {
  if (current_trigger_id.value) {
    return loadSharedApi({ type: 'tool', systemType: apiType.value })
      .pageToolRecord(
        current_trigger_id.value,
        paginationConfig,
        { ...query.value },
        isLoading ? loading : undefined,
      )
      .then((ok: any) => {
        tableData.value = ok.data.records
        paginationConfig.total = ok.data.total
      })
  } else return Promise.resolve()
}

const pre_disable = computed(() => {
  const index = tableData.value.findIndex((item) => item.id === currentId.value)
  return index === 0 && paginationConfig.current_page === 1
})

const next_disable = computed(() => {
  const index = tableData.value.findIndex((item) => item.id === currentId.value) + 1
  return (
    index >= tableData.value.length &&
    index + (paginationConfig.current_page - 1) * paginationConfig.page_size >=
      paginationConfig.total - 1
  )
})

/**
 * 下一页
 */
const nextRecord = () => {
  const index = tableData.value.findIndex((item) => item.id === currentId.value) + 1
  if (index >= tableData.value.length) {
    if (paginationConfig.current_page * paginationConfig.page_size >= paginationConfig.total) {
      return
    }
    paginationConfig.current_page = paginationConfig.current_page + 1
    getList(true).then(() => {
      currentId.value = tableData.value[index].id
      currentContent.value = tableData.value[index]
    })
    return
  } else {
    currentId.value = tableData.value[index].id
    currentContent.value = tableData.value[index]
  }
}
/**
 * 上一页
 */
const preRecord = () => {
  const index = tableData.value.findIndex((item) => item.id === currentId.value) - 1
  if (index < 0 && 1) {
    if (paginationConfig.current_page === 1) {
      return
    }
    paginationConfig.current_page = paginationConfig.current_page - 1
    getList(true).then(() => {
      currentId.value = tableData.value[tableData.value.length - 1].id
      currentContent.value = tableData.value[tableData.value.length - 1]
    })
  } else {
    currentId.value = tableData.value[index].id
    currentContent.value = tableData.value[index]
  }
}
const open = (tool: any) => {
  current_trigger_id.value = tool.id
  getList(true)
  drawer.value = true
}
const close = () => {
  paginationConfig.current_page = 1
  paginationConfig.total = 0
  tableData.value = []
  drawer.value = false
}

defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
