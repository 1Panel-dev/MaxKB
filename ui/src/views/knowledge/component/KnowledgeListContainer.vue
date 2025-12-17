<template>
  <ContentContainer>
    <template #header>
      <slot name="header"> </slot>
    </template>
    <template #search>
      <div class="flex">
        <div class="complex-search">
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
            @change="searchHandle"
            :placeholder="$t('common.searchBar.placeholder')"
            style="width: 220px"
            clearable
          />
          <el-select
            v-else-if="search_type === 'create_user'"
            v-model="search_form.create_user"
            @change="searchHandle"
            filterable
            clearable
            style="width: 220px"
          >
            <el-option v-for="u in user_options" :key="u.id" :value="u.id" :label="u.nick_name" />
          </el-select>
        </div>
        <el-dropdown trigger="click" v-if="!isShared && permissionPrecise.create()">
          <el-button type="primary" class="ml-8">
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
              <el-dropdown-item
                @click="openCreateDialog(CreateLarkKnowledgeDialog)"
                v-if="user.isPE() || user.isEE()"
              >
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
              <el-dropdown-item @click="openCreateDialog(CreateWorkflowKnowledgeDialog)">
                <div class="flex">
                  <el-avatar class="avatar-orange mt-4" shape="square" :size="32">
                    <img src="@/assets/knowledge/logo_workflow.svg" style="width: 60%" alt="" />
                  </el-avatar>
                  <div class="pre-wrap ml-8">
                    <div class="lighter">
                      {{ $t('views.knowledge.knowledgeType.workflowKnowledge') }}
                    </div>
                    <el-text type="info" size="small"
                      >{{ $t('views.knowledge.knowledgeType.workflowInfo') }}
                    </el-text>
                  </div>
                </div>
              </el-dropdown-item>
              <el-dropdown-item @click="openCreateFolder" divided v-if="apiType === 'workspace'">
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

    <div
      v-loading.fullscreen.lock="paginationConfig.current_page === 1 && loading"
      style="max-height: calc(100vh - 120px)"
    >
      <InfiniteScroll
        :size="knowledge.knowledgeList.length"
        :total="paginationConfig.total"
        :page_size="paginationConfig.page_size"
        v-model:current_page="paginationConfig.current_page"
        @load="getList"
        :loading="loading"
      >
        <el-row v-if="knowledge.knowledgeList.length > 0" :gutter="15" class="w-full">
          <template v-for="(item, index) in knowledge.knowledgeList" :key="index">
            <el-col :xs="24" :sm="12" :md="12" :lg="8" :xl="6" class="mb-16">
              <CardBox
                :title="item.name"
                :description="item.desc"
                class="cursor"
                @click="
                  router.push({
                    path: `/knowledge/${item.id}/${folder.currentFolder.id ? (folder.currentFolder.id !== 'share' ? item.folder_id : 'share') : 'shared'}/${item.type}/document`,
                  })
                "
              >
                <template #icon>
                  <KnowledgeIcon :type="item.type" />
                </template>
                <template #subTitle>
                  <el-text class="color-secondary lighter" size="small">
                    {{ $t('common.creator') }}: {{ i18n_name(item.nick_name) }}
                  </el-text>
                </template>
                <template #tag>
                  <el-tag v-if="isShared || isSystemShare" type="info" class="info-tag">
                    {{ t('views.shared.title') }}
                  </el-tag>
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
                    </div>
                  </div>
                </template>
                <template #mouseEnter>
                  <div @click.stop v-if="!isShared">
                    <el-dropdown trigger="click">
                      <el-button text @click.stop v-if="MoreFilledPermission(item)">
                        <AppIcon iconName="app-more"></AppIcon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item
                            @click.stop="syncKnowledge(item)"
                            v-if="item.type === 1 && permissionPrecise.sync(item.id)"
                          >
                            <AppIcon iconName="app-sync" class="color-secondary"></AppIcon>

                            {{ $t('views.knowledge.setting.sync') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            @click.stop="reEmbeddingKnowledge(item)"
                            v-if="permissionPrecise.vector(item.id)"
                          >
                            <AppIcon iconName="app-vectorization" class="color-secondary"></AppIcon>
                            {{ $t('views.knowledge.setting.vectorization') }}
                          </el-dropdown-item>

                          <el-dropdown-item
                            @click.stop="openGenerateDialog(item)"
                            v-if="permissionPrecise.generate(item.id)"
                          >
                            <AppIcon
                              iconName="app-generate-question"
                              class="color-secondary"
                            ></AppIcon>

                            {{ $t('views.document.generateQuestion.title') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            v-if="isSystemShare"
                            @click.stop="openAuthorizedWorkspaceDialog(item)"
                          >
                            <AppIcon iconName="app-lock" class="color-secondary"></AppIcon>
                            {{ $t('views.shared.authorized_workspace') }}</el-dropdown-item
                          >
                          <el-dropdown-item
                            @click.stop="openAuthorization(item)"
                            v-if="apiType === 'workspace' && permissionPrecise.auth(item.id)"
                          >
                            <AppIcon
                              iconName="app-resource-authorization"
                              class="color-secondary"
                            ></AppIcon>
                            {{ $t('views.system.resourceAuthorization.title') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            @click.stop="openMoveToDialog(item)"
                            v-if="permissionPrecise.edit(item.id) && apiType === 'workspace'"
                          >
                            <AppIcon iconName="app-migrate" class="color-secondary"></AppIcon>
                            {{ $t('common.moveTo') }}
                          </el-dropdown-item>

                          <el-dropdown-item
                            @click.stop="
                              router.push({
                                path: `/knowledge/${item.id}/${folder.currentFolder.id || 'shared'}/${item.type}/setting`,
                              })
                            "
                            v-if="permissionPrecise.edit(item.id)"
                          >
                            <AppIcon iconName="app-setting" class="color-secondary"></AppIcon>
                            {{ $t('common.setting') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            @click.stop="exportKnowledge(item)"
                            v-if="permissionPrecise.export(item.id)"
                          >
                            <AppIcon iconName="app-export" class="color-secondary"></AppIcon
                            >{{ $t('views.document.setting.export') }} Excel
                          </el-dropdown-item>
                          <el-dropdown-item
                            @click.stop="exportZipKnowledge(item)"
                            v-if="permissionPrecise.export(item.id)"
                          >
                            <AppIcon iconName="app-export" class="color-secondary"></AppIcon
                            >{{ $t('views.document.setting.export') }} ZIP</el-dropdown-item
                          >
                          <el-dropdown-item
                            type="danger"
                            @click.stop="deleteKnowledge(item)"
                            v-if="permissionPrecise.delete(item.id)"
                          >
                            <AppIcon iconName="app-delete" class="color-secondary"></AppIcon>
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

  <component :is="currentCreateDialog" ref="CreateKnowledgeDialogRef" v-if="!isShared" />
  <CreateFolderDialog ref="CreateFolderDialogRef" v-if="!isShared" @refresh="refreshFolder" />
  <GenerateRelatedDialog ref="GenerateRelatedDialogRef" :apiType="apiType" />
  <SyncWebDialog ref="SyncWebDialogRef" v-if="!isShared" />
  <AuthorizedWorkspace
    ref="AuthorizedWorkspaceDialogRef"
    v-if="isSystemShare"
  ></AuthorizedWorkspace>
  <MoveToDialog
    ref="MoveToDialogRef"
    :source="SourceTypeEnum.KNOWLEDGE"
    @refresh="refreshKnowledgeList"
    v-if="apiType === 'workspace'"
  />
  <ResourceAuthorizationDrawer
    :type="SourceTypeEnum.KNOWLEDGE"
    ref="ResourceAuthorizationDrawerRef"
    v-if="apiType === 'workspace'"
  />
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, shallowRef, nextTick, computed, watch } from 'vue'
import { useRouter, useRoute, onBeforeRouteLeave } from 'vue-router'
import { cloneDeep, get } from 'lodash'
import CreateKnowledgeDialog from '@/views/knowledge/create-component/CreateKnowledgeDialog.vue'
import CreateWebKnowledgeDialog from '@/views/knowledge/create-component/CreateWebKnowledgeDialog.vue'
import CreateLarkKnowledgeDialog from '@/views/knowledge/create-component/CreateLarkKnowledgeDialog.vue'
import CreateWorkflowKnowledgeDialog from '@/views/knowledge/create-component/CreateWorkflowKnowledgeDialog.vue'
import SyncWebDialog from '@/views/knowledge/component/SyncWebDialog.vue'
import CreateFolderDialog from '@/components/folder-tree/CreateFolderDialog.vue'
import MoveToDialog from '@/components/folder-tree/MoveToDialog.vue'
import GenerateRelatedDialog from '@/components/generate-related-dialog/index.vue'
import AuthorizedWorkspace from '@/views/system-shared/AuthorizedWorkspaceDialog.vue'
import ResourceAuthorizationDrawer from '@/components/resource-authorization-drawer/index.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import useStore from '@/stores'
import { numberFormat } from '@/utils/common'
import { t } from '@/locales'
import { i18n_name } from '@/utils/common'
import { SourceTypeEnum } from '@/enums/common'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import permissionMap from '@/permission'
const router = useRouter()
const route = useRoute()
const { folder, user, knowledge } = useStore()
onBeforeRouteLeave((to, from) => {
  knowledge.setKnowledgeList([])
})

const emit = defineEmits(['refreshFolder'])

const apiType = computed(() => {
  // 工作空间普通用户的共享是share。系统的共享是shared
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const permissionPrecise = computed(() => {
  return permissionMap['knowledge'][apiType.value]
})

const isShared = computed(() => {
  return folder.currentFolder.id === 'share'
})
const isSystemShare = computed(() => {
  return apiType.value === 'systemShare'
})

const MoreFilledPermission = (item: any) => {
  return (
    (item.type === 1 && permissionPrecise.value.sync(item.id)) ||
    permissionPrecise.value.vector(item.id) ||
    permissionPrecise.value.generate(item.id) ||
    (permissionPrecise.value.edit(item.id) && apiType.value) === 'workspace' ||
    permissionPrecise.value.export(item.id) ||
    permissionPrecise.value.auth(item.id) ||
    permissionPrecise.value.delete(item.id) ||
    isSystemShare.value
  )
}

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

const ResourceAuthorizationDrawerRef = ref()
function openAuthorization(item: any) {
  ResourceAuthorizationDrawerRef.value.open(item.id)
}

const MoveToDialogRef = ref()
function openMoveToDialog(data: any) {
  // 仅2个参数就行
  const obj = {
    id: data.id,
    folder_id: data.folder,
  }
  MoveToDialogRef.value?.open(obj)
}

function refreshKnowledgeList(row: any) {
  // 不是根目录才会移除
  if (folder.currentFolder?.parent_id) {
    const list = cloneDeep(knowledge.knowledgeList)
    const index = list.findIndex((v) => v.id === row.id)
    list.splice(index, 1)
    knowledge.setKnowledgeList(list)
  }
}

const CreateKnowledgeDialogRef = ref()
const currentCreateDialog = shallowRef<any>(null)

function openCreateDialog(data: any) {
  currentCreateDialog.value = data
  nextTick(() => {
    CreateKnowledgeDialogRef.value.open(folder.currentFolder)
  })
}

function reEmbeddingKnowledge(row: any) {
  loadSharedApi({ type: 'knowledge', systemType: apiType.value })
    .putReEmbeddingKnowledge(row.id)
    .then(() => {
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

const GenerateRelatedDialogRef = ref<InstanceType<typeof GenerateRelatedDialog>>()
function openGenerateDialog(row: any) {
  if (GenerateRelatedDialogRef.value) {
    GenerateRelatedDialogRef.value.open([], 'knowledge', row)
  }
}

const exportKnowledge = (item: any) => {
  loadSharedApi({ type: 'knowledge', systemType: apiType.value })
    .exportKnowledge(item.name, item.id, loading)
    .then(() => {
      MsgSuccess(t('common.exportSuccess'))
    })
}
const exportZipKnowledge = (item: any) => {
  loadSharedApi({ type: 'knowledge', systemType: apiType.value })
    .exportZipKnowledge(item.name, item.id, loading)
    .then(() => {
      MsgSuccess(t('common.exportSuccess'))
    })
}

function deleteKnowledge(row: any) {
  MsgConfirm(
    `${t('views.knowledge.delete.confirmTitle')}${row.name} ?`,
    `${t('views.knowledge.delete.confirmMessage1')} ${row.application_mapping_count} ${t('views.knowledge.delete.confirmMessage2')}`,
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      loadSharedApi({ type: 'knowledge', systemType: apiType.value })
        .delKnowledge(row.id, loading)
        .then(() => {
          const list = cloneDeep(knowledge.knowledgeList)
          const index = list.findIndex((v) => v.id === row.id)
          list.splice(index, 1)
          knowledge.setKnowledgeList(list)

          MsgSuccess(t('common.deleteSuccess'))
        })
    })
    .catch(() => {})
}

const AuthorizedWorkspaceDialogRef = ref()
function openAuthorizedWorkspaceDialog(row: any) {
  if (AuthorizedWorkspaceDialogRef.value) {
    AuthorizedWorkspaceDialogRef.value.open(row)
  }
}

// 文件夹相关
const CreateFolderDialogRef = ref()
function openCreateFolder() {
  CreateFolderDialogRef.value.open(SourceTypeEnum.KNOWLEDGE, folder.currentFolder.id)
}
watch(
  () => folder.currentFolder,
  (newValue) => {
    if (newValue && newValue.id && !isSystemShare.value) {
      paginationConfig.current_page = 1
      knowledge.setKnowledgeList([])
      getList()
    }
  },
  { deep: true, immediate: true },
)

function getList() {
  const params: any = {
    folder_id: folder.currentFolder?.id || user.getWorkspaceId(),
    scope: apiType.value === 'systemShare' ? 'SHARED' : 'WORKSPACE',
  }
  if (search_form.value[search_type.value]) {
    params[search_type.value] = search_form.value[search_type.value]
  }
  loadSharedApi({ type: 'knowledge', isShared: isShared.value, systemType: apiType.value })
    .getKnowledgeListPage(paginationConfig, params, loading)
    .then((res: any) => {
      paginationConfig.total = res.data?.total
      knowledge.setKnowledgeList([...knowledge.knowledgeList, ...res.data.records])
    })
}

function clickFolder(item: any) {
  folder.setCurrentFolder(item)
}

function searchHandle() {
  paginationConfig.current_page = 1
  knowledge.setKnowledgeList([])
  getList()
}

function refreshFolder() {
  emit('refreshFolder')
}

onMounted(() => {
  if (apiType.value !== 'workspace') {
    folder.setCurrentFolder({
      id: '',
    })
    getList()
  }
  loadSharedApi({ type: 'workspace', isShared: isShared.value, systemType: apiType.value })
    .getAllMemberList(user.getWorkspaceId(), loading)
    .then((res: any) => {
      user_options.value = res.data
    })
})
</script>

<style lang="scss" scoped></style>
