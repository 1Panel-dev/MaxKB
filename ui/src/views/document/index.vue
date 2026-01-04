<template>
  <div class="document p-16-24">
    <h2 class="mb-16">{{ $t('common.fileUpload.document') }}</h2>
    <el-card style="--el-card-padding: 0">
      <div class="main-calc-height">
        <div class="p-24">
          <div class="flex-between">
            <div>
              <template v-if="!isShared">
                <el-button
                  v-if="knowledgeDetail?.type === 0 && permissionPrecise.doc_create(id)"
                  type="primary"
                  @click="
                    router.push({
                      path: `/knowledge/document/upload/${folderId}/${type}`,
                      query: { id: id },
                    })
                  "
                  >{{ $t('views.document.uploadDocument') }}
                </el-button>
                <el-button
                  v-if="knowledgeDetail?.type === 1 && permissionPrecise.doc_create(id)"
                  type="primary"
                  @click="importDoc"
                  >{{ $t('views.document.importDocument') }}
                </el-button>
                <el-button
                  v-if="knowledgeDetail?.type === 2 && permissionPrecise.doc_create(id)"
                  type="primary"
                  @click="
                    router.push({
                      path: `/knowledge/import/lark/${folderId}`,
                      query: {
                        id: id,
                        folder_token: knowledgeDetail?.meta.folder_token,
                      },
                    })
                  "
                  >{{ $t('views.document.importDocument') }}
                </el-button>
                <el-button
                  v-if="knowledgeDetail?.type === 4 && permissionPrecise.doc_create(id)"
                  type="primary"
                  @click="toImportWorkflow"
                  >{{ $t('views.document.importDocument') }}
                </el-button>
                <el-button
                  @click="batchRefresh"
                  :disabled="multipleSelection.length === 0"
                  v-if="permissionPrecise.doc_vector(id)"
                  >{{ $t('views.knowledge.setting.vectorization') }}
                </el-button>
                <el-button
                  @click="openGenerateDialog()"
                  :disabled="multipleSelection.length === 0"
                  v-if="permissionPrecise.doc_generate(id)"
                  >{{ $t('views.document.generateQuestion.title') }}
                </el-button>
                <el-button
                  @click="openBatchEditDocument"
                  :disabled="multipleSelection.length === 0"
                  v-if="permissionPrecise.doc_edit(id)"
                >
                  {{ $t('common.setting') }}
                </el-button>

                <el-dropdown v-if="MoreFilledPermission0(id)">
                  <el-button class="ml-12 mr-12">
                    <AppIcon iconName="app-more"></AppIcon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item
                        @click="openknowledgeDialog()"
                        :disabled="multipleSelection.length === 0"
                        v-if="permissionPrecise.doc_migrate(id)"
                      >
                        {{ $t('views.document.setting.migration') }}
                      </el-dropdown-item>
                      <el-dropdown-item
                        @click="openAddTagDialog()"
                        :disabled="multipleSelection.length === 0"
                        v-if="permissionPrecise.doc_tag(id)"
                        >{{ $t('views.document.tag.addTag') }}
                      </el-dropdown-item>
                      <el-dropdown-item
                        divided
                        @click="syncMulDocument"
                        :disabled="multipleSelection.length === 0"
                        v-if="knowledgeDetail?.type === 1 && permissionPrecise.doc_sync(id)"
                        >{{ $t('views.document.syncDocument') }}
                      </el-dropdown-item>
                      <el-dropdown-item
                        divided
                        @click="syncLarkMulDocument"
                        :disabled="multipleSelection.length === 0"
                        v-if="knowledgeDetail?.type === 2 && permissionPrecise.doc_sync(id)"
                        >{{ $t('views.document.syncDocument') }}
                      </el-dropdown-item>

                      <el-dropdown-item
                        divided
                        @click="deleteMulDocument"
                        :disabled="multipleSelection.length === 0"
                        v-if="permissionPrecise.doc_delete(id)"
                        >{{ $t('common.delete') }}
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </template>
            </div>
            <div class="flex">
              <div class="flex-between complex-search">
                <el-select
                  class="complex-search__left"
                  v-model="search_type"
                  style="width: 120px"
                  @change="search_type_change"
                >
                  <el-option :label="$t('dynamicsForm.tag.label')" value="tag" />
                  <el-option :label="$t('common.name')" value="name" />
                </el-select>
                <el-input
                  v-if="search_type === 'name'"
                  v-model="search_form.name"
                  @change="refresh"
                  :placeholder="$t('common.searchBar.placeholder')"
                  style="width: 220px"
                  clearable
                />
                <el-input
                  v-if="search_type === 'tag'"
                  v-model="search_form.tag"
                  @change="refresh"
                  :placeholder="$t('views.document.tag.requiredMessage3')"
                  style="width: 220px"
                  clearable
                />
              </div>

              <el-tooltip
                effect="dark"
                :content="$t('workflow.ExecutionRecord')"
                placement="top"
                v-if="knowledgeDetail?.type === 4 && permissionPrecise.doc_create(id)"
              >
                <el-button @click="openListAction" class="ml-12">
                  <AppIcon iconName="app-execution-record" class="color-secondary"></AppIcon>
                </el-button>
              </el-tooltip>
              <el-button @click="openTagDrawer" class="ml-12" v-if="permissionPrecise.tag_read(id)">
                {{ $t('views.document.tag.label') }}
              </el-button>
            </div>
          </div>
          <app-table
            ref="multipleTableRef"
            class="mt-16 document-table"
            :data="documentData"
            :pagination-config="paginationConfig"
            :quick-create="
              knowledgeDetail?.type === 0 && permissionPrecise.doc_create(id) && !isShared
            "
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
            <el-table-column
              type="selection"
              width="55"
              :reserve-selection="true"
              v-if="!isShared"
            />
            <el-table-column prop="name" :label="$t('views.document.table.name')" min-width="280">
              <template #default="{ row }">
                <ReadWrite
                  v-if="!isShared"
                  @change="editName($event, row.id)"
                  :data="row.name"
                  :showEditIcon="row.id === currentMouseId"
                />
                <span v-else>{{ row.name }}</span>
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
                          >{{ $t('common.status.all') }}
                        </el-dropdown-item>
                        <el-dropdown-item
                          :class="filterMethod['status'] === State.SUCCESS ? 'is-active' : ''"
                          class="justify-center"
                          :command="beforeCommand('status', State.SUCCESS)"
                          >{{ $t('common.status.success') }}
                        </el-dropdown-item>
                        <el-dropdown-item
                          :class="filterMethod['status'] === State.FAILURE ? 'is-active' : ''"
                          class="justify-center"
                          :command="beforeCommand('status', State.FAILURE)"
                          >{{ $t('common.status.fail') }}
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
                          >{{ $t('common.status.all') }}
                        </el-dropdown-item>
                        <el-dropdown-item
                          :class="filterMethod['is_active'] === true ? 'is-active' : ''"
                          class="justify-center"
                          :command="beforeCommand('is_active', true)"
                          >{{ $t('common.status.enabled') }}
                        </el-dropdown-item>
                        <el-dropdown-item
                          :class="filterMethod['is_active'] === false ? 'is-active' : ''"
                          class="justify-center"
                          :command="beforeCommand('is_active', false)"
                          >{{ $t('common.status.disabled') }}
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
                          >{{ $t('common.status.all') }}
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
            <el-table-column
              :label="$t('common.operation')"
              align="left"
              width="160"
              fixed="right"
              v-if="!isShared"
            >
              <template #default="{ row }">
                <span @click.stop>
                  <el-switch
                    :loading="loading"
                    size="small"
                    v-model="row.is_active"
                    :before-change="() => changeState(row)"
                    v-if="permissionPrecise.doc_edit(id)"
                  />
                </span>
                <el-divider direction="vertical" />
                <template v-if="knowledgeDetail?.type === 0 || knowledgeDetail?.type === 4">
                  <el-tooltip
                    effect="dark"
                    :content="$t('views.document.setting.cancelVectorization')"
                    placement="top"
                    v-if="
                      ([State.STARTED, State.PENDING] as Array<string>).includes(
                        getTaskState(row.status, TaskType.EMBEDDING),
                      )
                    "
                  >
                    <span class="mr-4">
                      <el-button
                        type="primary"
                        text
                        @click.stop="cancelTask(row, TaskType.EMBEDDING)"
                        v-if="permissionPrecise.doc_vector(id)"
                      >
                        <el-icon><Close /></el-icon>
                      </el-button>
                    </span>
                  </el-tooltip>
                  <el-tooltip
                    effect="dark"
                    :content="$t('views.knowledge.setting.vectorization')"
                    placement="top"
                    v-else
                  >
                    <span class="mr-4" v-if="permissionPrecise.doc_vector(id)">
                      <el-button type="primary" text @click.stop="refreshDocument(row)">
                        <AppIcon iconName="app-document-refresh" style="font-size: 16px"></AppIcon>
                      </el-button>
                    </span>
                  </el-tooltip>
                  <el-tooltip
                    effect="dark"
                    :content="$t('common.setting')"
                    placement="top"
                    v-if="permissionPrecise.doc_edit(id)"
                  >
                    <span class="mr-4">
                      <el-button type="primary" text @click.stop="settingDoc(row)">
                        <AppIcon iconName="app-setting"></AppIcon>
                      </el-button>
                    </span>
                  </el-tooltip>
                  <span @click.stop>
                    <el-dropdown trigger="click" v-if="MoreFilledPermission1(id)">
                      <el-button text type="primary">
                        <AppIcon iconName="app-more"></AppIcon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item
                            v-if="
                              ([State.STARTED, State.PENDING] as Array<string>).includes(
                                getTaskState(row.status, TaskType.GENERATE_PROBLEM),
                              ) && permissionPrecise.doc_generate(id)
                            "
                            @click="cancelTask(row, TaskType.GENERATE_PROBLEM)"
                          >
                            <el-icon class="color-secondary"><Close /></el-icon>
                            {{ $t('views.document.setting.cancelGenerateQuestion') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            @click="openGenerateDialog(row)"
                            v-else-if="permissionPrecise.doc_generate(id)"
                          >
                            <AppIcon
                              iconName="app-generate-question"
                              class="color-secondary"
                            ></AppIcon>
                            {{ $t('views.document.generateQuestion.title') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            @click="openTagSettingDrawer(row)"
                            v-if="permissionPrecise.doc_tag(id)"
                          >
                            <AppIcon iconName="app-tag" class="color-secondary"></AppIcon>

                            {{ $t('views.document.tag.setting') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            @click="openknowledgeDialog(row)"
                            v-if="permissionPrecise.doc_migrate(id)"
                          >
                            <AppIcon iconName="app-migrate" class="color-secondary"></AppIcon>
                            {{ $t('views.document.setting.migration') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            @click="exportDocument(row)"
                            v-if="permissionPrecise.doc_export(id)"
                          >
                            <AppIcon iconName="app-export" class="color-secondary"></AppIcon>
                            {{ $t('views.document.setting.export') }} Excel
                          </el-dropdown-item>
                          <el-dropdown-item
                            @click="exportDocumentZip(row)"
                            v-if="permissionPrecise.doc_export(id)"
                          >
                            <AppIcon iconName="app-export" class="color-secondary"></AppIcon>
                            {{ $t('views.document.setting.export') }} Zip
                          </el-dropdown-item>
                          <el-dropdown-item
                            @click.stop="downloadDocument(row)"
                            v-if="permissionPrecise.doc_download(id)"
                          >
                            <AppIcon iconName="app-download" class="color-secondary" />
                            {{ $t('views.document.setting.download') }}
                          </el-dropdown-item>
                          <el-upload
                            v-if="permissionPrecise.doc_replace(id)"
                            ref="elUploadRef"
                            :file-list="[]"
                            action="#"
                            :auto-upload="false"
                            :show-file-list="false"
                            :on-change="(file: any, fileList: any) => replaceDocument(file, row)"
                          >
                            <el-dropdown-item>
                              <AppIcon iconName="app-upload" class="color-secondary" />
                              {{ $t('views.document.setting.replace') }}
                            </el-dropdown-item>
                          </el-upload>
                          <el-dropdown-item
                            @click.stop="deleteDocument(row)"
                            v-if="permissionPrecise.doc_delete(id)"
                          >
                            <AppIcon iconName="app-delete" class="color-secondary"></AppIcon>
                            {{ $t('common.delete') }}</el-dropdown-item
                          >
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </span>
                </template>
                <template v-if="knowledgeDetail?.type === 1 || knowledgeDetail?.type === 2">
                  <el-tooltip
                    effect="dark"
                    :content="$t('views.document.setting.cancelVectorization')"
                    placement="top"
                    v-if="
                      ([State.STARTED, State.PENDING] as Array<string>).includes(
                        getTaskState(row.status, TaskType.EMBEDDING),
                      ) && permissionPrecise.doc_vector(id)
                    "
                  >
                    <span class="mr-4">
                      <el-button
                        type="primary"
                        text
                        @click.stop="cancelTask(row, TaskType.EMBEDDING)"
                      >
                        <el-icon><Close /></el-icon>
                      </el-button>
                    </span>
                  </el-tooltip>
                  <el-tooltip
                    effect="dark"
                    :content="$t('views.knowledge.setting.vectorization')"
                    placement="top"
                    v-if="permissionPrecise.vector(id)"
                  >
                    <span class="mr-4">
                      <el-button type="primary" text @click.stop="refreshDocument(row)">
                        <AppIcon iconName="app-document-refresh" style="font-size: 16px"></AppIcon>
                      </el-button>
                    </span>
                  </el-tooltip>
                  <el-tooltip
                    effect="dark"
                    :content="$t('common.setting')"
                    placement="top"
                    v-if="permissionPrecise.doc_edit(id)"
                  >
                    <span class="mr-4">
                      <el-button type="primary" text @click.stop="settingDoc(row)">
                        <AppIcon iconName="app-setting"></AppIcon>
                      </el-button>
                    </span>
                  </el-tooltip>
                  <span @click.stop>
                    <el-dropdown trigger="click" v-if="MoreFilledPermission2(id)">
                      <el-button text type="primary">
                        <AppIcon iconName="app-more"></AppIcon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item
                            @click="syncDocument(row)"
                            v-if="permissionPrecise.sync(id)"
                          >
                            <AppIcon iconName="app-sync" class="color-secondary"></AppIcon>
                            {{ $t('views.knowledge.setting.sync') }}</el-dropdown-item
                          >
                          <el-dropdown-item
                            @click="openTagSettingDrawer(row)"
                            v-if="permissionPrecise.doc_tag(id)"
                          >
                            <AppIcon iconName="app-tag" class="color-secondary"></AppIcon>

                            {{ $t('views.document.tag.setting') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            v-if="
                              permissionPrecise.doc_generate(id) &&
                              ([State.STARTED, State.PENDING] as Array<string>).includes(
                                getTaskState(row.status, TaskType.GENERATE_PROBLEM),
                              )
                            "
                            @click="cancelTask(row, TaskType.GENERATE_PROBLEM)"
                          >
                            <el-icon class="color-secondary"><Close /></el-icon>
                            {{ $t('views.document.setting.cancelGenerateQuestion') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            @click="openGenerateDialog(row)"
                            v-else-if="permissionPrecise.doc_generate(id)"
                          >
                            <AppIcon
                              iconName="app-generate-question"
                              class="color-secondary"
                            ></AppIcon>
                            {{ $t('views.document.generateQuestion.title') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            @click="openknowledgeDialog(row)"
                            v-if="permissionPrecise.doc_migrate(id)"
                          >
                            <AppIcon iconName="app-migrate" class="color-secondary"></AppIcon>
                            {{ $t('views.document.setting.migration') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            @click="exportDocument(row)"
                            v-if="permissionPrecise.doc_export(id)"
                          >
                            <AppIcon iconName="app-export" class="color-secondary"></AppIcon>
                            {{ $t('views.document.setting.export') }} Excel
                          </el-dropdown-item>
                          <el-dropdown-item
                            @click="exportDocumentZip(row)"
                            v-if="permissionPrecise.doc_export(id)"
                          >
                            <AppIcon iconName="app-export" class="color-secondary"></AppIcon>
                            {{ $t('views.document.setting.export') }} Zip
                          </el-dropdown-item>
                          <el-dropdown-item
                            @click.stop="deleteDocument(row)"
                            v-if="permissionPrecise.doc_delete(id)"
                          >
                            <AppIcon iconName="app-delete" class="color-secondary"></AppIcon>
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
        v-if="permissionPrecise.doc_vector(id)"
      >
        {{ $t('views.document.setting.cancelVectorization') }}
      </el-button>
      <el-button
        :disabled="multipleSelection.length === 0"
        @click="cancelTaskHandle(2)"
        v-if="permissionPrecise.doc_generate(id)"
      >
        {{ $t('views.document.setting.cancelGenerate') }}
      </el-button>
      <el-text type="info" class="secondary ml-24">
        {{ $t('common.selected') }} {{ multipleSelection.length }}
        {{ $t('views.document.items') }}
      </el-text>
      <el-button class="ml-16" type="primary" link @click="clearSelection">
        {{ $t('common.clear') }}
      </el-button>
    </div>

    <EmbeddingContentDialog ref="embeddingContentDialogRef"></EmbeddingContentDialog>

    <ImportDocumentDialog ref="ImportDocumentDialogRef" :title="title" @refresh="refresh" />
    <!-- 选择知识库 -->
    <SelectKnowledgeDialog
      ref="selectKnowledgeDialogRef"
      @refresh="refreshMigrate"
      :workspaceId="knowledgeDetail?.workspace_id"
    />
    <GenerateRelatedDialog ref="GenerateRelatedDialogRef" @refresh="getList" :apiType="apiType" />
    <TagDrawer ref="tagDrawerRef" />
    <TagSettingDrawer ref="tagSettingDrawerRef" />
    <AddTagDialog ref="addTagDialogRef" @addTags="addTags" :apiType="apiType" />
    <!-- 执行详情 -->
    <ExecutionRecord ref="ListActionRef"></ExecutionRecord>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute, onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'
import type { ElTable } from 'element-plus'
import ImportDocumentDialog from './component/ImportDocumentDialog.vue'
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
import permissionMap from '@/permission'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import TagDrawer from './tag/TagDrawer.vue'
import TagSettingDrawer from './tag/TagSettingDrawer.vue'
import AddTagDialog from '@/views/document/tag/MulAddTagDialog.vue'
import ExecutionRecord from '@/views/knowledge-workflow/component/execution-record/ExecutionRecordDrawer.vue'

const route = useRoute()
const router = useRouter()
const {
  params: { id, folderId, type }, // id为knowledgeID
} = route as any
const { common } = useStore()
const storeKey = 'documents'
onBeforeRouteUpdate(() => {
  common.savePage(storeKey, null)
  common.saveCondition(storeKey, null)
})
onBeforeRouteLeave((to: any) => {
  if (to.name !== 'ParagraphIndex') {
    common.savePage(storeKey, null)
    common.saveCondition(storeKey, null)
  } else {
    common.saveCondition(storeKey, {
      search_type: search_type.value,
      search_form: search_form.value,
      filterMethod: filterMethod.value,
    })
  }
})

const isShared = computed(() => {
  return folderId === 'share'
})

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else if (route.path.includes('share/')) {
    return 'workspaceShare'
  } else {
    return 'workspace'
  }
})
const permissionPrecise = computed(() => {
  return permissionMap['knowledge'][apiType.value]
})

const MoreFilledPermission0 = (id: string) => {
  return (
    permissionPrecise.value.doc_migrate(id) ||
    (knowledgeDetail?.value.type === 1 && permissionPrecise.value.doc_sync(id)) ||
    (knowledgeDetail?.value.type === 2 && permissionPrecise.value.doc_sync(id)) ||
    permissionPrecise.value.doc_delete(id) ||
    permissionPrecise.value.doc_tag(id)
  )
}

const MoreFilledPermission1 = (id: string) => {
  return (
    permissionPrecise.value.doc_generate(id) ||
    permissionPrecise.value.doc_migrate(id) ||
    permissionPrecise.value.doc_export(id) ||
    permissionPrecise.value.doc_download(id) ||
    permissionPrecise.value.doc_delete(id) ||
    permissionPrecise.value.doc_tag(id) ||
    permissionPrecise.value.doc_replace(id)
  )
}

const MoreFilledPermission2 = (id: string) => {
  return (
    permissionPrecise.value.sync(id) ||
    permissionPrecise.value.doc_generate(id) ||
    permissionPrecise.value.doc_migrate(id) ||
    permissionPrecise.value.doc_export(id) ||
    permissionPrecise.value.doc_delete(id)
  )
}

const getTaskState = (status: string, taskType: number) => {
  const statusList = status.split('').reverse()
  return taskType - 1 > statusList.length + 1 ? 'n' : statusList[taskType - 1]
}

const search_type = ref('name')
const search_form = ref<any>({
  name: '',
  tag: '',
})

const beforePagination = computed(() => common.paginationConfig[storeKey])
const beforeSearch = computed(() => common.search[storeKey])
const embeddingContentDialogRef = ref<InstanceType<typeof EmbeddingContentDialog>>()
const ListActionRef = ref<InstanceType<typeof ExecutionRecord>>()
const loading = ref(false)
let interval: any

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

const openListAction = () => {
  ListActionRef.value?.open(id)
}

const toImportWorkflow = () => {
  if (knowledgeDetail.value.is_publish) {
    router.push({
      path: `/knowledge/import/workflow/${folderId}`,
      query: {
        id: id,
      },
    })
  } else {
    MsgConfirm(t('common.tip'), t('views.document.tip.toImportDocConfirm'), {
      cancelButtonText: t('common.close'),
      showConfirmButton: false,
      type: 'warning',
    })
      .then(() => {})
      .catch(() => {})
  }
}

const exportDocument = (document: any) => {
  loadSharedApi({ type: 'document', systemType: apiType.value })
    .exportDocument(document.name, document.knowledge_id, document.id, loading)
    .then(() => {
      MsgSuccess(t('common.exportSuccess'))
    })
}
const exportDocumentZip = (document: any) => {
  loadSharedApi({ type: 'document', systemType: apiType.value })
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
  loadSharedApi({ type: 'document', systemType: apiType.value })
    .putBatchCancelTask(id, obj, loading)
    .then(() => {
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
  loadSharedApi({ type: 'document', systemType: apiType.value })
    .putCancelTask(id, row.id, { type: task_type })
    .then(() => {
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
    confirmButtonClass: 'danger',
  })
    .then(() => {
      loadSharedApi({ type: 'document', systemType: apiType.value })
        .putLarkDocumentSync(id, row.id)
        .then(() => {
          getList()
        })
    })
    .catch(() => {})
}

function syncWebDocument(row: any) {
  if (row.meta?.source_url) {
    MsgConfirm(t('views.document.sync.confirmTitle'), t('views.document.sync.confirmMessage1'), {
      confirmButtonText: t('views.document.sync.label'),
      confirmButtonClass: 'danger',
    })
      .then(() => {
        loadSharedApi({ type: 'document', systemType: apiType.value })
          .putDocumentSync(row.knowledge_id, row.id)
          .then(() => {
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
    return loadSharedApi({ type: 'document', systemType: apiType.value })
      .putDocumentRefresh(row.knowledge_id, row.id, stateList)
      .then(() => {
        getList()
      })
  }
  embeddingContentDialogRef.value?.open(embeddingDocument)
}

function rowClickHandle(row: any, column: any) {
  if (column && column.type === 'selection') {
    return
  }

  router.push({
    path: `/paragraph/${id}/${row.id}`,
    query: { from: apiType.value, isShared: isShared.value ? 'true' : 'false' },
  })
}

/*
  快速创建空白文档
*/
function creatQuickHandle(val: string) {
  loading.value = true
  const obj = [{ name: val }]
  loadSharedApi({ type: 'document', systemType: apiType.value })
    .putMulDocument(id, obj)
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
  MsgConfirm(t('views.document.sync.confirmTitle'), t('views.document.sync.confirmMessage1'), {
    confirmButtonText: t('views.document.sync.label'),
    confirmButtonClass: 'danger',
  })
    .then(() => {
      loadSharedApi({ type: 'document', systemType: apiType.value })
        .putMulSyncDocument(id, arr, loading)
        .then(() => {
          MsgSuccess(t('views.document.sync.successMessage'))
          getList()
        })
    })
    .catch(() => {})
}

function syncLarkMulDocument() {
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  loadSharedApi({ type: 'document', systemType: apiType.value })
    .putMulLarkSyncDocument(id, arr, loading)
    .then(() => {
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
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      const arr: string[] = []
      multipleSelection.value.map((v) => {
        if (v) {
          arr.push(v.id)
        }
      })
      loadSharedApi({ type: 'document', systemType: apiType.value })
        .delMulDocument(id, arr, loading)
        .then(() => {
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
    loadSharedApi({ type: 'document', systemType: apiType.value })
      .putBatchRefresh(id, arr, stateList, loading)
      .then(() => {
        MsgSuccess(t('views.document.tip.vectorizationSuccess'))
        multipleTableRef.value?.clearSelection()
      })
  }
  embeddingContentDialogRef.value?.open(embeddingBatchDocument)
}

function downloadDocument(row: any) {
  loadSharedApi({ type: 'document', systemType: apiType.value })
    .getDownloadSourceFile(id, row.id, row.name)
    .then(() => {
      getList()
    })
}

const elUploadRef = ref()

function replaceDocument(file: any, row: any) {
  const formData = new FormData()
  formData.append('file', file.raw, file.name)
  elUploadRef.value.clearFiles()
  loadSharedApi({ type: 'document', systemType: apiType.value })
    .postReplaceSourceFile(id, row.id, formData, loading)
    .then(() => {
      MsgSuccess(t('views.document.tip.replaceSuccess'))
      getList()
    })
    .catch((e: any) => {})
}

function deleteDocument(row: any) {
  MsgConfirm(
    `${t('views.document.delete.confirmTitle3')} ${row.name} ?`,
    `${t('views.document.delete.confirmMessage1')} ${row.paragraph_count} ${t('views.document.delete.confirmMessage2')}`,
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      loadSharedApi({ type: 'document', systemType: apiType.value })
        .delDocument(id, row.id, loading)
        .then(() => {
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
  loadSharedApi({ type: 'document', systemType: apiType.value })
    .putDocument(id, documentId, data, loading)
    .then((res: any) => {
      const index = documentData.value.findIndex((v) => v.id === documentId)
      documentData.value.splice(index, 1, res.data)
      MsgSuccess(msg)
      return true
    })
    .catch(() => {
      return false
    })
}

async function changeState(row: any) {
  const obj = {
    is_active: !row.is_active,
  }
  const str = !row.is_active ? t('common.status.enableSuccess') : t('common.status.disableSuccess')
  await updateData(row.id, obj, str)
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
    ...filterMethod.value,
    order_by: orderBy.value,
    folder_id: folderId,
  }
  if (search_form.value[search_type.value]) {
    param[search_type.value] = search_form.value[search_type.value]
  }
  loadSharedApi({ type: 'document', isShared: isShared.value, systemType: apiType.value })
    .getDocumentPage(id as string, paginationConfig.value, param, bool ? undefined : loading)
    .then((res: any) => {
      documentData.value = res.data.records
      paginationConfig.value.total = res.data.total
    })
}

const search_type_change = () => {
  search_form.value = { name: '', tag: '' }
}

function getDetail() {
  loadSharedApi({ type: 'knowledge', isShared: isShared.value, systemType: apiType.value })
    .getKnowledgeDetail(id, loading)
    .then((res: any) => {
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

const tagDrawerRef = ref()
function openTagDrawer() {
  tagDrawerRef.value.open()
}

const tagSettingDrawerRef = ref()
function openTagSettingDrawer(doc: any) {
  tagSettingDrawerRef.value.open(doc)
}

const addTagDialogRef = ref()

function openAddTagDialog() {
  addTagDialogRef.value?.open()
}

function addTags(tags: any) {
  const arr: string[] = multipleSelection.value.map((v) => v.id)

  loadSharedApi({ type: 'document', systemType: apiType.value })
    .postMulDocumentTags(id, { tag_ids: tags, document_ids: arr }, loading)
    .then(() => {
      addTagDialogRef.value?.close()
      getList()
      clearSelection()
    })
}

onMounted(() => {
  getDetail()
  if (beforePagination.value) {
    paginationConfig.value = beforePagination.value
  }
  if (beforeSearch.value) {
    filterMethod.value = beforeSearch.value['filterMethod']
    search_type.value = beforeSearch.value['search_type']
    search_form.value = beforeSearch.value['search_form']
  }
  getList()
  // 初始化定时任务
  initInterval()
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
  .document-table {
    :deep(.el-table__row) {
      cursor: pointer;
    }
  }
}
</style>
