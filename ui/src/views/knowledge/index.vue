<template>
  <LayoutContainer class="knowledge-manage">
    <template #left>
      <h4 class="p-16 pb-0">{{ $t('views.knowledge.title') }}</h4>
      <folder-tree
        :source="FolderSource.KNOWLEDGE"
        :data="folderList"
        :currentNodeKey="currentFolder?.id"
        @handleNodeClick="folderClickHandel"
        class="p-8"
        isShared
        @refreshTree="refreshFolder"
      />
    </template>
    <SharedWorkspace v-if="currentFolder.id === 'share'"></SharedWorkspace>
    <ContentContainer v-else :header="currentFolder?.name">
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
          <el-dropdown trigger="click">
            <el-button
              type="primary"
              class="ml-8"
              v-hasPermission="[
                RoleConst.ADMIN.getWorkspaceRole,
                PermissionConst.KNOWLEDGE_CREATE.getWorkspacePermission,
              ]"
            >
              {{ $t('common.create') }}
              <el-icon class="el-icon--right">
                <arrow-down />
              </el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu class="create-dropdown">
                <el-dropdown-item @click="openCreateDialog(CreateKnowledgeDialog)">
                  <div class="flex">
                    <el-avatar class="avatar-blue mt-4" shape="square" :size="32">
                      <img src="@/assets/knowledge/icon_document.svg" style="width: 58%" alt="" />
                    </el-avatar>
                    <div class="pre-wrap ml-8">
                      <div class="lighter">
                        {{ $t('views.knowledge.knowledgeType.generalKnowledge') }}
                      </div>
                      <el-text type="info" size="small"
                        >{{ $t('views.knowledge.knowledgeType.generalInfo') }}
                      </el-text>
                    </div>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item @click="openCreateDialog(CreateWebKnowledgeDialog)">
                  <div class="flex">
                    <el-avatar class="avatar-purple mt-4" shape="square" :size="32">
                      <img src="@/assets/knowledge/icon_web.svg" style="width: 58%" alt="" />
                    </el-avatar>
                    <div class="pre-wrap ml-8">
                      <div class="lighter">
                        {{ $t('views.knowledge.knowledgeType.webKnowledge') }}
                      </div>
                      <el-text type="info" size="small"
                        >{{ $t('views.knowledge.knowledgeType.webInfo') }}
                      </el-text>
                    </div>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item @click="openCreateDialog(CreateLarkKnowledgeDialog)">
                  <div class="flex">
                    <el-avatar
                      class="avatar-purple mt-4"
                      shape="square"
                      :size="32"
                      style="background: none"
                    >
                      <img src="@/assets/knowledge/logo_lark.svg" alt="" />
                    </el-avatar>
                    <div class="pre-wrap ml-8">
                      <div class="lighter">
                        {{ $t('views.knowledge.knowledgeType.larkKnowledge') }}
                      </div>
                      <el-text type="info" size="small"
                        >{{ $t('views.knowledge.knowledgeType.larkInfo') }}
                      </el-text>
                    </div>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item>
                  <div class="flex">
                    <el-avatar
                      class="avatar-purple mt-4"
                      shape="square"
                      :size="32"
                      style="background: none"
                    >
                      <img src="@/assets/knowledge/logo_yuque.svg" alt="" />
                    </el-avatar>
                    <div class="pre-wrap ml-8">
                      <div class="lighter">
                        {{ $t('views.knowledge.knowledgeType.yuqueKnowledge') }}
                      </div>
                      <el-text type="info" size="small"
                        >{{ $t('views.knowledge.knowledgeType.yuqueInfo') }}
                      </el-text>
                    </div>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item @click="openCreateFolder" divided>
                  <div class="flex align-center">
                    <AppIcon iconName="app-folder" style="font-size: 32px"></AppIcon>
                    <div class="pre-wrap ml-4">
                      <div class="lighter">
                        {{ $t('components.folder.addFolder') }}
                      </div>
                    </div>
                  </div>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </template>
      <div v-loading.fullscreen.lock="paginationConfig.current_page === 1 && loading">
        <InfiniteScroll
          :size="knowledgeList.length"
          :total="paginationConfig.total"
          :page_size="paginationConfig.page_size"
          v-model:current_page="paginationConfig.current_page"
          @load="getList"
          :loading="loading"
        >
          <el-row v-if="knowledgeList.length > 0" :gutter="15">
            <template v-for="(item, index) in knowledgeList" :key="index">
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
                  @click="clickFolder(item)"
                >
                  <template #icon>
                    <el-avatar shape="square" :size="32" style="background: none">
                      <AppIcon iconName="app-folder" style="font-size: 32px"></AppIcon>
                    </el-avatar>
                  </template>
                  <template #subTitle>
                    <el-text class="color-secondary lighter" size="small">
                      {{ $t('common.creator') }}: {{ item.nick_name }}
                    </el-text>
                  </template>
                </CardBox>
              </el-col>
              <el-col v-else :xs="24" :sm="12" :md="12" :lg="8" :xl="6" class="mb-16">
                <CardBox
                  :title="item.name"
                  :description="item.desc"
                  :isShared="currentFolder.id === 'share'"
                  class="cursor"
                  @click="
                    router.push({ path: `/knowledge/${item.id}/${currentFolder.id}/document` })
                  "
                >
                  <template #icon>
                    <KnowledgeIcon :type="item.type" />
                  </template>
                  <template #subTitle>
                    <el-text class="color-secondary" size="small">
                      {{ $t('common.creator') }}: {{ item.nick_name }}
                    </el-text>
                  </template>

                  <template #footer>
                    <div class="footer-content flex-between">
                      <div>
                        <span class="bold mr-4">{{ item?.document_count || 0 }}</span>
                        <span class="color-secondary">{{
                          $t('views.knowledge.document_count')
                        }}</span>
                        <el-divider direction="vertical" />
                        <span class="bold mr-4">{{ numberFormat(item?.char_length) || 0 }}</span>
                        <span class="color-secondary">{{ $t('common.character') }}</span>
                        <el-divider direction="vertical" />
                        <span class="bold mr-4">{{ item?.application_mapping_count || 0 }}</span>
                        <span class="color-secondary">{{
                          $t('views.knowledge.relatedApp_count')
                        }}</span>
                      </div>
                    </div>
                  </template>
                  <template #mouseEnter>
                    <div @click.stop>
                      <el-dropdown trigger="click">
                        <el-button text @click.stop>
                          <el-icon>
                            <MoreFilled />
                          </el-icon>
                        </el-button>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item
                              icon="Refresh"
                              @click.stop="syncKnowledge(item)"
                              v-if="
                                item.type === 1 ||
                                hasPermission(
                                  [
                                    RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                                    PermissionConst.KNOWLEDGE_SYNC.getWorkspacePermission,
                                  ],
                                  'OR',
                                )
                              "
                              >{{ $t('views.knowledge.setting.sync') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              @click.stop="reEmbeddingKnowledge(item)"
                              v-if="
                                hasPermission(
                                  [
                                    RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                                    PermissionConst.KNOWLEDGE_VECTOR.getWorkspacePermission,
                                  ],
                                  'OR',
                                )
                              "
                            >
                              <AppIcon iconName="app-vectorization"></AppIcon>
                              {{ $t('views.knowledge.setting.vectorization') }}
                            </el-dropdown-item>

                            <el-dropdown-item
                              icon="Connection"
                              @click.stop="openGenerateDialog(item)"
                              v-if="
                                hasPermission(
                                  [
                                    RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                                    PermissionConst.KNOWLEDGE_PROBLEM_CREATE.getWorkspacePermission,
                                  ],
                                  'OR',
                                )
                              "
                              >{{ $t('views.document.generateQuestion.title') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              icon="Setting"
                              @click.stop="
                                router.push({
                                  path: `/knowledge/${item.id}/${currentFolder.value}/setting`,
                                })
                              "
                              v-if="
                                hasPermission(
                                  [
                                    RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                                    PermissionConst.KNOWLEDGE_EDIT.getWorkspacePermission,
                                  ],
                                  'OR',
                                )
                              "
                            >
                              {{ $t('common.setting') }}
                            </el-dropdown-item>
                            <el-dropdown-item
                              @click.stop="exportKnowledge(item)"
                              v-if="
                                hasPermission(
                                  [
                                    RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                                    PermissionConst.KNOWLEDGE_EXPORT.getWorkspacePermission,
                                  ],
                                  'OR',
                                )
                              "
                            >
                              <AppIcon iconName="app-export"></AppIcon
                              >{{ $t('views.document.setting.export') }} Excel
                            </el-dropdown-item>
                            <el-dropdown-item
                              @click.stop="exportZipKnowledge(item)"
                              v-if="
                                hasPermission(
                                  [
                                    RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                                    PermissionConst.KNOWLEDGE_EXPORT.getWorkspacePermission,
                                  ],
                                  'OR',
                                )
                              "
                            >
                              <AppIcon iconName="app-export"></AppIcon
                              >{{ $t('views.document.setting.export') }} ZIP</el-dropdown-item
                            >
                            <el-dropdown-item
                              icon="Delete"
                              @click.stop="deleteKnowledge(item)"
                              v-if="
                                hasPermission(
                                  [
                                    RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                                    PermissionConst.KNOWLEDGE_EXPORT.getWorkspacePermission,
                                  ],
                                  'OR',
                                )
                              "
                            >
                              {{ $t('common.delete') }}</el-dropdown-item
                            >
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
        </InfiniteScroll>
      </div>
    </ContentContainer>

    <component :is="currentCreateDialog" ref="CreateKnowledgeDialogRef" />
    <CreateFolderDialog ref="CreateFolderDialogRef" @refresh="refreshFolder" />
    <GenerateRelatedDialog ref="GenerateRelatedDialogRef" />
    <SyncWebDialog ref="SyncWebDialogRef" />
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, shallowRef, nextTick } from 'vue'
import CreateKnowledgeDialog from './create-component/CreateKnowledgeDialog.vue'
import CreateWebKnowledgeDialog from './create-component/CreateWebKnowledgeDialog.vue'
import CreateLarkKnowledgeDialog from './create-component/CreateLarkKnowledgeDialog.vue'
import SyncWebDialog from './component/SyncWebDialog.vue'
import CreateFolderDialog from '@/components/folder-tree/CreateFolderDialog.vue'
import GenerateRelatedDialog from '@/components/generate-related-dialog/index.vue'
import KnowledgeApi from '@/api/knowledge/knowledge'
import SharedWorkspace from '@/views/shared/knowledge-shared/SharedWorkspace.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import useStore from '@/stores'
import { numberFormat } from '@/utils/common'
import { t } from '@/locales'
import { useRouter } from 'vue-router'
import { FolderSource } from '@/enums/common'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'

const router = useRouter()
const { folder, user } = useStore()

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

const folderList = ref<any[]>([])
const knowledgeList = ref<any[]>([])
const currentFolder = ref<any>({})

const CreateKnowledgeDialogRef = ref()
const currentCreateDialog = shallowRef<any>(null)

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
  const params = {
    folder_id: currentFolder.value?.id || user.getWorkspaceId(),
    [search_type.value]: search_form.value[search_type.value],
  }

  KnowledgeApi.getKnowledgeListPage(paginationConfig, params, loading).then((res) => {
    paginationConfig.total = res.data.total
    knowledgeList.value = [...knowledgeList.value, ...res.data.records]
  })
}

function getFolder() {
  const params = {}
  folder.asyncGetFolder(FolderSource.KNOWLEDGE, params, loading).then((res: any) => {
    folderList.value = res.data
    currentFolder.value = res.data?.[0] || {}
    getList()
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
  CreateFolderDialogRef.value.open(FolderSource.KNOWLEDGE, currentFolder.value.parent_id)
}

const GenerateRelatedDialogRef = ref<InstanceType<typeof GenerateRelatedDialog>>()
function openGenerateDialog(row: any) {
  if (GenerateRelatedDialogRef.value) {
    GenerateRelatedDialogRef.value.open([], 'knowledge', row.id)
  }
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
  getFolder()
  getList()
}

onMounted(() => {
  getFolder()
})
</script>

<style lang="scss" scoped></style>
