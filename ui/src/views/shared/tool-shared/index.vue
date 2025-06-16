<template>
  <div class="tool-shared">
    <ContentContainer>
      <template #header>
        <div class="shared-header">
          <span class="title">{{ t('views.system.shared_resources') }}</span>
          <el-icon size="12">
            <rightOutlined></rightOutlined>
          </el-icon>
          <span class="sub-title">{{ t('views.tool.title') }}</span>
        </div>
      </template>
      <template #search>
        <div class="flex">
          <div class="flex-between complex-search">
            <el-select
              class="complex-search__left"
              v-model="search_type"
              style="width: 120px"
              @change="search_type_change"
            >
              <el-option :label="$t('common.creator')" value="create_user" />

              <el-option :label="$t('views.model.modelForm.modeName.label')" value="name" />
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
          <el-button class="ml-16" type="primary"> {{ $t('common.create') }}</el-button>
        </div>
      </template>

      <div>
        <el-row v-if="toolList.length > 0" :gutter="15">
          <template v-for="(item, index) in toolList" :key="index">
            <el-col
              v-if="item.resource_type === 'folder'"
              :xs="24"
              :sm="12"
              :md="12"
              :lg="8"
              :xl="6"
              class="mb-16"
            >
              <CardBox
                :title="item.name"
                :description="item.desc || $t('common.noData')"
                class="cursor"
              >
                <template #icon>
                  <el-avatar shape="square" :size="32" style="background: none">
                    <AppIcon iconName="app-folder" style="font-size: 32px"></AppIcon>
                  </el-avatar>
                </template>
                <template #subTitle>
                  <el-text class="color-secondary lighter" size="small">
                    {{ $t('common.creator') }}: {{ item.username }}
                  </el-text>
                </template>
              </CardBox>
            </el-col>
            <el-col v-else :xs="24" :sm="12" :md="12" :lg="8" :xl="6" class="mb-16">
              <CardBox isShared :title="item.name" :description="item.desc" class="cursor">
                <template #icon>
                  <el-avatar
                    v-if="isAppIcon(item?.icon)"
                    shape="square"
                    :size="32"
                    style="background: none"
                    class="mr-8"
                  >
                    <img :src="item?.icon" alt="" />
                  </el-avatar>
                  <el-avatar v-else class="avatar-green" shape="square" :size="32">
                    <img src="@/assets/node/icon_tool.svg" style="width: 58%" alt="" />
                  </el-avatar>
                </template>
                <template #subTitle>
                  <el-text class="color-secondary lighter" size="small">
                    {{ $t('common.creator') }}: {{ item.username }}
                  </el-text>
                </template>

                <template #footer>
                  <div v-if="item.is_active" class="flex align-center">
                    <el-icon class="color-success mr-8" style="font-size: 16px">
                      <SuccessFilled />
                    </el-icon>
                    <span class="color-secondary">
                      {{ $t('common.status.enabled') }}
                    </span>
                  </div>
                  <div v-else class="flex align-center">
                    <AppIcon iconName="app-disabled" class="color-secondary mr-8"></AppIcon>
                    <span class="color-secondary">
                      {{ $t('common.status.disabled') }}
                    </span>
                  </div>
                </template>
                <template #mouseEnter>
                  <div @click.stop>
                    <el-switch
                      v-model="item.is_active"
                      :before-change="() => changeState(item)"
                      size="small"
                      class="mr-4"
                    />
                    <el-divider direction="vertical" />
                    <el-dropdown trigger="click">
                      <el-button text @click.stop>
                        <el-icon>
                          <MoreFilled />
                        </el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item
                            icon="Lock"
                            @click.stop="openAuthorizedWorkspaceDialog(item)"
                            >{{ $t('views.system.authorized_workspace') }}</el-dropdown-item
                          >
                          <el-dropdown-item
                            v-if="!item.template_id"
                            :disabled="!canEdit(item)"
                            @click.stop="openCreateDialog(item)"
                          >
                            <el-icon>
                              <EditPen />
                            </el-icon>
                            {{ $t('common.edit') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            :disabled="!canEdit(item)"
                            v-if="!item.template_id"
                            @click.stop="copyTool(item)"
                          >
                            <AppIcon iconName="app-copy"></AppIcon>
                            {{ $t('common.copy') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            v-if="item.init_field_list?.length > 0"
                            :disabled="!canEdit(item)"
                            @click.stop="configInitParams(item)"
                          >
                            <AppIcon iconName="app-operation" class="mr-4"></AppIcon>
                            {{ $t('common.param.initParam') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            v-if="!item.template_id"
                            :disabled="!canEdit(item)"
                            @click.stop="exportTool(item)"
                          >
                            <AppIcon iconName="app-export"></AppIcon>
                            {{ $t('common.export') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            :disabled="!canEdit(item)"
                            divided
                            @click.stop="deleteTool(item)"
                          >
                            <el-icon><Delete /></el-icon>
                            {{ $t('common.delete') }}
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </template>
              </CardBox>
            </el-col>
          </template>
        </el-row>
        <el-empty :description="$t('common.noData')" v-else />
      </div>
    </ContentContainer>
    <InitParamDrawer ref="InitParamDrawerRef" @refresh="refresh" />
    <ToolFormDrawer ref="ToolFormDrawerRef" @refresh="refresh" :title="ToolDrawertitle" />
    <AuthorizedWorkspace  ref="AuthorizedWorkspaceDialogRef"></AuthorizedWorkspace>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, computed } from 'vue'
import { cloneDeep, get } from 'lodash'
import ToolApi from '@/api/shared/tool'
import useStore from '@/stores/modules-shared-system'
import InitParamDrawer from '@/views/shared/tool-shared/component/InitParamDrawer.vue'
import ToolFormDrawer from './ToolFormDrawer.vue'
import { t } from '@/locales'
import { isAppIcon } from '@/utils/common'
import iconMap from '@/components/app-icon/icons/common'
import AuthorizedWorkspace from '@/views/shared/AuthorizedWorkspaceDialog.vue'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'

const { folder, user } = useStore()
const rightOutlined = iconMap['right-outlined'].iconReader()
const InitParamDrawerRef = ref()
const search_type = ref('name')
const search_form = ref<{
  name: string
  create_user: string
}>({
  name: '',
  create_user: '',
})
const user_options = ref<any[]>([])

const AuthorizedWorkspaceDialogRef = ref()
function openAuthorizedWorkspaceDialog(row: any) {
  if (AuthorizedWorkspaceDialogRef.value) {
    AuthorizedWorkspaceDialogRef.value.open(row, 'Tool')
  }
}
const loading = ref(false)
const changeStateloading = ref(false)
const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0,
})

const folderList = ref<any[]>([])
const toolList = ref<any[]>([])
const currentFolder = ref<any>({})

const search_type_change = () => {
  search_form.value = { name: '', create_user: '' }
}
const canEdit = (row: any) => {
  return user.userInfo?.id === row?.user_id
}

const ToolFormDrawerRef = ref()
const ToolDrawertitle = ref('')

function openCreateDialog(data?: any) {
  // 有template_id的不允许编辑，是模板转换来的
  if (data?.template_id) {
    return
  }
  ToolDrawertitle.value = data ? t('views.tool.editTool') : t('views.tool.createTool')
  if (data) {
    if (data?.permission_type !== 'PUBLIC' || canEdit(data)) {
      ToolApi.getToolById(data?.id, changeStateloading).then((res) => {
        ToolFormDrawerRef.value.open(res.data)
      })
    }
  } else {
    ToolFormDrawerRef.value.open(data)
  }
}

function getList() {
  const params = {
    folder_id: currentFolder.value?.id || 'root',
    scope: 'WORKSPACE',
  }
  ToolApi.getToolList(paginationConfig, params, loading).then((res) => {
    paginationConfig.total = res.data?.total
    toolList.value = [...toolList.value, ...res.data?.records]
  })
}

function getFolder() {
  const params = {}
  folder.asyncGetFolder('TOOL', params, loading).then((res: any) => {
    folderList.value = res.data
    currentFolder.value = res.data?.[0] || {}
    getList()
  })
}

async function changeState(row: any) {
  if (row.is_active) {
    MsgConfirm(
      `${t('views.tool.disabled.confirmTitle')}${row.name} ?`,
      t('views.tool.disabled.confirmMessage'),
      {
        confirmButtonText: t('common.status.disable'),
        confirmButtonClass: 'danger',
      },
    ).then(() => {
      const obj = {
        is_active: !row.is_active,
      }
      ToolApi.putTool(row.id, obj, changeStateloading)
        .then(() => {
          return true
        })
        .catch(() => {
          return false
        })
    })
  } else {
    const res = await ToolApi.getToolById(row.id, changeStateloading)
    if (
      !res.data.init_params &&
      res.data.init_field_list &&
      res.data.init_field_list.length > 0 &&
      res.data.init_field_list.filter((item: any) => item.default_value && item.show_default_value)
        .length !== res.data.init_field_list.length
    ) {
      InitParamDrawerRef.value.open(res.data, !row.is_active)
      return false
    }
    const obj = {
      is_active: !row.is_active,
    }
    ToolApi.putTool(row.id, obj, changeStateloading)
      .then(() => {
        return true
      })
      .catch(() => {
        return false
      })
  }
}

function refresh(data: any) {
  if (data) {
    const index = toolList.value.findIndex((v) => v.id === data.id)
    // if (user.userInfo && data.user_id === user.userInfo.id) {
    //   data.username = user.userInfo.username
    // } else {
    //   data.username = userOptions.value.find((v) => v.value === data.user_id)?.label
    // }
    toolList.value.splice(index, 1, data)
  }
  paginationConfig.total = 0
  paginationConfig.current_page = 1
  toolList.value = []
  getList()
}

function folderClickHandel(row: any) {
  currentFolder.value = row
  toolList.value = []
  getList()
}

function copyTool(row: any) {
  ToolDrawertitle.value = t('views.tool.copyTool')
  const obj = cloneDeep(row)
  delete obj['id']
  obj['name'] = obj['name'] + `  ${t('views.tool.form.title.copy')}`
  ToolFormDrawerRef.value.open(obj)
}

function exportTool(row: any) {
  ToolApi.exportTool(row.id, row.name, loading).catch((e: any) => {
    if (e.response.status !== 403) {
      e.response.data.text().then((res: string) => {
        MsgError(`${t('views.application.tip.ExportError')}:${JSON.parse(res).message}`)
      })
    }
  })
}

function deleteTool(row: any) {
  MsgConfirm(
    `${t('views.tool.delete.confirmTitle')}${row.name} ?`,
    t('views.tool.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      ToolApi.delTool(row.id, loading).then(() => {
        const index = toolList.value.findIndex((v) => v.id === row.id)
        toolList.value.splice(index, 1)
        MsgSuccess(t('common.deleteSuccess'))
      })
    })
    .catch(() => {})
}

function configInitParams(item: any) {
  ToolApi.getToolById(item?.id, changeStateloading).then((res) => {
    InitParamDrawerRef.value.open(res.data)
  })
}

// function importTool(file: any) {
//   const formData = new FormData()
//   formData.append('file', file.raw, file.name)
//   elUploadRef.value.clearFiles()
//   ToolApi
//     .postImportTool(formData, loading)
//     .then(async (res: any) => {
//       if (res?.data) {
//         searchHandle()
//       }
//     })
//     .catch((e: any) => {
//       if (e.code === 400) {
//         MsgConfirm(t('common.tip'), t('views.application.tip.professionalMessage'), {
//           cancelButtonText: t('common.confirm'),
//           confirmButtonText: t('common.professional')
//         }).then(() => {
//           window.open('https://maxkb.cn/pricing.html', '_blank')
//         })
//       }
//     })
// }

onMounted(() => {
  getFolder()
})
</script>

<style lang="scss" scoped>
.tool-shared {
  padding-left: 8px;
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
