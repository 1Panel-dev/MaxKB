<template>
  <div class="document p-16-24">
    <h2 class="mb-16">{{ $t('views.trigger.title') }}</h2>
    <el-card style="--el-card-padding: 0">
      <div class="main-calc-height">
        <div class="p-24">
          <div class="flex-between">
            <div>
              <el-button type="primary" @click="openCreateTriggerDrawer"
                >{{ $t('common.create') }}
              </el-button>
              <el-button @click="batchChangeState(true)" :disabled="multipleSelection.length === 0"
                >{{ $t('views.trigger.activate', '启用') }}
              </el-button>
              <el-button @click="batchChangeState(false)" :disabled="multipleSelection.length === 0"
                >{{ $t('view.trigger.ban', '禁用') }}
              </el-button>
              <el-button @click="batchDelete" :disabled="multipleSelection.length === 0"
                >{{ $t('common.delete') }}
              </el-button>
            </div>
            <div class="flex-between complex-search">
              <el-select
                class="complex-search__left"
                v-model="search_type"
                style="width: 120px"
                @change="search_type_change"
              >
                <el-option :label="$t('common.name', '名称')" value="name" />
                <el-option :label="$t('view.trigger.type', '类型')" value="type" />
                <el-option :label="$t('view.trigger.task', '任务')" value="task" />
                <el-option :label="$t('view.trigger.status', '状态')" value="is_active" />
                <el-option :label="$t('view.trigger.createUser', '创建者')" value="create_user" />
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
                <el-option :label="$t('view.trigger.scheduled', '定时触发')" value="SCHEDULED" />
                <el-option :label="$t('view.trigger.event', '事件触发')" value="EVENT" />
              </el-select>
              <el-select
                v-else-if="search_type === 'is_active'"
                v-model="search_form.is_active"
                @change="searchHandle"
                filterable
                clearable
                style="width: 220px"
              >
                <el-option :label="$t('view.trigger.active', '启用')" value="true" />
                <el-option :label="$t('view.trigger.ban', '禁用')" value="false" />
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
                :placeholder="$t('views.document.tag.requiredMessage3')"
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
          >
            <el-table-column type="selection" width="55" :reserve-selection="true" />
            <el-table-column
              prop="name"
              :label="$t('views.trigger.table.name', '名称')"
              min-width="100"
            >
            </el-table-column>
            <el-table-column
              prop="trigger_type"
              :label="$t('views.trigger.table.type', '类型')"
              min-width="80"
            >
            </el-table-column>
            <el-table-column
              prop="is_active"
              :label="$t('views.trigger.table.status', '状态')"
              min-width="80"
            >
            </el-table-column>
            <el-table-column
              prop="desc"
              :label="$t('views.trigger.table.desc', '描述')"
              min-width="150"
            >
            </el-table-column>
            <el-table-column
              prop="update_time"
              :label="$t('views.document.table.updateTime')"
              width="175"
              sortable
            >
              <template #default="{ row }">
                {{ datetimeFormat(row.update_time) }}
              </template>
            </el-table-column>
            <el-table-column
              prop="trigger_task"
              :label="$t('views.trigger.table.task', '任务')"
              width="180"
            >
              <template #default="{ row }">
                <el-popover>
                  <template #reference>
                    <div class="flex">
                      <el-check-tag
                        type="info"
                        class="mr-8"
                        v-if="
                          row.trigger_task.filter((item: any) => item.type === 'APPLICATION')
                            .length !== 0
                        "
                      >
                        智能体
                        {{
                          row.trigger_task.filter((item: any) => item.type === 'APPLICATION').length
                        }}
                      </el-check-tag>
                      <el-check-tag
                        type="info"
                        v-if="
                          row.trigger_task.filter((item: any) => item.type === 'TOOL').length !== 0
                        "
                      >
                        工具
                        {{ row.trigger_task.filter((item: any) => item.type === 'TOOL').length }}
                      </el-check-tag>
                    </div>
                  </template>

                  <div>
                    <!-- 智能体部分 -->
                    <div
                      class="color-secondary mb-8"
                      v-if="
                        row.trigger_task.filter((item: any) => item.type === 'APPLICATION')
                          .length !== 0
                      "
                    >
                      智能体
                      {{
                        row.trigger_task.filter((item: any) => item.type === 'APPLICATION').length
                      }}
                    </div>
                    <div
                      v-for="item in row.trigger_task.filter(
                        (item: any) => item.type === 'APPLICATION',
                      )"
                      :key="item.id"
                      class="flex align-center mb-8"
                    >
                      <el-avatar shape="square" :size="20" style="background: none" class="mr-8">
                        <img :src="resetUrl(item?.icon, resetUrl('./favicon.ico'))" alt="" />
                      </el-avatar>
                      <span>{{ item.name }}</span>
                    </div>
                    <el-divider
                      class="mt-8 mb-8"
                      v-if="
                        row.trigger_task.some((item: any) => item.type === 'APPLICATION') &&
                        row.trigger_task.some((item: any) => item.type === 'TOOL')
                      "
                    />
                    <!-- 工具部分 -->
                    <div
                      class="color-secondary mb-8"
                      v-if="
                        row.trigger_task.filter((item: any) => item.type === 'TOOL').length !== 0
                      "
                    >
                      工具 {{ row.trigger_task.filter((item: any) => item.type === 'TOOL').length }}
                    </div>
                    <div
                      v-for="item in row.trigger_task.filter((item: any) => item.type === 'TOOL')"
                      :key="item.id"
                      class="flex align-center mb-8"
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
                      <span>{{ item.name }}</span>
                    </div>
                  </div>
                </el-popover>
              </template>
            </el-table-column>
            <el-table-column align="left" width="160" fixed="right" :label="$t('common.operation')">
              <template #default="{ row }">
                <span @click.stop>
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
                      <AppIcon iconName="app-edit" class="color-secondary"></AppIcon>
                    </el-button>
                  </span>
                </el-tooltip>
                <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
                  <span class="mr-4">
                    <el-button type="primary" text @click="deleteTrigger(row)">
                      <AppIcon iconName="app-delete" class="color-secondary"></AppIcon>
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
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute, onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'
import type { ElTable } from 'element-plus'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import useStore from '@/stores'
import triggerAPI from '@/api/trigger/trigger'
import { TaskType, State } from '@/utils/status'
import { t } from '@/locales'
import permissionMap from '@/permission'
import { datetimeFormat } from '@/utils/time'
import WorkspaceApi from '@/api/workspace/workspace'
import { resetUrl } from '@/utils/common'

import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import type { TriggerData } from '@/api/type/trigger'

import TriggerDrawer from '@/views/trigger/component/TriggerDrawer.vue'

const triggerDrawerRef = ref<InstanceType<typeof TriggerDrawer>>()
const openCreateTriggerDrawer = () => {
  triggerDrawerRef.value?.open()
}
const openEditTriggerDrawer = (trigger: any) => {
  triggerDrawerRef.value?.open(trigger.id)
}
const route = useRoute()
const router = useRouter()
const {
  params: { id, folderId, type }, // id为knowledgeID
} = route as any
const { user } = useStore()
const loading = ref(false)
const paginationConfig = ref({
  current_page: 1,
  page_size: 10,
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
  MsgConfirm(`${t('views.document.delete.confirmTitle3', '是否删除触发器')} ${row.name} ?`, ``, {
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
      ? t('views.trigger.delete.successMessage', '批量启用成功')
      : t('views.trigger.delete.successMessage', '批量禁用成功')
    MsgSuccess(msg)
    multipleTableRef.value?.clearSelection()
    getList()
  })
}

function batchDelete() {
  MsgConfirm(
    `${t('views.document.delete.confirmTitle1')} ${multipleSelection.value.length} ${t('views.trigger.delete.confirmTitle2', '个触发器?')}`,
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
const elUploadRef = ref()

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
<style lang="scss" scoped>
.document {
  .mul-operation {
    position: fixed;
    margin-left: var(--sidebar-width);
    bottom: 0;
    right: 24px;
    width: calc(100% - var(--sidebar-width) - 48px);
    padding: 16px 24px;
    box-sizing: border-box;
    background: #ffffff;
    z-index: 22;
    box-shadow: 0px -2px 4px 0px rgba(31, 35, 41, 0.08);
  }
  .document-table {
    :deep(.el-table__row) {
      cursor: pointer;
    }
  }
}
</style>
