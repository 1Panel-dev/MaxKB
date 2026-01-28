<template>
  <div class="trigger-manage p-16-24">
    <h2 class="ml-24 mb-16">{{ $t('views.trigger.title') }}</h2>
    <el-card style="--el-card-padding: 0">
      <div class="main-calc-height">
        <div class="p-24">
          <div class="flex-between">
            <div>
              <el-button
                v-if="triggerPermissionMap.create()"
                type="primary"
                @click="openCreateTriggerDrawer"
                >{{ $t('common.create') }}
              </el-button>
              <el-button
                v-if="triggerPermissionMap.edit()"
                @click="batchChangeState(true)"
                :disabled="multipleSelection.length === 0"
                >{{ $t('common.status.enable') }}
              </el-button>
              <el-button
                v-if="triggerPermissionMap.edit()"
                @click="batchChangeState(false)"
                :disabled="multipleSelection.length === 0"
                >{{ $t('common.status.disable') }}
              </el-button>
              <el-button
                v-if="triggerPermissionMap.delete()"
                @click="batchDelete"
                :disabled="multipleSelection.length === 0"
                >{{ $t('common.delete') }}
              </el-button>
            </div>
            <div class="flex-between complex-search">
              <el-select
                class="complex-search__left"
                v-model="search_type"
                style="width: 90px"
                @change="search_type_change"
              >
                <el-option :label="$t('common.name')" value="name" />
                <el-option :label="$t('common.type')" value="type" />
                <el-option :label="$t('views.trigger.task')" value="task" />
                <el-option :label="$t('common.status.label')" value="is_active" />
                <el-option :label="$t('common.creator')" value="create_user" />
              </el-select>
              <el-input
                v-if="search_type === 'name'"
                v-model="search_form.name"
                @change="searchHandle"
                :placeholder="$t('common.searchBar.placeholder')"
                style="width: 220px"
                clearable
              />
              <el-select
                v-else-if="search_type === 'type'"
                v-model="search_form.type"
                @change="searchHandle"
                filterable
                clearable
                style="width: 220px"
              >
                <el-option :label="$t('views.trigger.type.scheduled')" value="SCHEDULED" />
                <el-option :label="$t('views.trigger.type.event')" value="EVENT" />
              </el-select>
              <el-select
                v-else-if="search_type === 'is_active'"
                v-model="search_form.is_active"
                @change="searchHandle"
                filterable
                clearable
                style="width: 220px"
              >
                <el-option :label="$t('common.status.enable')" value="true" />
                <el-option :label="$t('common.status.disable')" value="false" />
              </el-select>
              <el-select
                v-else-if="search_type === 'create_user'"
                v-model="search_form.create_user"
                @change="searchHandle"
                filterable
                clearable
                style="width: 220px"
              >
                <el-option
                  v-for="u in user_options"
                  :key="u.id"
                  :value="u.id"
                  :label="u.nick_name"
                />
              </el-select>
              <el-input
                v-if="search_type === 'task'"
                v-model="search_form.task"
                @change="searchHandle"
                :placeholder="$t('common.search')"
                style="width: 220px"
                clearable
              />
            </div>
          </div>
          <app-table
            ref="multipleTableRef"
            class="mt-16"
            :data="triggerData"
            :pagination-config="paginationConfig"
            @sizeChange="handleSizeChange"
            @changePage="getList"
            @selection-change="handleSelectionChange"
            v-loading="loading"
            :row-key="(row: any) => row.id"
            :maxTableHeight="300"
            :tooltip-options="{
              popperClass: 'max-w-350',
            }"
          >
            <el-table-column type="selection" width="55" :reserve-selection="true" />
            <el-table-column prop="name" :label="$t('common.name')" show-overflow-tooltip>
              <template #default="{ row }">
                <div class="flex align-center">
                  <TriggerIcon :type="row.trigger_type" class="mr-8" :size="24" />
                  {{ row.name }}
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="trigger_type" :label="$t('common.type')" min-width="80">
              <template #default="{ row }">
                {{ $t(TriggerType[row.trigger_type as keyof typeof TriggerType]) }}
              </template>
            </el-table-column>
            <el-table-column prop="is_active" :label="$t('common.status.label')" min-width="90">
              <template #default="{ row }">
                <div v-if="row.is_active" class="flex align-center">
                  <el-icon class="color-success mr-8" style="font-size: 16px">
                    <SuccessFilled />
                  </el-icon>
                  <span class="color-text-primary">
                    {{ $t('common.status.enabled') }}
                  </span>
                </div>
                <div v-else class="flex align-center">
                  <AppIcon iconName="app-disabled" class="color-secondary mr-8"></AppIcon>
                  <span class="color-text-primary">
                    {{ $t('common.status.disabled') }}
                  </span>
                </div>
              </template>
            </el-table-column>
            <el-table-column
              prop="desc"
              :label="$t('common.desc')"
              min-width="160"
              show-overflow-tooltip
            >
            </el-table-column>

            <el-table-column prop="trigger_task" :label="$t('views.trigger.task')" width="180">
              <template #default="{ row }">
                <el-popover popper-class="max-w-200">
                  <template #reference>
                    <div class="flex">
                      <el-tag
                        class="info-tag mr-8 cursor"
                        v-if="
                          row.trigger_task.filter((item: any) => item.type === 'APPLICATION').length
                        "
                      >
                        {{ $t('views.application.title') }}
                        {{
                          row.trigger_task.filter((item: any) => item.type === 'APPLICATION').length
                        }}
                      </el-tag>
                      <el-tag
                        class="info-tag cursor"
                        v-if="row.trigger_task.filter((item: any) => item.type === 'TOOL').length"
                      >
                        {{ $t('views.tool.title') }}
                        {{ row.trigger_task.filter((item: any) => item.type === 'TOOL').length }}
                      </el-tag>
                    </div>
                  </template>

                  <div>
                    <!-- 智能体部分 -->
                    <div
                      v-if="
                        row.trigger_task.filter((item: any) => item.type === 'APPLICATION').length
                      "
                    >
                      <h5 class="color-input-placeholder">
                        {{ $t('views.application.title') }}
                        {{
                          row.trigger_task.filter((item: any) => item.type === 'APPLICATION').length
                        }}
                      </h5>
                      <div
                        v-for="item in row.trigger_task.filter(
                          (item: any) => item.type === 'APPLICATION',
                        )"
                        :key="item.id"
                        class="flex align-center mt-8"
                      >
                        <el-avatar shape="square" :size="20" style="background: none" class="mr-8">
                          <img :src="resetUrl(item?.icon, resetUrl('./favicon.ico'))" alt="" />
                        </el-avatar>
                        <span class="ellipsis" :title="item.name">{{ item.name }}</span>
                      </div>
                    </div>
                    <el-divider
                      class="mt-8 mb-8"
                      v-if="
                        row.trigger_task.filter((item: any) => item.type === 'APPLICATION')
                          .length &&
                        row.trigger_task.filter((item: any) => item.type === 'TOOL').length
                      "
                    />

                    <!-- 工具部分 -->
                    <div v-if="row.trigger_task.filter((item: any) => item.type === 'TOOL').length">
                      <h5 class="color-input-placeholder">
                        {{ $t('views.tool.title') }}
                        {{ row.trigger_task.filter((item: any) => item.type === 'TOOL').length }}
                      </h5>
                      <div
                        v-for="item in row.trigger_task.filter((item: any) => item.type === 'TOOL')"
                        :key="item.id"
                        class="flex align-center mt-8"
                      >
                        <el-avatar
                          v-if="item?.icon"
                          shape="square"
                          :size="20"
                          style="background: none"
                          class="mr-8"
                        >
                          <img :src="resetUrl(item?.icon)" alt="" />
                        </el-avatar>
                        <ToolIcon v-else :size="20" :type="item?.tool_type" class="mr-8" />
                        <span class="ellipsis" :title="item.name">{{ item.name }}</span>
                      </div>
                    </div>
                  </div>
                </el-popover>
              </template>
            </el-table-column>
            <el-table-column
              prop="create_time"
              :label="$t('common.createTime')"
              width="175"
              sortable
            >
              <template #default="{ row }">
                {{ datetimeFormat(row.create_time) }}
              </template>
            </el-table-column>
            <el-table-column align="left" width="160" fixed="right" :label="$t('common.operation')">
              <template #default="{ row }">
                <span v-if="triggerPermissionMap.edit()" @click.stop>
                  <el-switch
                    :before-change="() => changeState(row)"
                    :loading="loading"
                    size="small"
                    v-model="row.is_active"
                  />
                </span>
                <el-divider direction="vertical" />
                <el-tooltip effect="dark" :content="$t('common.edit')" placement="top">
                  <span class="mr-4">
                    <el-button type="primary" text @click="openEditTriggerDrawer(row)">
                      <AppIcon iconName="app-edit"></AppIcon>
                    </el-button>
                  </span>
                </el-tooltip>
                <el-tooltip
                  v-if="triggerPermissionMap.record()"
                  effect="dark"
                  :content="$t('workflow.ExecutionRecord')"
                  placement="top"
                >
                  <span class="mr-4">
                    <el-button type="primary" text @click="openExecutionRecordDrawer(row)">
                      <AppIcon iconName="app-schedule-report"></AppIcon>
                    </el-button>
                  </span>
                </el-tooltip>

                <el-tooltip
                  v-if="triggerPermissionMap.delete()"
                  effect="dark"
                  :content="$t('common.delete')"
                  placement="top"
                >
                  <span class="mr-4">
                    <el-button type="primary" text @click="deleteTrigger(row)">
                      <AppIcon iconName="app-delete"></AppIcon>
                    </el-button>
                  </span>
                </el-tooltip>
              </template>
            </el-table-column>
          </app-table>
        </div>
      </div>
    </el-card>
    <TriggerDrawer @refresh="getList()" ref="triggerDrawerRef"></TriggerDrawer>
    <TriggerTaskRecordDrawer ref="triggerTaskRecordDrawerRef"></TriggerTaskRecordDrawer>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { ElTable } from 'element-plus'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import useStore from '@/stores'
import triggerAPI from '@/api/trigger/trigger'
import { TriggerType } from '@/enums/trigger'
import { t } from '@/locales'
import TriggerTaskRecordDrawer from './execution-record/TriggerTaskRecordDrawer.vue'
import permissionMap from '@/permission'
import { datetimeFormat } from '@/utils/time'
import WorkspaceApi from '@/api/workspace/workspace'
import { resetUrl } from '@/utils/common'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import type { TriggerData } from '@/api/type/trigger'
import TriggerDrawer from '@/views/trigger/component/TriggerDrawer.vue'
import { hasPermission } from '@/utils/permission'
import { PermissionConst, RoleConst } from '@/utils/permission/data'

const { user } = useStore()

const triggerTaskRecordDrawerRef = ref<InstanceType<typeof TriggerTaskRecordDrawer>>()

const triggerDrawerRef = ref<InstanceType<typeof TriggerDrawer>>()
const openCreateTriggerDrawer = () => {
  triggerDrawerRef.value?.open()
}
const openEditTriggerDrawer = (trigger: any) => {
  triggerDrawerRef.value?.open(trigger.id)
}

const openExecutionRecordDrawer = (trigger: any) => {
  triggerTaskRecordDrawerRef.value?.open(trigger.id)
}

const loading = ref(false)
const paginationConfig = ref({
  current_page: 1,
  page_size: 20,
  total: 0,
})

const user_options = ref<any[]>([])
const search_type = ref('name')
const search_form = ref<any>({
  name: '',
  type: '',
  task: '',
  is_active: '',
  create_user: '',
})

const search_type_change = () => {
  search_form.value = {
    name: '',
    type: '',
    task: '',
    is_active: '',
    create_user: '',
  }
}

function searchHandle() {
  paginationConfig.value.current_page = 1
  triggerData.value = []
  getList()
}

function deleteTrigger(row: any) {
  MsgConfirm(`${t('views.trigger.delete.confirmTitle')} ${row.name} ?`, ``, {
    confirmButtonText: t('common.confirm'),
    confirmButtonClass: 'danger',
  }).then(() => {
    triggerAPI.deleteTrigger(row.id, loading).then(() => {
      MsgSuccess(t('common.deleteSuccess'))
      getList()
    })
  })
}

const handleSelectionChange = (val: any[]) => {
  multipleSelection.value = val
}

function batchChangeState(is_active: boolean) {
  const idList: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      idList.push(v.id)
    }
  })
  triggerAPI.activateMulTrigger({ id_list: idList, is_active: is_active }, loading).then(() => {
    const msg: string = is_active
      ? t('common.status.enableSuccess')
      : t('common.status.disableSuccess')
    MsgSuccess(msg)
    multipleTableRef.value?.clearSelection()
    getList()
  })
}

function batchDelete() {
  MsgConfirm(
    `${t('views.document.delete.confirmTitle1')} ${multipleSelection.value.length} ${t('views.trigger.delete.confirmTitle2')}`,
    '',
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger',
    },
  ).then(() => {
    const arr: string[] = []
    multipleSelection.value.map((v) => {
      if (v) {
        arr.push(v.id)
      }
    })
    triggerAPI.delMulTrigger(arr, loading).then(() => {
      MsgSuccess(t('views.document.delete.successMessage'))
      multipleTableRef.value?.clearSelection()
      getList()
    })
  })
}

const triggerPermissionMap = {
  edit: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.TRIGGER_EDIT.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  create: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.TRIGGER_CREATE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  delete: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.TRIGGER_DELETE.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
  record: () =>
    hasPermission(
      [
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        PermissionConst.TRIGGER_RECORD.getWorkspacePermissionWorkspaceManageRole,
      ],
      'OR',
    ),
}

async function changeState(row: any) {
  const obj = {
    is_active: !row.is_active,
  }
  const str = !row.is_active ? t('common.status.enableSuccess') : t('common.status.disableSuccess')
  await updateData(row.id, obj, str)
}

/**
 * 更新状态/数据
 */
function updateData(triggerId: string, data: TriggerData, msg: string) {
  triggerAPI
    .putTrigger(triggerId, data, loading)
    .then((res: any) => {
      const trigger: TriggerData = triggerData.value.find((v) => v.id === triggerId)
      if (trigger) {
        trigger.is_active = res.data.is_active
      }
      MsgSuccess(msg)
      return true
    })
    .catch(() => {
      return false
    })
}

const multipleSelection = ref<any[]>([])
const multipleTableRef = ref<InstanceType<typeof ElTable>>()

const triggerData = ref<any[]>([])

function handleSizeChange() {
  paginationConfig.value.current_page = 1
  getList()
}

function getList(bool?: boolean) {
  const param: any = {}
  if (search_form.value[search_type.value]) {
    param[search_type.value] = search_form.value[search_type.value]
  }
  triggerAPI
    .pageTrigger(paginationConfig.value, param, bool ? undefined : loading)
    .then((res: any) => {
      triggerData.value = res.data.records
      paginationConfig.value.total = res.data.total
    })
}

onMounted(() => {
  getList()
  WorkspaceApi.getAllMemberList(user.getWorkspaceId(), loading).then((res) => {
    user_options.value = res.data
  })
})
</script>
<style lang="scss" scoped></style>
