<template>
  <el-drawer v-model="drawer" title="执行记录" direction="rtl" size="800px" :before-close="close">
    <div class="lighter mb-12">
      {{ $t('views.system.resourceMapping.sub_title') }}
    </div>
    <div class="flex-between mb-16">
      <div class="flex-between complex-search">
        <el-select class="complex-search__left" v-model="searchType" style="width: 100px">
          <el-option :label="$t('common.name')" value="name" />
          <el-option :label="$t('common.status.label')" value="state" />
        </el-select>
        <el-input
          v-if="searchType === 'name'"
          v-model="query.resource_name"
          :placeholder="$t('common.search')"
          style="width: 220px"
          clearable
          @keyup.enter="page()"
        />
        <el-select
          v-else-if="searchType === 'state'"
          v-model="query.source_type"
          @change="page()"
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
      </div>
    </div>

    <app-table
      ref="multipleTableRef"
      class="mt-16"
      :data="tableData"
      :pagination-config="paginationConfig"
      @sizeChange="handleSizeChange"
      @changePage="page"
      :maxTableHeight="200"
      :row-key="(row: any) => row.id"
      v-loading="loading"
      :tooltip-options="{
        popperClass: 'max-w-350',
      }"
    >
      <el-table-column prop="name" :label="$t('common.name')" min-width="130" show-overflow-tooltip>
        <template #default="{ row }">
          <el-button link>
            <div class="flex align-center">
              <el-avatar shape="square" :size="22" style="background: none" class="mr-8">
                <img
                  v-if="row.source_type === 'TOOL'"
                  :src="resetUrl(row?.icon, resetUrl('./favicon.ico'))"
                  alt=""
                />
                <img
                  v-if="row.source_type === 'APPLICATION'"
                  :src="resetUrl(row?.icon, resetUrl('./favicon.ico'))"
                  alt=""
                />
              </el-avatar>

              <span>{{ row.source_name }}</span>
            </div>
          </el-button>
        </template>
      </el-table-column>

      <el-table-column
        prop="source_type"
        min-width="120"
        show-overflow-tooltip
        :label="$t('common.type')"
      >
        <template #default="{ row }">
          {{
            row.source_type === 'APPLICATION'
              ? $t('views.application.title')
              : $t('views.knowledge.title')
          }}
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
  </el-drawer>
</template>
<script setup lang="ts">
import { ref, reactive } from 'vue'
import { isAppIcon, resetUrl } from '@/utils/common'
import triggerAPI from '@/api/trigger/trigger'
import { datetimeFormat } from '@/utils/time'
const toDetails = (row: any) => {
  triggerAPI.getTriggerTaskRecordDetails(row.trigger_id, row.trigger_task_id, row.id).then((ok) => {
    console.log(ok)
  })
}
const searchType = ref<string>('name')
const drawer = ref<boolean>(false)
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})
const tableData = ref<Array<any>>([])
const page = () => {
  if (current_trigger_id.value) {
    triggerAPI
      .pageTriggerTaskRecord(current_trigger_id.value, paginationConfig, { ...query.value })
      .then((ok) => {
        tableData.value = ok.data.records
        paginationConfig.total = ok.data.total
      })
  }
}
const query = ref<any>({
  state: '',
  name: '',
})
const loading = ref<boolean>(false)
const current_trigger_id = ref<string>()
const open = (trigger_id: string) => {
  current_trigger_id.value = trigger_id
  drawer.value = true
  page()
}
const handleSizeChange = () => {}
const close = () => {
  drawer.value = false
}
defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
