<template>
  <div class="resource-manage_knowledge">
    <div class="shared-header">
      <span class="title">{{ t('views.system.resource_management.label') }}</span>
      <el-icon size="12">
        <rightOutlined></rightOutlined>
      </el-icon>
      <span class="sub-title">{{ t('views.knowledge.title') }}</span>
    </div>
    <div class="table-content">
      <div class="flex-between complex-search">
        <el-select
          class="complex-search__left"
          v-model="search_type"
          style="width: 120px"
          @change="search_type_change"
        >
          <el-option :label="$t('common.creator')" value="create_user" />

          <el-option :label="$t('common.name')" value="name" />
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
          clearable
          style="width: 220px"
        >
          <el-option v-for="u in user_options" :key="u.id" :value="u.id" :label="u.username" />
        </el-select>
      </div>
      <div class="table-knowledge">
        <el-table height="100%" :data="knowledgeList" style="width: 100%">
          <el-table-column type="selection" width="55" />
          <el-table-column width="220" :label="$t('common.name')">
            <template #default="scope">
              <div class="table-name flex align-center">
                <el-icon size="24">
                  <KnowledgeIcon size="24" :type="scope.row.type" />
                </el-icon>
                {{ scope.row.name }}
              </div>
            </template>
          </el-table-column>
          <el-table-column
            property="type"
            :label="$t('views.application.form.appType.label')"
            width="120"
          />
          <el-table-column width="100" property="workspace_name">
            <template #header>
              <div class="flex align-center">
                {{ $t('views.role.member.workspace') }}

                <el-popover placement="bottom">
                  <template #reference
                    ><el-icon style="margin-left: 4px; cursor: pointer" size="16">
                      <AppIcon iconName="app-filter_outlined"></AppIcon> </el-icon
                  ></template>
                  <div>
                    <el-checkbox
                      v-model="checkAll"
                      :indeterminate="isIndeterminate"
                      @change="handleCheckAllChange"
                    >
                      {{ $t('views.document.feishu.allCheck') }}
                    </el-checkbox>
                    <el-checkbox-group
                      v-model="checkedWorkspaces"
                      @change="handleCheckedWorkspacesChange"
                    >
                      <el-checkbox
                        v-for="workspace in workspaces"
                        :key="workspace"
                        :label="workspace"
                        :value="workspace"
                      >
                        {{ workspace }}
                      </el-checkbox>
                    </el-checkbox-group>
                  </div>
                </el-popover>
              </div>
            </template>
          </el-table-column>
          <el-table-column property="nick_name" :label="$t('common.creator')" />
          <el-table-column
            property="update_time"
            sortable
            width="180"
            :formatter="formatter"
            :label="$t('views.document.table.updateTime')"
          />
          <el-table-column
            width="180"
            property="create_time"
            sortable
            :formatter="formatter"
            :label="$t('common.createTime')"
          />
          <el-table-column
            class-name="operation-column_text"
            width="120"
            fixed="right"
            :label="$t('common.operation')"
          >
            <template #default="scope">
              <el-button
                @click="
                  router.push({
                    path: `/knowledge/resource/${scope.row.id}/documentResource`,
                  })
                "
                text
                type="primary"
              >
                <el-icon size="16">
                  <AppIcon iconName="app-icon-blue"></AppIcon>
                </el-icon>
              </el-button>
              <el-button @click="reEmbeddingKnowledge(scope.row)" text type="primary">
                <el-icon size="16">
                  <AppIcon iconName="app-vectorization"></AppIcon>
                </el-icon>
              </el-button>
              <el-dropdown trigger="click">
                <el-button text @click.stop>
                  <el-icon size="16">
                    <MoreFilled />
                  </el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item
                      icon="Refresh"
                      @click.stop="syncKnowledge(scope.row)"
                      v-if="scope.row.type === 1"
                      >{{ $t('views.knowledge.setting.sync') }}
                    </el-dropdown-item>
                    <el-dropdown-item
                      icon="Connection"
                      @click.stop="openGenerateDialog(scope.row)"
                      >{{ $t('views.document.generateQuestion.title') }}</el-dropdown-item
                    >
                    <el-dropdown-item @click.stop="exportKnowledge(scope.row)">
                      <AppIcon iconName="app-export"></AppIcon
                      >{{ $t('views.document.setting.export') }} Excel</el-dropdown-item
                    >
                    <el-dropdown-item @click.stop="exportZipKnowledge(scope.row)">
                      <AppIcon iconName="app-export"></AppIcon
                      >{{ $t('views.document.setting.export') }} ZIP</el-dropdown-item
                    >
                    <el-dropdown-item icon="Delete" @click.stop="deleteKnowledge(scope.row)">{{
                      $t('common.delete')
                    }}</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div class="table__pagination mt-16">
        <el-pagination
          v-model:current-page="paginationConfig.current_page"
          v-model:page-size="paginationConfig.page_size"
          :page-sizes="pageSizes"
          :total="paginationConfig.total"
          layout="total, prev, pager, next, sizes"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
  <component :is="currentCreateDialog" ref="CreateKnowledgeDialogRef" />
  <CreateFolderDialog ref="CreateFolderDialogRef" @refresh="refreshFolder" />
  <GenerateRelatedDialog ref="GenerateRelatedDialogRef" />
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, shallowRef, nextTick } from 'vue'
import CreateKnowledgeDialog from './create-component/CreateKnowledgeDialog.vue'
import CreateWebKnowledgeDialog from './create-component/CreateWebKnowledgeDialog.vue'
import CreateLarkKnowledgeDialog from './create-component/CreateLarkKnowledgeDialog.vue'
import CreateFolderDialog from '@/components/folder-tree/CreateFolderDialog.vue'
import GenerateRelatedDialog from '@/components/generate-related-dialog/index.vue'
import KnowledgeApi from '@/api/resource-management/knowledge'
import SharedWorkspace from '@/views/shared/knowledge-shared/SharedWorkspace.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import useStore from '@/stores/modules-resource-management'
import { numberFormat } from '@/utils/common'
import iconMap from '@/components/app-icon/icons/common'
import { t } from '@/locales'
import { useRouter } from 'vue-router'
import type { CheckboxValueType } from 'element-plus'

const router = useRouter()
const { folder } = useStore()
let knowledgeListbp = []
const loading = ref(false)

const search_type = ref('name')
const search_form = ref<any>({
  name: '',
  create_user: '',
})

const user_options = ref<any[]>([])

const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0,
})
const pageSizes = [10, 20, 50, 100]

const folderList = ref<any[]>([])
const knowledgeList = ref<any[]>([])
const currentFolder = ref<any>({})
const rightOutlined = iconMap['right-outlined'].iconReader()

const CreateKnowledgeDialogRef = ref()
const currentCreateDialog = shallowRef<any>(null)
const checkAll = ref(false)
const isIndeterminate = ref(true)
const checkedWorkspaces = ref([])
let workspaces = []

const handleCheckAllChange = (val: CheckboxValueType) => {
  checkedWorkspaces.value = val ? workspaces : []
  isIndeterminate.value = false
  knowledgeList.value = val ? [...knowledgeListbp] : []
}
const handleCheckedWorkspacesChange = (value: CheckboxValueType[]) => {
  const checkedCount = value.length
  checkAll.value = checkedCount === workspaces.length
  isIndeterminate.value = checkedCount > 0 && checkedCount < workspaces.length
  knowledgeList.value = knowledgeListbp.filter((ele) => value.includes(ele.workspace_id))
}

const handleSizeChange = (val) => {
  console.log(val)
}
const handleCurrentChange = (val) => {
  console.log(val)
}
function openCreateDialog(data: any) {
  currentCreateDialog.value = data
  nextTick(() => {
    CreateKnowledgeDialogRef.value.open(currentFolder.value)
  })

  // common.asyncGetValid(ValidType.Dataset, ValidCount.Dataset, loading).then(async (res: any) => {
  //   if (res?.data) {
  //     CreateDatasetDialogRef.value.open()
  //   } else if (res?.code === 400) {
  //     MsgConfirm(t('common.tip'), t('views.knowledge.tip.professionalMessage'), {
  //       cancelButtonText: t('common.confirm'),
  //       confirmButtonText: t('common.professional'),
  //     })
  //       .then(() => {
  //         window.open('https://maxkb.cn/pricing.html', '_blank')
  //       })
  //       .catch(() => {})
  //   }
  // })
}

function reEmbeddingKnowledge(row: any) {
  KnowledgeApi.putReEmbeddingKnowledge(row.id).then(() => {
    MsgSuccess(t('common.submitSuccess'))
  })
}

const SyncWebDialogRef = ref()

function syncKnowledge(row: any) {
  SyncWebDialogRef.value.open(row.id)
}

const search_type_change = () => {
  search_form.value = { name: '', create_user: '' }
}

function getList() {
  console.log(currentFolder.value?.id)
  const params = {
    folder_id: currentFolder.value?.id || localStorage.getItem('workspace_id'),
    [search_type.value]: search_form.value[search_type.value],
  }

  KnowledgeApi.getKnowledgeListPage(paginationConfig, params, loading).then((res) => {
    paginationConfig.total = res.data.total
    knowledgeListbp = [...res.data.records]
    workspaces = [...new Set(knowledgeListbp.map((ele) => ele.workspace_id))]
    checkedWorkspaces.value = [...workspaces]
    checkAll.value = true
    handleCheckAllChange(true)
  })
}

function folderClickHandel(row: any) {
  currentFolder.value = row
  knowledgeList.value = []
  if (currentFolder.value.id === 'share') return
  getList()
}

function clickFolder(item: any) {
  currentFolder.value.id = item.id
  knowledgeList.value = []
  getList()
}

const CreateFolderDialogRef = ref()

function openCreateFolder() {
  CreateFolderDialogRef.value.open('KNOWLEDGE', currentFolder.value.id)
}

const GenerateRelatedDialogRef = ref<InstanceType<typeof GenerateRelatedDialog>>()
function openGenerateDialog(row: any) {
  if (GenerateRelatedDialogRef.value) {
    GenerateRelatedDialogRef.value.open([], 'knowledge', row.id)
  }
}

const formatter = (_, __, value) => {
  return value ? new Date(value).toLocaleString() : '-'
}

const exportKnowledge = (item: any) => {
  KnowledgeApi.exportKnowledge(item.name, item.id, loading).then((ok) => {
    MsgSuccess(t('common.exportSuccess'))
  })
}
const exportZipKnowledge = (item: any) => {
  KnowledgeApi.exportZipKnowledge(item.name, item.id, loading).then((ok) => {
    MsgSuccess(t('common.exportSuccess'))
  })
}

function deleteKnowledge(row: any) {
  MsgConfirm(
    `${t('views.knowledge.delete.confirmTitle')}${row.name} ?`,
    `${t('views.knowledge.delete.confirmMessage1')} ${row.application_mapping_count} ${t('views.knowledge.delete.confirmMessage2')}`,
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'color-danger',
    },
  )
    .then(() => {
      KnowledgeApi.delKnowledge(row.id, loading).then(() => {
        const index = knowledgeList.value.findIndex((v) => v.id === row.id)
        knowledgeList.value.splice(index, 1)
        MsgSuccess(t('common.deleteSuccess'))
      })
    })
    .catch(() => {})
}

function refreshFolder() {
  knowledgeList.value = []
  getList()
}

onMounted(() => {
  getList()
})
</script>

<style lang="scss" scoped>
.resource-manage_knowledge {
  padding: 16px 24px;
  .complex-search {
    width: 280px;
  }
  .complex-search__left {
    width: 75px;
  }

  .el-avatar {
    --el-avatar-size: 24px;
  }

  .table-content {
    padding: 24px;
    background-color: #fff;
    border-radius: 4px;
    box-shadow: 0px 2px 4px 0px #1f23291f;
    margin-top: 16px;
    height: calc(100vh - 180px);

    .table-knowledge {
      height: calc(100% - 100px);
      margin-top: 16px;

      .table-name {
        .el-icon {
          margin-right: 8px;
        }
      }

      .operation-column_text {
        .el-button.is-text {
          --el-button-text-color: #3370ff;
        }
        .el-button.is-text:not(.is-disabled):hover {
          background-color: #3370ff1a;
        }
        .el-button + .el-button,
        .el-button + .el-dropdown {
          margin-left: 4px;
        }
      }
    }

    .table__pagination {
      display: flex;
      align-items: center;
      justify-content: flex-end;
    }
  }
  .shared-header {
    color: #646a73;
    font-weight: 400;
    font-size: 14px;
    line-height: 22px;
    display: flex;
    align-items: center;

    :deep(.el-icon i) {
      height: 12px;
    }

    .sub-title {
      color: #1f2329;
    }
  }
}
</style>
