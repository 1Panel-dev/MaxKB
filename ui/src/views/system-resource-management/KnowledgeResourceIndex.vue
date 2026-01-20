<template>
  <div class="p-16-24">
    <el-breadcrumb separator-icon="ArrowRight">
      <el-breadcrumb-item>{{ t('views.system.resource_management.label') }}</el-breadcrumb-item>
      <el-breadcrumb-item>
        <h5 class="ml-4 color-text-primary">{{ t('views.knowledge.title') }}</h5>
      </el-breadcrumb-item>
    </el-breadcrumb>
    <el-card class="mt-16" style="height: calc(var(--app-main-height) + 20px)">
      <div class="flex-between mb-16">
        <div class="complex-search">
          <el-select
            class="complex-search__left"
            v-model="search_type"
            style="width: 120px"
            @change="search_type_change"
          >
            <el-option :label="$t('common.creator')" value="create_user" />
            <el-option :label="$t('common.name')" value="name" />
            <el-option :label="$t('common.type')" value="type" />
          </el-select>
          <el-input
            v-if="search_type === 'name'"
            v-model="search_form.name"
            @change="getList"
            :placeholder="$t('common.searchBar.placeholder')"
            style="width: 220px"
            clearable
          />
          <el-select
            v-else-if="search_type === 'create_user'"
            v-model="search_form.create_user"
            @change="getList"
            filterable
            clearable
            style="width: 220px"
          >
            <el-option v-for="u in user_options" :key="u.id" :value="u.id" :label="u.nick_name" />
          </el-select>
          <el-select
            v-else-if="search_type === 'type'"
            v-model="search_form.type"
            @change="getList"
            clearable
            filterable
            style="width: 220px"
          >
            <el-option v-for="u in type_options" :key="u.id" :value="u.value" :label="u.label" />
          </el-select>
        </div>
      </div>

      <app-table
        :data="knowledgeList"
        :pagination-config="paginationConfig"
        @sizeChange="getList"
        @changePage="getList"
        :maxTableHeight="260"
      >
        <!-- <el-table-column type="selection" width="55" /> -->
        <el-table-column width="220" :label="$t('common.name')" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex align-center">
              <KnowledgeIcon :type="row.type" :size="24" />
              <span class="ml-8">
                {{ row.name }}
              </span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="tool_type" :label="$t('common.type')" width="110">
          <template #default="{ row }">
            <span v-if="row.type === 1">{{
              $t('views.knowledge.knowledgeType.webKnowledge')
            }}</span>
            <span v-else-if="row.type === 2">{{
              $t('views.knowledge.knowledgeType.larkKnowledge')
            }}</span>
            <span v-else-if="row.type === 4">{{
              $t('views.knowledge.knowledgeType.workflowKnowledge')
            }}</span>
            <span v-else>{{ $t('views.knowledge.knowledgeType.generalKnowledge') }}</span>
          </template>
        </el-table-column>
        <el-table-column
          v-if="user.isEE()"
          width="150"
          prop="workspace_name"
          :label="$t('views.workspace.title')"
          show-overflow-tooltip
        >
          <template #header>
            <div>
              <span>{{ $t('views.workspace.title') }}</span>
              <el-popover :width="200" trigger="click" :visible="workspaceVisible">
                <template #reference>
                  <el-button
                    style="margin-top: -2px"
                    :type="workspaceArr && workspaceArr.length > 0 ? 'primary' : ''"
                    link
                    @click="workspaceVisible = !workspaceVisible"
                  >
                    <el-icon>
                      <Filter />
                    </el-icon>
                  </el-button>
                </template>
                <div class="filter">
                  <div class="form-item mb-16 ml-4">
                    <div @click.stop>
                      <el-input
                        v-model="filterText"
                        :placeholder="$t('common.search')"
                        prefix-icon="Search"
                        clearable
                      />
                      <el-scrollbar height="300" v-if="filterData.length">
                        <el-checkbox-group
                          v-model="workspaceArr"
                          style="display: flex; flex-direction: column"
                        >
                          <el-checkbox
                            v-for="item in filterData"
                            :key="item.value"
                            :label="item.label"
                            :value="item.value"
                          />
                        </el-checkbox-group>
                      </el-scrollbar>
                      <el-empty v-else :description="$t('common.noData')" />
                    </div>
                  </div>
                </div>
                <div class="text-right">
                  <el-button size="small" @click="filterWorkspaceChange('clear')"
                    >{{ $t('common.clear') }}
                  </el-button>
                  <el-button type="primary" @click="filterWorkspaceChange" size="small"
                    >{{ $t('common.confirm') }}
                  </el-button>
                </div>
              </el-popover>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="nick_name" :label="$t('common.creator')" show-overflow-tooltip />
        <el-table-column :label="$t('views.document.table.updateTime')" width="180">
          <template #default="{ row }">
            {{ datetimeFormat(row.update_time) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.createTime')" width="180">
          <template #default="{ row }">
            {{ datetimeFormat(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.operation')" align="left" width="120" fixed="right">
          <template #default="{ row }">
            <el-tooltip
              effect="dark"
              :content="$t('views.system.resource_management.management')"
              placement="top"
            >
              <span class="mr-8" v-if="ManagePermission()">
                <el-button
                  type="primary"
                  text
                  :title="$t('views.system.resource_management.management')"
                  @click="
                    router.push({
                      path: `/knowledge/${row.id}/resource-management/${row.type}/document`,
                    })
                  "
                >
                  <AppIcon iconName="app-admin-operation"></AppIcon>
                </el-button>
              </span>
            </el-tooltip>
            <el-tooltip
              effect="dark"
              :content="$t('views.knowledge.setting.vectorization')"
              placement="top"
            >
              <span class="mr-8">
                <el-button
                  type="primary"
                  text
                  :title="$t('views.knowledge.setting.vectorization')"
                  @click.stop="reEmbeddingKnowledge(row)"
                  v-if="permissionPrecise.vector()"
                >
                  <AppIcon iconName="app-vectorization"></AppIcon>
                </el-button>
              </span>
            </el-tooltip>
            <el-dropdown trigger="click" v-if="MoreFilledPermission()">
              <el-button text @click.stop type="primary">
                <AppIcon iconName="app-more"></AppIcon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    @click.stop="syncKnowledge(row)"
                    v-if="row.type === 1 && permissionPrecise.sync()"
                  >
                    <AppIcon iconName="app-sync" class="color-secondary"></AppIcon>
                    {{ $t('views.knowledge.setting.sync') }}
                  </el-dropdown-item>

                  <el-dropdown-item
                    @click.stop="openGenerateDialog(row)"
                    v-if="permissionPrecise.generate()"
                  >
                    <AppIcon iconName="app-generate-question" class="color-secondary"></AppIcon>
                    {{ $t('views.document.generateQuestion.title') }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    @click="
                      router.push({
                        path: `/knowledge/${row.id}/resource-management/${row.type}/setting`,
                      })
                    "
                    v-if="permissionPrecise.edit()"
                  >
                    <AppIcon iconName="app-setting" class="color-secondary"></AppIcon>
                    {{ $t('common.setting') }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    @click.stop="openAuthorization(row)"
                    v-if="permissionPrecise.auth()"
                  >
                    <AppIcon
                      iconName="app-resource-authorization"
                      class="color-secondary"
                    ></AppIcon>
                    {{ $t('views.system.resourceAuthorization.title') }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    @click.stop="exportKnowledge(row)"
                    v-if="permissionPrecise.export()"
                  >
                    <AppIcon iconName="app-export" class="color-secondary"></AppIcon>
                    {{ $t('views.document.setting.export') }} Excel
                  </el-dropdown-item>
                  <el-dropdown-item
                    @click.stop="exportZipKnowledge(row)"
                    v-if="permissionPrecise.export()"
                  >
                    <AppIcon iconName="app-export" class="color-secondary"></AppIcon>
                    {{ $t('views.document.setting.export') }} ZIP
                  </el-dropdown-item>
                  <el-dropdown-item
                    text
                    @click.stop="openResourceMappingDrawer(row)"
                    v-if="permissionPrecise.relate_map()"
                  >
                    <AppIcon iconName="app-resource-mapping" class="color-secondary"></AppIcon>
                    {{ $t('views.system.resourceMapping.title') }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    type="danger"
                    @click.stop="deleteKnowledge(row)"
                    v-if="permissionPrecise.delete()"
                  >
                    <AppIcon iconName="app-delete" class="color-secondary"></AppIcon>
                    {{ $t('common.delete') }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </app-table>
    </el-card>
    <SyncWebDialog ref="SyncWebDialogRef" />
    <GenerateRelatedDialog ref="GenerateRelatedDialogRef" apiType="systemManage" />
    <ResourceAuthorizationDrawer
      :type="SourceTypeEnum.KNOWLEDGE"
      ref="ResourceAuthorizationDrawerRef"
    />
    <ResourceMappingDrawer ref="resourceMappingDrawerRef"></ResourceMappingDrawer>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import KnowledgeResourceApi from '@/api/system-resource-management/knowledge'
import UserApi from '@/api/user/user'
import SyncWebDialog from '@/views/knowledge/component/SyncWebDialog.vue'
import GenerateRelatedDialog from '@/components/generate-related-dialog/index.vue'
import ResourceAuthorizationDrawer from '@/components/resource-authorization-drawer/index.vue'
import { datetimeFormat } from '@/utils/time'
import { loadPermissionApi } from '@/utils/dynamics-api/permission-api.ts'
import permissionMap from '@/permission'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { SourceTypeEnum } from '@/enums/common'
import { t } from '@/locales'
import useStore from '@/stores'
import { hasPermission } from '@/utils/permission'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
import ResourceMappingDrawer from '@/components/resource_mapping/index.vue'

const router = useRouter()
const { user } = useStore()

const permissionPrecise = computed(() => {
  return permissionMap['knowledge']['systemManage']
})

const ManagePermission = () => {
  return (
    permissionPrecise.value.doc_read() ||
    permissionPrecise.value.problem_read() ||
    permissionPrecise.value.edit() ||
    permissionPrecise.value.knowledge_chat_user_read() ||
    permissionPrecise.value.hit_test() ||
    hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_KNOWLEDGE_WORKFLOW_READ], 'OR')
  )
}

const MoreFilledPermission = () => {
  return (['sync', 'generate', 'edit', 'export', 'delete', 'auth', 'relate_map'] as const).some(
    (key) => permissionPrecise.value[key](),
  )
}

const search_type = ref('name')
const search_form = ref<any>({
  name: '',
  create_user: '',
  type: '',
})
const user_options = ref<any[]>([])
const type_options = ref<any[]>([
  {
    label: t('views.knowledge.knowledgeType.generalKnowledge'),
    value: '0',
  },
  {
    label: t('views.knowledge.knowledgeType.webKnowledge'),
    value: '1',
  },
  {
    label: t('views.knowledge.knowledgeType.larkKnowledge'),
    value: '2',
  },
  {
    label: t('views.knowledge.knowledgeType.workflowKnowledge'),
    value: '4',
  },
])
const loading = ref(false)
const knowledgeList = ref<any[]>([])
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})

const ResourceAuthorizationDrawerRef = ref()

function openAuthorization(item: any) {
  ResourceAuthorizationDrawerRef.value.open(item.id)
}

const exportKnowledge = (item: any) => {
  KnowledgeResourceApi.exportKnowledge(item.name, item.id, loading).then(() => {
    MsgSuccess(t('common.exportSuccess'))
  })
}
const exportZipKnowledge = (item: any) => {
  KnowledgeResourceApi.exportZipKnowledge(item.name, item.id, loading).then(() => {
    MsgSuccess(t('common.exportSuccess'))
  })
}

function deleteKnowledge(row: any) {
  MsgConfirm(
    `${t('views.knowledge.delete.confirmTitle')}${row.name} ?`,
    row.resource_count > 0
      ? t('views.knowledge.delete.resourceCountMessage', row.resource_count)
      : '',
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      KnowledgeResourceApi.delKnowledge(row.id, loading).then(() => {
        getList()
        MsgSuccess(t('common.deleteSuccess'))
      })
    })
    .catch(() => {})
}

const GenerateRelatedDialogRef = ref<InstanceType<typeof GenerateRelatedDialog>>()

function openGenerateDialog(row: any) {
  if (GenerateRelatedDialogRef.value) {
    GenerateRelatedDialogRef.value.open([], 'knowledge', row)
  }
}

const SyncWebDialogRef = ref()

function syncKnowledge(row: any) {
  SyncWebDialogRef.value.open(row.id)
}

function reEmbeddingKnowledge(row: any) {
  KnowledgeResourceApi.putReEmbeddingKnowledge(row.id).then(() => {
    MsgSuccess(t('common.submitSuccess'))
  })
}

const workspaceOptions = ref<any[]>([])
const workspaceVisible = ref(false)
const workspaceArr = ref<any[]>([])

const filterText = ref('')
const filterData = ref<any[]>([])

watch(
  [() => workspaceOptions.value, () => filterText.value],
  () => {
    if (!filterText.value.length) {
      filterData.value = workspaceOptions.value
    }
    filterData.value = workspaceOptions.value.filter((v: any) =>
      v.label.toLowerCase().includes(filterText.value.toLowerCase()),
    )
  },
  { immediate: true },
)

function filterWorkspaceChange(val: string) {
  if (val === 'clear') {
    workspaceArr.value = []
  }
  filterText.value = ''
  getList()
  workspaceVisible.value = false
}

async function getWorkspaceList() {
  if (user.isEE()) {
    const res = await loadPermissionApi('workspace').getSystemWorkspaceList(loading)
    workspaceOptions.value = res.data.map((item: any) => ({
      label: item.name,
      value: item.id,
    }))
  }
}

const search_type_change = () => {
  search_form.value = { name: '', create_user: '' }
}

function getList() {
  const params: any = {}
  if (search_form.value[search_type.value]) {
    params[search_type.value] = search_form.value[search_type.value]
  }
  if (workspaceArr.value.length > 0) {
    params.workspace_ids = JSON.stringify(workspaceArr.value)
  }
  KnowledgeResourceApi.getKnowledgeListPage(paginationConfig, params, loading).then((res: any) => {
    paginationConfig.total = res.data?.total
    knowledgeList.value = res.data?.records
  })
}

const resourceMappingDrawerRef = ref<InstanceType<typeof ResourceMappingDrawer>>()
const openResourceMappingDrawer = (knowledge: any) => {
  resourceMappingDrawerRef.value?.open('KNOWLEDGE', knowledge)
}
onMounted(() => {
  getWorkspaceList()
  getList()

  UserApi.getAllMemberList('').then((res: any) => {
    user_options.value = res.data
  })
})
</script>

<style lang="scss" scoped></style>
