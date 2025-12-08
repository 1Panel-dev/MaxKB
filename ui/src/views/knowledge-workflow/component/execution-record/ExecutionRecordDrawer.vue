<template>
  <el-drawer
    v-model="drawer"
    :title="$t('workflow.ExecutionRecord')"
    direction="rtl"
    size="800px"
    :before-close="close"
  >
    <div class="flex mb-16">
      <div class="flex-between complex-search">
        <el-select
          v-model="filter_type"
          class="complex-search__left"
          @change="changeFilterHandle"
          style="width: 120px"
        >
          <el-option :label="$t('workflow.initiator')" value="user_name" />
          <el-option :label="$t('common.status.label')" value="state" />
        </el-select>
        <el-select
          v-if="filter_type === 'state'"
          v-model="query.state"
          @change="getList(true)"
          style="width: 220px"
          clearable
        >
          <el-option :label="$t('common.status.success')" value="SUCCESS" />
          <el-option :label="$t('common.status.fail')" value="FAILURE" />
          <el-option :label="$t('common.status.padding')" value="PADDING" />
        </el-select>
        <el-input
          v-else
          v-model="query.user_name"
          @change="getList(true)"
          :placeholder="$t('common.search')"
          prefix-icon="Search"
          style="width: 220px"
          clearable
        />
      </div>
    </div>

    <app-table-infinite-scroll
      :data="data"
      class="w-full"
      v-loading="loading"
      @changePage="changePage"
      :maxTableHeight="150"
      :paginationConfig="paginationConfig"
      :row-class-name="setRowClass"
    >
      <el-table-column prop="user_name" :label="$t('workflow.initiator')">
        <template #default="{ row }">
          {{ row.meta.user_name }}
        </template>
      </el-table-column>
      <el-table-column prop="state" :label="$t('common.status.label')" width="180">
        <template #default="{ row }">
          <el-text class="color-text-primary" v-if="row.state === 'SUCCESS'">
            <el-icon class="color-success"><SuccessFilled /></el-icon>
            {{ $t('common.status.success') }}
          </el-text>
          <el-text class="color-text-primary" v-else-if="row.state === 'FAILURE'">
            <el-icon class="color-danger"><CircleCloseFilled /></el-icon>
            {{ $t('common.status.fail') }}
          </el-text>
          <el-text class="color-text-primary" v-else>
            <el-icon class="is-loading color-primary"><Loading /></el-icon>
            {{ $t('common.status.padding') }}
          </el-text>
        </template>
      </el-table-column>
      <el-table-column prop="run_time" :label="$t('chat.KnowledgeSource.consumeTime')">
        <template #default="{ row }">
          {{ row.run_time != undefined ? row.run_time + 's' : '-' }}
        </template>
      </el-table-column>
      <el-table-column
        prop="create_time"
        :label="$t('chat.executionDetails.createTime')"
        width="180"
      >
        <template #default="{ row }">
          {{ datetimeFormat(row.create_time) }}
        </template>
      </el-table-column>

      <el-table-column :label="$t('common.operation')" width="80">
        <template #default="{ row }">
          <el-tooltip effect="dark" :content="$t('chat.executionDetails.title')" placement="top">
            <el-button type="primary" text @click.stop="toDetails(row)">
              <AppIcon iconName="app-operate-log"></AppIcon>
            </el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </app-table-infinite-scroll>
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
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import AppTableInfiniteScroll from '@/components/app-table-infinite-scroll/index.vue'
import ExecutionDetailDrawer from './ExecutionDetailDrawer.vue'
import { computed, ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { datetimeFormat } from '@/utils/time'
import type { Dict } from '@/api/type/common'
const drawer = ref<boolean>(false)
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
const paginationConfig = reactive({
  current_page: 1,
  page_size: 10,
  total: 0,
})
const query = ref<any>({
  user_name: '',
  state: '',
})
const loading = ref(false)
const filter_type = ref<string>('user_name')
const active_knowledge_id = ref<string>('')
const data = ref<Array<any>>([])
const tableIndexMap = computed<Dict<number>>(() => {
  return data.value
    .map((row, index) => ({
      [row.id]: index,
    }))
    .reduce((pre, next) => ({ ...pre, ...next }), {})
})
const ExecutionDetailDrawerRef = ref<any>()
const currentId = ref<string>('')
const currentContent = ref<string>('')

const toDetails = (row: any) => {
  currentContent.value = row
  currentId.value = row.id

  ExecutionDetailDrawerRef.value?.open()
}

const changeFilterHandle = () => {
  query.value = { user_name: '', status: '' }
}
const changePage = () => {
  paginationConfig.current_page += 1
  getList()
}

const getList = (clear?: boolean) => {
  if (clear) {
    paginationConfig.current_page = 1
  }
  return loadSharedApi({ type: 'knowledge', systemType: apiType.value })
    .getWorkflowActionPage(active_knowledge_id.value, paginationConfig, query.value, loading)
    .then((ok: any) => {
      paginationConfig.total = ok.data?.total
      if (clear) {
        data.value = ok.data.records
      } else {
        data.value = data.value.concat(ok.data.records)
      }
    })
}

const pre_disable = computed(() => {
  const index = tableIndexMap.value[currentId.value] - 1
  return index < 0
})

const next_disable = computed(() => {
  const index = tableIndexMap.value[currentId.value] + 1
  return index >= data.value.length && index >= paginationConfig.total - 1
})
/**
 * 上一页
 */
const preRecord = () => {
  const index = tableIndexMap.value[currentId.value] - 1
  console.log('index', index)

  if (index >= 0) {
    currentId.value = data.value[index].id
    currentContent.value = data.value[index]
  }
}

const open = (knowledge_id: string) => {
  active_knowledge_id.value = knowledge_id
  getList()
  drawer.value = true
}
const close = () => {
  paginationConfig.current_page = 1
  paginationConfig.total = 0
  data.value = []
  drawer.value = false
}
defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
