<template>
  <div class="document p-16-24">
    <h2 class="mb-16">{{ $t('common.fileUpload.document') }}</h2>
    <el-card style="--el-card-padding: 0">
      <div class="main-calc-height">
        <div class="p-24">
          <div class="flex-between">
            <div>
              <el-button
                v-if="knowledgeDetail.type === 0"
                type="primary"
                @click="
                  router.push({ path: `/knowledge/document/upload/${folderId}`, query: { id: id } })
                "
                v-hasPermission="[
                  RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                  PermissionConst.KNOWLEDGE_DOCUMENT_CREATE.getWorkspacePermission,
                ]"
                >{{ $t('views.document.uploadDocument') }}
              </el-button>
              <el-button
                v-if="knowledgeDetail.type === 1"
                type="primary"
                @click="importDoc"
                v-hasPermission="[
                  RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                  PermissionConst.KNOWLEDGE_DOCUMENT_CREATE.getWorkspacePermission,
                ]"
                >{{ $t('views.document.importDocument') }}
              </el-button>
              <el-button
                v-if="knowledgeDetail.type === 2"
                type="primary"
                @click="
                  router.push({
                    path: `/knowledge/import`,
                    query: { id: id, folder_token: knowledgeDetail.meta.folder_token },
                  })
                "
                >{{ $t('views.document.importDocument') }}
              </el-button>
              <el-button
                @click="batchRefresh"
                :disabled="multipleSelection.length === 0"
                v-hasPermission="[
                  RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                  PermissionConst.KNOWLEDGE_DOCUMENT_VECTOR.getWorkspacePermission,
                ]"
                >{{ $t('views.knowledge.setting.vectorization') }}
              </el-button>
              <el-button
                @click="openGenerateDialog()"
                :disabled="multipleSelection.length === 0"
                v-hasPermission="[
                  RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                  PermissionConst.KNOWLEDGE_DOCUMENT_GENERATE.getWorkspacePermission,
                ]"
                >{{ $t('views.document.generateQuestion.title') }}
              </el-button>
              <el-button
                @click="openknowledgeDialog()"
                :disabled="multipleSelection.length === 0"
                v-hasPermission="[
                  RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                  PermissionConst.KNOWLEDGE_DOCUMENT_MIGRATE.getWorkspacePermission,
                ]"
                >{{ $t('views.document.setting.migration') }}
              </el-button>
              <el-dropdown>
                <el-button
                  class="ml-12 mr-12"
                  v-hasPermission="[
                    RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                    PermissionConst.KNOWLEDGE_DOCUMENT_EDIT.getWorkspacePermission,
                  ]"
                >
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item
                      @click="openBatchEditDocument"
                      :disabled="multipleSelection.length === 0"
                    >
                      {{ $t('common.setting') }}
                    </el-dropdown-item>
                    <el-dropdown-item
                      divided
                      @click="syncMulDocument"
                      :disabled="multipleSelection.length === 0"
                      v-if="knowledgeDetail.type === 1"
                      >{{ $t('views.document.syncDocument') }}
                    </el-dropdown-item>
                    <el-dropdown-item
                      divided
                      @click="syncLarkMulDocument"
                      :disabled="multipleSelection.length === 0"
                      v-if="knowledgeDetail.type === 2"
                      >{{ $t('views.document.syncDocument') }}
                    </el-dropdown-item>

                    <el-dropdown-item
                      divided
                      @click="deleteMulDocument"
                      :disabled="multipleSelection.length === 0"
                      >{{ $t('common.delete') }}
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>

            <el-input
              v-model="filterText"
              :placeholder="$t('common.searchBar.placeholder')"
              prefix-icon="Search"
              class="w-240"
              @change="getList"
              clearable
            />
          </div>
          <app-table
            ref="multipleTableRef"
            class="mt-16"
            :data="documentData"
            :pagination-config="paginationConfig"
            :quick-create="knowledgeDetail.type === 0"
            @sizeChange="handleSizeChange"
            @changePage="getList"
            @cell-mouse-enter="cellMouseEnter"
            @cell-mouse-leave="cellMouseLeave"
            @creatQuick="creatQuickHandle"
            @row-click="rowClickHandle"
            @selection-change="handleSelectionChange"
            @sort-change="handleSortChange"
            v-loading="loading"
            :row-key="(row: any) => row.id"
            :storeKey="storeKey"
          >
            <el-table-column type="selection" width="55" :reserve-selection="true" />
            <el-table-column prop="name" :label="$t('views.document.table.name')" min-width="280">
              <template #default="{ row }">
                <ReadWrite
                  @change="editName($event, row.id)"
                  :data="row.name"
                  :showEditIcon="row.id === currentMouseId"
                />
              </template>
            </el-table-column>
            <el-table-column
              prop="status"
              :label="$t('views.document.fileStatus.label')"
              width="130"
            >
              <template #header>
                <div>
                  <span>{{ $t('views.document.fileStatus.label') }}</span>
                  <el-dropdown trigger="click" @command="dropdownHandle">
                    <el-button
                      style="margin-top: 1px"
                      link
                      :type="filterMethod['status'] ? 'primary' : ''"
                    >
                      <el-icon>
                        <Filter />
                      </el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu style="width: 100px">
                        <el-dropdown-item
                          :class="filterMethod['status'] ? '' : 'is-active'"
                          :command="beforeCommand('status', '')"
                          class="justify-center"
                          >{{ $t('views.document.table.all') }}
                        </el-dropdown-item>
                        <el-dropdown-item
                          :class="filterMethod['status'] === State.SUCCESS ? 'is-active' : ''"
                          class="justify-center"
                          :command="beforeCommand('status', State.SUCCESS)"
                          >{{ $t('views.document.fileStatus.SUCCESS') }}
                        </el-dropdown-item>
                        <el-dropdown-item
                          :class="filterMethod['status'] === State.FAILURE ? 'is-active' : ''"
                          class="justify-center"
                          :command="beforeCommand('status', State.FAILURE)"
                          >{{ $t('views.document.fileStatus.FAILURE') }}
                        </el-dropdown-item>
                        <el-dropdown-item
                          :class="
                            filterMethod['status'] === State.STARTED &&
                            filterMethod['task_type'] == TaskType.EMBEDDING
                              ? 'is-active'
                              : ''
                          "
                          class="justify-center"
                          :command="beforeCommand('status', State.STARTED, TaskType.EMBEDDING)"
                          >{{ $t('views.document.fileStatus.EMBEDDING') }}
                        </el-dropdown-item>
                        <el-dropdown-item
                          :class="filterMethod['status'] === State.PENDING ? 'is-active' : ''"
                          class="justify-center"
                          :command="beforeCommand('status', State.PENDING)"
                          >{{ $t('views.document.fileStatus.PENDING') }}
                        </el-dropdown-item>
                        <el-dropdown-item
                          :class="
                            filterMethod['status'] === State.STARTED &&
                            filterMethod['task_type'] === TaskType.GENERATE_PROBLEM
                              ? 'is-active'
                              : ''
                          "
                          class="justify-center"
                          :command="
                            beforeCommand('status', State.STARTED, TaskType.GENERATE_PROBLEM)
                          "
                          >{{ $t('views.document.fileStatus.GENERATE') }}
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </template>
              <template #default="{ row }">
                <StatusValue :status="row.status" :status-meta="row.status_meta"></StatusValue>
              </template>
            </el-table-column>
            <el-table-column
              prop="char_length"
              :label="$t('views.document.table.char_length')"
              align="right"
              min-width="90"
              sortable
            >
              <template #default="{ row }">
                {{ numberFormat(row.char_length) }}
              </template>
            </el-table-column>
            <el-table-column
              prop="paragraph_count"
              :label="$t('views.document.table.paragraph')"
              align="right"
              min-width="90"
              sortable
            />

            <el-table-column width="130">
              <template #header>
                <div>
                  <span>{{ $t('views.document.enableStatus.label') }}</span>
                  <el-dropdown trigger="click" @command="dropdownHandle">
                    <el-button
                      style="margin-top: 1px"
                      link
                      :type="filterMethod['is_active'] ? 'primary' : ''"
                    >
                      <el-icon>
                        <Filter />
                      </el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu style="width: 100px">
                        <el-dropdown-item
                          :class="filterMethod['is_active'] === '' ? 'is-active' : ''"
                          :command="beforeCommand('is_active', '')"
                          class="justify-center"
                          >{{ $t('views.document.table.all') }}
                        </el-dropdown-item>
                        <el-dropdown-item
                          :class="filterMethod['is_active'] === true ? 'is-active' : ''"
                          class="justify-center"
                          :command="beforeCommand('is_active', true)"
                          >{{ $t('views.document.enableStatus.enable') }}
                        </el-dropdown-item>
                        <el-dropdown-item
                          :class="filterMethod['is_active'] === false ? 'is-active' : ''"
                          class="justify-center"
                          :command="beforeCommand('is_active', false)"
                          >{{ $t('views.document.enableStatus.close') }}
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </template>
              <template #default="{ row }">
                <div v-if="row.is_active" class="flex align-center">
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
            </el-table-column>
            <el-table-column width="170">
              <template #header>
                <div>
                  <span>{{ $t('views.document.form.hit_handling_method.label') }}</span>
                  <el-dropdown trigger="click" @command="dropdownHandle">
                    <el-button
                      style="margin-top: 1px"
                      link
                      :type="filterMethod['hit_handling_method'] ? 'primary' : ''"
                    >
                      <el-icon>
                        <Filter />
                      </el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu style="width: 150px">
                        <el-dropdown-item
                          :class="filterMethod['hit_handling_method'] ? '' : 'is-active'"
                          :command="beforeCommand('hit_handling_method', '')"
                          class="justify-center"
                          >{{ $t('views.document.table.all') }}
                        </el-dropdown-item>
                        <template v-for="(value, key) of hitHandlingMethod" :key="key">
                          <el-dropdown-item
                            :class="filterMethod['hit_handling_method'] === key ? 'is-active' : ''"
                            class="justify-center"
                            :command="beforeCommand('hit_handling_method', key)"
                            >{{ $t(value) }}
                          </el-dropdown-item>
                        </template>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </template>
              <template #default="{ row }">
                {{
                  $t(hitHandlingMethod[row.hit_handling_method as keyof typeof hitHandlingMethod])
                }}
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
            <el-table-column :label="$t('common.operation')" align="left" width="160" fixed="right">
              <template #default="{ row }">
                <span @click.stop>
                  <el-switch
                    :loading="loading"
                    size="small"
                    v-model="row.is_active"
                    :before-change="() => changeState(row)"
                  />
                </span>
                <el-divider direction="vertical" />
                <template v-if="knowledgeDetail.type === 0">
                  <span
                    class="mr-4"
                    v-if="
                      ([State.STARTED, State.PENDING] as Array<string>).includes(
                        getTaskState(row.status, TaskType.EMBEDDING),
                      )
                    "
                  >
                    <el-button
                      type="primary"
                      text
                      @click.stop="cancelTask(row, TaskType.EMBEDDING)"
                      :title="$t('views.document.setting.cancelVectorization')"
                      v-hasPermission="[
                        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                        PermissionConst.KNOWLEDGE_DOCUMENT_VECTOR.getWorkspacePermission,
                      ]"
                    >
                      <AppIcon iconName="app-close" style="font-size: 16px"></AppIcon>
                    </el-button>
                  </span>
                  <span class="mr-4" v-else>
                    <el-button
                      type="primary"
                      text
                      @click.stop="refreshDocument(row)"
                      :title="$t('views.knowledge.setting.vectorization')"
                      v-hasPermission="[
                        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                        PermissionConst.KNOWLEDGE_DOCUMENT_VECTOR.getWorkspacePermission,
                      ]"
                    >
                      <AppIcon iconName="app-document-refresh" style="font-size: 16px"></AppIcon>
                    </el-button>
                  </span>
                  <span class="mr-4">
                    <el-button
                      type="primary"
                      text
                      @click.stop="settingDoc(row)"
                      :title="$t('common.setting')"
                      v-hasPermission="[
                        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                        PermissionConst.KNOWLEDGE_DOCUMENT_EDIT.getWorkspacePermission,
                      ]"
                    >
                      <el-icon><Setting /></el-icon>
                    </el-button>
                  </span>
                  <span @click.stop>
                    <el-dropdown trigger="click">
                      <el-button
                        text
                        type="primary"
                        v-hasPermission="[
                          RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                          PermissionConst.KNOWLEDGE_DOCUMENT_EDIT.getWorkspacePermission,
                        ]"
                      >
                        <el-icon><MoreFilled /></el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item
                            v-if="
                              ([State.STARTED, State.PENDING] as Array<string>).includes(
                                getTaskState(row.status, TaskType.GENERATE_PROBLEM),
                              )
                            "
                            @click="cancelTask(row, TaskType.GENERATE_PROBLEM)"
                          >
                            <el-icon><Connection /></el-icon>
                            {{ $t('views.document.setting.cancelGenerateQuestion') }}
                          </el-dropdown-item>
                          <el-dropdown-item v-else @click="openGenerateDialog(row)">
                            <el-icon><Connection /></el-icon>
                            {{ $t('views.document.generateQuestion.title') }}
                          </el-dropdown-item>
                          <el-dropdown-item @click="openknowledgeDialog(row)">
                            <AppIcon iconName="app-migrate"></AppIcon>
                            {{ $t('views.document.setting.migration') }}
                          </el-dropdown-item>
                          <el-dropdown-item @click="exportDocument(row)">
                            <AppIcon iconName="app-export"></AppIcon>
                            {{ $t('views.document.setting.export') }} Excel
                          </el-dropdown-item>
                          <el-dropdown-item @click="exportDocumentZip(row)">
                            <AppIcon iconName="app-export"></AppIcon>
                            {{ $t('views.document.setting.export') }} Zip
                          </el-dropdown-item>
                          <el-dropdown-item icon="Delete" @click.stop="deleteDocument(row)">
                            {{ $t('common.delete') }}</el-dropdown-item
                          >
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </span>
                </template>
                <template v-if="knowledgeDetail.type === 1 || knowledgeDetail.type === 2">
                  <span class="mr-4">
                    <el-button
                      type="primary"
                      text
                      @click.stop="syncDocument(row)"
                      :title="$t('views.knowledge.setting.sync')"
                      v-hasPermission="[
                        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                        PermissionConst.KNOWLEDGE_SYNC.getWorkspacePermission,
                      ]"
                    >
                      <el-icon><Refresh /></el-icon>
                    </el-button>
                  </span>
                  <span class="mr-4">
                    <el-button
                      v-if="
                        ([State.STARTED, State.PENDING] as Array<string>).includes(
                          getTaskState(row.status, TaskType.EMBEDDING),
                        )
                      "
                      type="primary"
                      text
                      @click.stop="cancelTask(row, TaskType.EMBEDDING)"
                      :title="$t('views.document.setting.cancelVectorization')"
                      v-hasPermission="[
                        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                        PermissionConst.KNOWLEDGE_DOCUMENT_VECTOR.getWorkspacePermission,
                      ]"
                    >
                      <AppIcon iconName="app-close" style="font-size: 16px"></AppIcon>
                    </el-button>

                    <el-button
                      v-else
                      type="primary"
                      text
                      @click.stop="refreshDocument(row)"
                      :title="$t('views.knowledge.setting.vectorization')"
                      v-hasPermission="[
                        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                        PermissionConst.KNOWLEDGE_DOCUMENT_VECTOR.getWorkspacePermission,
                      ]"
                    >
                      <AppIcon iconName="app-document-refresh" style="font-size: 16px"></AppIcon>
                    </el-button>
                  </span>

                  <span @click.stop>
                    <el-dropdown trigger="click">
                      <el-button
                        text
                        type="primary"
                        v-hasPermission="[
                          RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
                          PermissionConst.KNOWLEDGE_DOCUMENT_EDIT.getWorkspacePermission,
                        ]"
                      >
                        <el-icon><MoreFilled /></el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item icon="Setting" @click="settingDoc(row)">{{
                            $t('common.setting')
                          }}</el-dropdown-item>
                          <el-dropdown-item
                            v-if="
                              ([State.STARTED, State.PENDING] as Array<string>).includes(
                                getTaskState(row.status, TaskType.GENERATE_PROBLEM),
                              )
                            "
                            @click="cancelTask(row, TaskType.GENERATE_PROBLEM)"
                          >
                            <el-icon><Connection /></el-icon>
                            {{ $t('views.document.setting.cancelGenerateQuestion') }}
                          </el-dropdown-item>
                          <el-dropdown-item v-else @click="openGenerateDialog(row)">
                            <el-icon><Connection /></el-icon>
                            {{ $t('views.document.generateQuestion.title') }}
                          </el-dropdown-item>
                          <el-dropdown-item @click="openknowledgeDialog(row)">
                            <AppIcon iconName="app-migrate"></AppIcon>
                            {{ $t('views.document.setting.migration') }}
                          </el-dropdown-item>
                          <el-dropdown-item @click="exportDocument(row)">
                            <AppIcon iconName="app-export"></AppIcon>
                            {{ $t('views.document.setting.export') }} Excel
                          </el-dropdown-item>
                          <el-dropdown-item @click="exportDocumentZip(row)">
                            <AppIcon iconName="app-export"></AppIcon>
                            {{ $t('views.document.setting.export') }} Zip
                          </el-dropdown-item>
                          <el-dropdown-item icon="Delete" @click.stop="deleteDocument(row)">
                            {{ $t('common.delete') }}
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </span>
                </template>
              </template>
            </el-table-column>
          </app-table>
        </div>
      </div>
    </el-card>
    <div class="mul-operation w-full flex" v-if="multipleSelection.length !== 0">
      <el-button
        :disabled="multipleSelection.length === 0"
        @click="cancelTaskHandle(1)"
        v-hasPermission="[
          RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
          PermissionConst.KNOWLEDGE_DOCUMENT_VECTOR.getWorkspacePermission,
        ]"
      >
        {{ $t('views.document.setting.cancelVectorization') }}
      </el-button>
      <el-button
        :disabled="multipleSelection.length === 0"
        @click="cancelTaskHandle(2)"
        v-hasPermission="[
          RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
          PermissionConst.KNOWLEDGE_DOCUMENT_GENERATE.getWorkspacePermission,
        ]"
      >
        {{ $t('views.document.setting.cancelGenerate') }}
      </el-button>
      <el-text type="info" class="secondary ml-24">
        {{ $t('views.document.selected') }} {{ multipleSelection.length }}
        {{ $t('views.document.items') }}
      </el-text>
      <el-button class="ml-16" type="primary" link @click="clearSelection">
        {{ $t('common.clear') }}
      </el-button>
    </div>

    <EmbeddingContentDialog ref="embeddingContentDialogRef"></EmbeddingContentDialog>

    <ImportDocumentDialog ref="ImportDocumentDialogRef" :title="title" @refresh="refresh" />
    <SyncWebDialog ref="SyncWebDialogRef" @refresh="refresh" />
    <!-- 选择知识库 -->
    <SelectKnowledgeDialog ref="selectKnowledgeDialogRef" @refresh="refreshMigrate" />
    <GenerateRelatedDialog ref="GenerateRelatedDialogRef" @refresh="getList" />
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute, onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'
import { ElTable } from 'element-plus'
import documentApi from '@/api/knowledge/document'
import ImportDocumentDialog from './component/ImportDocumentDialog.vue'
import SyncWebDialog from '@/views/knowledge/component/SyncWebDialog.vue'
import SelectKnowledgeDialog from './component/SelectKnowledgeDialog.vue'
import { numberFormat } from '@/utils/common'
import { datetimeFormat } from '@/utils/time'
import { hitHandlingMethod } from '@/enums/document'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import useStore from '@/stores'
import StatusValue from '@/views/document/component/Status.vue'
import GenerateRelatedDialog from '@/components/generate-related-dialog/index.vue'
import EmbeddingContentDialog from '@/views/document/component/EmbeddingContentDialog.vue'
import { TaskType, State } from '@/utils/status'
import { t } from '@/locales'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'

const router = useRouter()
const route = useRoute()
const {
  params: { id, folderId }, // id为knowledgeID
} = route as any

const { common, knowledge, document } = useStore()
const storeKey = 'documents'
const getTaskState = (status: string, taskType: number) => {
  const statusList = status.split('').reverse()
  return taskType - 1 > statusList.length + 1 ? 'n' : statusList[taskType - 1]
}
onBeforeRouteUpdate(() => {
  common.savePage(storeKey, null)
  common.saveCondition(storeKey, null)
})
onBeforeRouteLeave((to: any) => {
  if (to.name !== 'Paragraph') {
    common.savePage(storeKey, null)
    common.saveCondition(storeKey, null)
  } else {
    common.saveCondition(storeKey, {
      filterText: filterText.value,
      filterMethod: filterMethod.value,
    })
  }
})
const beforePagination = computed(() => common.paginationConfig[storeKey])
const beforeSearch = computed(() => common.search[storeKey])
const embeddingContentDialogRef = ref<InstanceType<typeof EmbeddingContentDialog>>()
const SyncWebDialogRef = ref()
const loading = ref(false)
let interval: any
const filterText = ref('')
const filterMethod = ref<any>({})
const orderBy = ref<string>('')
const documentData = ref<any[]>([])
const currentMouseId = ref(null)
const knowledgeDetail = ref<any>({})

const paginationConfig = ref({
  current_page: 1,
  page_size: 10,
  total: 0,
})

const ImportDocumentDialogRef = ref()
const multipleTableRef = ref<InstanceType<typeof ElTable>>()
const multipleSelection = ref<any[]>([])
const title = ref('')

const selectKnowledgeDialogRef = ref()

const exportDocument = (document: any) => {
  documentApi
    .exportDocument(document.name, document.knowledge_id, document.id, loading)
    .then(() => {
      MsgSuccess(t('common.exportSuccess'))
    })
}
const exportDocumentZip = (document: any) => {
  documentApi
    .exportDocumentZip(document.name, document.knowledge_id, document.id, loading)
    .then(() => {
      MsgSuccess(t('common.exportSuccess'))
    })
}

function cancelTaskHandle(val: any) {
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  const obj = {
    id_list: arr,
    type: val,
  }
  documentApi.putBatchCancelTask(id, obj, loading).then(() => {
    MsgSuccess(t('views.document.tip.cancelSuccess'))
    multipleTableRef.value?.clearSelection()
  })
}

function clearSelection() {
  multipleTableRef.value?.clearSelection()
}

function openknowledgeDialog(row?: any) {
  const arr: string[] = []
  if (row) {
    arr.push(row.id)
  } else {
    multipleSelection.value.map((v) => {
      if (v) {
        arr.push(v.id)
      }
    })
  }

  selectKnowledgeDialogRef.value.open(arr)
}

function dropdownHandle(obj: any) {
  filterMethod.value[obj.attr] = obj.command
  if (obj.attr == 'status') {
    filterMethod.value['task_type'] = obj.task_type
  }

  getList()
}

function beforeCommand(attr: string, val: any, task_type?: number) {
  return {
    attr: attr,
    command: val,
    task_type,
  }
}

const cancelTask = (row: any, task_type: number) => {
  documentApi.putCancelTask(id, row.id, { type: task_type }).then(() => {
    MsgSuccess(t('views.document.tip.sendMessage'))
  })
}

function importDoc() {
  title.value = t('views.document.importDocument')
  ImportDocumentDialogRef.value.open()
}

function settingDoc(row: any) {
  title.value = t('common.setting')
  ImportDocumentDialogRef.value.open(row)
}

const handleSelectionChange = (val: any[]) => {
  multipleSelection.value = val
}

function openBatchEditDocument() {
  title.value = t('common.setting')
  const arr: string[] = multipleSelection.value.map((v) => v.id)
  ImportDocumentDialogRef.value.open(null, arr)
}

/**
 * 初始化轮询
 */
const initInterval = () => {
  interval = setInterval(() => {
    getList(true)
  }, 6000)
}

/**
 * 关闭轮询
 */
const closeInterval = () => {
  if (interval) {
    clearInterval(interval)
  }
}

function syncDocument(row: any) {
  if (+row.type === 1) {
    syncWebDocument(row)
  } else {
    syncLarkDocument(row)
  }
}

function syncLarkDocument(row: any) {
  MsgConfirm(t('views.document.sync.confirmTitle'), t('views.document.sync.confirmMessage1'), {
    confirmButtonText: t('views.document.sync.label'),
    confirmButtonClass: 'color-danger',
  })
    .then(() => {
      documentApi.putLarkDocumentSync(id, row.id).then(() => {
        getList()
      })
    })
    .catch(() => {})
}

function syncWebDocument(row: any) {
  if (row.meta?.source_url) {
    MsgConfirm(t('views.document.sync.confirmTitle'), t('views.document.sync.confirmMessage1'), {
      confirmButtonText: t('views.document.sync.label'),
      confirmButtonClass: 'color-danger',
    })
      .then(() => {
        documentApi.putDocumentSync(row.knowledge_id, row.id).then(() => {
          getList()
        })
      })
      .catch(() => {})
  } else {
    MsgConfirm(t('common.tip'), t('views.document.sync.confirmMessage2'), {
      confirmButtonText: t('common.confirm'),
      type: 'warning',
    })
      .then(() => {})
      .catch(() => {})
  }
}

function refreshDocument(row: any) {
  const embeddingDocument = (stateList: Array<string>) => {
    return documentApi.putDocumentRefresh(row.knowledge_id, row.id, stateList).then(() => {
      getList()
    })
  }
  embeddingContentDialogRef.value?.open(embeddingDocument)
}

function rowClickHandle(row: any, column: any) {
  if (column && column.type === 'selection') {
    return
  }

  router.push({ path: `/paragraph/${id}/${row.id}` })
}

/*
  快速创建空白文档
*/
function creatQuickHandle(val: string) {
  loading.value = true
  const obj = [{ name: val }]
  document
    .asyncPutDocument(id, obj)
    .then(() => {
      getList()
      MsgSuccess(t('common.createSuccess'))
    })
    .catch(() => {
      loading.value = false
    })
}

function syncMulDocument() {
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  documentApi.putMulSyncDocument(id, arr, loading).then(() => {
    MsgSuccess(t('views.document.sync.successMessage'))
    getList()
  })
}

function syncLarkMulDocument() {
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  documentApi.delMulLarkSyncDocument(id, arr, loading).then(() => {
    MsgSuccess(t('views.document.sync.successMessage'))
    getList()
  })
}

function deleteMulDocument() {
  MsgConfirm(
    `${t('views.document.delete.confirmTitle1')} ${multipleSelection.value.length} ${t('views.document.delete.confirmTitle2')}`,
    t('views.document.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'color-danger',
    },
  )
    .then(() => {
      const arr: string[] = []
      multipleSelection.value.map((v) => {
        if (v) {
          arr.push(v.id)
        }
      })
      documentApi.delMulDocument(id, arr, loading).then(() => {
        MsgSuccess(t('views.document.delete.successMessage'))
        multipleTableRef.value?.clearSelection()
        getList()
      })
    })
    .catch(() => {})
}

function batchRefresh() {
  const arr: string[] = multipleSelection.value.map((v) => v.id)
  const embeddingBatchDocument = (stateList: Array<string>) => {
    documentApi.putBatchRefresh(id, arr, stateList, loading).then(() => {
      MsgSuccess(t('views.document.tip.vectorizationSuccess'))
      multipleTableRef.value?.clearSelection()
    })
  }
  embeddingContentDialogRef.value?.open(embeddingBatchDocument)
}

function deleteDocument(row: any) {
  MsgConfirm(
    `${t('views.document.delete.confirmTitle3')} ${row.name} ?`,
    `${t('views.document.delete.confirmMessage1')} ${row.paragraph_count} ${t('views.document.delete.confirmMessage2')}`,
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'color-danger',
    },
  )
    .then(() => {
      documentApi.delDocument(id, row.id, loading).then(() => {
        MsgSuccess(t('common.deleteSuccess'))
        getList()
      })
    })
    .catch(() => {})
}

/*
  更新名称或状态
*/
function updateData(documentId: string, data: any, msg: string) {
  documentApi
    .putDocument(id, documentId, data, loading)
    .then((res) => {
      const index = documentData.value.findIndex((v) => v.id === documentId)
      documentData.value.splice(index, 1, res.data)
      MsgSuccess(msg)
      return true
    })
    .catch(() => {
      return false
    })
}

function changeState(row: any) {
  const obj = {
    is_active: !row.is_active,
  }
  const str = !row.is_active ? t('common.status.enableSuccess') : t('common.status.disableSuccess')
  currentMouseId.value && updateData(row.id, obj, str)
}

function editName(val: string, id: string) {
  if (val) {
    const obj = {
      name: val,
    }
    updateData(id, obj, t('common.modifySuccess'))
  } else {
    MsgError(t('views.document.tip.nameMessage'))
  }
}

function cellMouseEnter(row: any) {
  currentMouseId.value = row.id
}

function cellMouseLeave() {
  currentMouseId.value = null
}

function handleSizeChange() {
  paginationConfig.value.current_page = 1
  getList()
}

function handleSortChange({ prop, order }: { prop: string; order: string }) {
  orderBy.value = order === 'ascending' ? prop : `-${prop}`
  getList()
}

function getList(bool?: boolean) {
  const param = {
    ...(filterText.value && { name: filterText.value }),
    ...filterMethod.value,
    order_by: orderBy.value,
    folder_id: folderId,
  }
  documentApi
    .getDocumentPage(id as string, paginationConfig.value, param, bool ? undefined : loading)
    .then((res) => {
      documentData.value = res.data.records
      paginationConfig.value.total = res.data.total
    })
}

function getDetail() {
  knowledge.asyncGetKnowledgeDetail(id, loading).then((res: any) => {
    knowledgeDetail.value = res.data
  })
}

function refreshMigrate() {
  multipleTableRef.value?.clearSelection()
  getList()
}

function refresh() {
  paginationConfig.value.current_page = 1
  getList()
}

const GenerateRelatedDialogRef = ref()

function openGenerateDialog(row?: any) {
  const arr: string[] = []
  if (row) {
    arr.push(row.id)
  } else {
    multipleSelection.value.map((v) => {
      if (v) {
        arr.push(v.id)
      }
    })
  }

  GenerateRelatedDialogRef.value.open(arr, 'document')
}

onMounted(() => {
  getDetail()
  if (beforePagination.value) {
    paginationConfig.value = beforePagination.value
  }
  if (beforeSearch.value) {
    filterText.value = beforeSearch.value['filterText']
    filterMethod.value = beforeSearch.value['filterMethod']
  }
  getList()
  // 初始化定时任务
  // initInterval()
})

onBeforeUnmount(() => {
  // 清除定时任务
  closeInterval()
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
}
</style>
