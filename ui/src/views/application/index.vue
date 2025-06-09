<template>
  <LayoutContainer class="application-manage">
    <template #left>
      <h4 class="p-16 pb-0">{{ $t('views.application.title') }}</h4>
      <folder-tree
        :data="folderList"
        :currentNodeKey="currentFolder?.id"
        @handleNodeClick="folderClickHandel"
        class="p-8"
      />
    </template>
    <ContentContainer :header="currentFolder?.name">
      <template #search>
        <div class="flex">
          <div class="flex-between complex-search">
            <el-select
              class="complex-search__left"
              v-model="search_type"
              style="width: 120px"
              @change="search_type_change"
            >
              <el-option :label="$t('common.creator')" value="create_user"/>

              <el-option :label="$t('common.name')" value="name"/>
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
              <el-option v-for="u in user_options" :key="u.id" :value="u.id" :label="u.username"/>
            </el-select>
          </div>
          <el-dropdown trigger="click">
            <el-button type="primary" class="ml-8">
              {{ $t('common.create') }}
              <el-icon class="el-icon--right">
                <arrow-down/>
              </el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu class="create-dropdown">
                <el-dropdown-item @click="openCreateDialog('SIMPLE')">
                  <div class="flex">
                    <el-avatar shape="square" class="avatar-blue mt-4" :size="36">
                      <img
                        src="@/assets/application/icon_simple_application.svg"
                        style="width: 65%"
                        alt=""
                      />
                    </el-avatar>
                    <div class="pre-wrap ml-8">
                      <div class="lighter">{{ $t('views.application.simple') }}</div>
                      <el-text type="info" size="small">{{
                          $t('views.application.simplePlaceholder')
                        }}
                      </el-text>
                    </div>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item @click="openCreateDialog('WORK_FLOW')">
                  <div class="flex">
                    <el-avatar shape="square" class="avatar-purple mt-4" :size="36">
                      <img
                        src="@/assets/application/icon_workflow_application.svg"
                        style="width: 65%"
                        alt=""
                      />
                    </el-avatar>
                    <div class="pre-wrap ml-8">
                      <div class="lighter">{{ $t('views.application.workflow') }}</div>
                      <el-text type="info" size="small">{{
                          $t('views.application.workflowPlaceholder')
                        }}
                      </el-text>
                    </div>
                  </div>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </template>
      <div>
        <el-row v-if="applicationList.length > 0" :gutter="15">
          <!-- <template v-for="(item, index) in datasetFolderList" :key="index">
            <el-col :xs="24" :sm="12" :md="12" :lg="8" :xl="6" class="mb-16">
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
          </template> -->
          <template v-for="(item, index) in applicationList" :key="index">
            <el-col :xs="24" :sm="12" :md="12" :lg="8" :xl="6" class="mb-16">
              <CardBox
                :title="item.name"
                :description="item.desc"
                class="cursor"
                @click="router.push({ path: `/application/${item.id}/${item.type}/overview` })"
              >
                <template #icon>
                  <LogoIcon height="28px" style="width: 28px; height: 28px; display: block"/>
                </template>
                <template #subTitle>
                  <el-text class="color-secondary" size="small">
                    <auto-tooltip :content="item.username">
                      {{ $t('common.creator') }}: {{ item.username }}
                    </auto-tooltip>
                  </el-text>
                </template>
                <div class="status-tag">
                  <el-tag type="warning" v-if="isWorkFlow(item.type)" style="height: 22px">
                    {{ $t('views.application.workflow') }}
                  </el-tag>
                  <el-tag class="blue-tag" v-else style="height: 22px">
                    {{ $t('views.application.simple') }}
                  </el-tag>
                </div>

                <template #footer>
                  <div class="footer-content">
                    <el-tooltip
                      effect="dark"
                      :content="$t('views.application.setting.demo')"
                      placement="top"
                    >
                      <el-button text @click.stop @click="getAccessToken(item.id)">
                        <AppIcon iconName="app-view"></AppIcon>
                      </el-button>
                    </el-tooltip>
                    <el-divider direction="vertical"/>
                    <el-tooltip effect="dark" :content="$t('common.setting')" placement="top">
                      <el-button text @click.stop="settingApplication(item)">
                        <AppIcon iconName="Setting"></AppIcon>
                      </el-button>
                    </el-tooltip>
                    <el-divider direction="vertical"/>
                    <span @click.stop>
                      <el-dropdown trigger="click">
                        <el-button text @click.stop>
                          <el-icon><MoreFilled/></el-icon>
                        </el-button>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item
                              v-if="is_show_copy_button(item)"
                              @click="copyApplication(item)"
                            >
                              <AppIcon iconName="app-copy"></AppIcon>
                              {{ $t('common.copy') }}
                            </el-dropdown-item>
                            <el-dropdown-item @click.stop="exportApplication(item)">
                              <AppIcon iconName="app-export"></AppIcon>

                              {{ $t('common.export') }}
                            </el-dropdown-item>
                            <el-dropdown-item icon="Delete" @click.stop="deleteApplication(item)">{{
                                $t('common.delete')
                              }}</el-dropdown-item>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </span>
                  </div>
                </template>
                <template #mouseEnter>
                  <div @click.stop>
                    <el-dropdown trigger="click">
                      <el-button text @click.stop>
                        <el-icon>
                          <MoreFilled/>
                        </el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item
                            icon="Refresh"
                            @click.stop="syncDataset(item)"
                            v-if="item.type === 1"
                          >{{ $t('views.knowledge.setting.sync') }}
                          </el-dropdown-item
                          >
                          <el-dropdown-item @click.stop="reEmbeddingDataset(item)">
                            <AppIcon iconName="app-vectorization"></AppIcon>
                            {{ $t('views.knowledge.setting.vectorization') }}
                          </el-dropdown-item>
                          <!--

                          <el-dropdown-item
                            icon="Connection"
                            @click.stop="openGenerateDialog(item)"
                            >{{ $t('views.document.generateQuestion.title') }}</el-dropdown-item
                          >
                          <el-dropdown-item
                            icon="Setting"
                            @click.stop="router.push({ path: `/knowledge/${item.id}/setting` })"
                          >
                            {{ $t('common.setting') }}</el-dropdown-item
                          >
                          <el-dropdown-item @click.stop="export_dataset(item)">
                            <AppIcon iconName="app-export"></AppIcon
                            >{{ $t('views.document.setting.export') }} Excel</el-dropdown-item
                          >
                          <el-dropdown-item @click.stop="export_zip_dataset(item)">
                            <AppIcon iconName="app-export"></AppIcon
                            >{{ $t('views.document.setting.export') }} ZIP</el-dropdown-item
                          >
                          <el-dropdown-item icon="Delete" @click.stop="deleteDataset(item)">{{
                            $t('common.delete')
                          }}</el-dropdown-item> -->
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </template>
              </CardBox>
            </el-col>
          </template>
        </el-row>
        <el-empty :description="$t('common.noData')" v-else/>
      </div>
    </ContentContainer>
    <CreateApplicationDialog ref="CreateApplicationDialogRef"/>
  </LayoutContainer>
</template>

<script lang="ts" setup>
import {onMounted, ref, reactive, computed} from 'vue'
import CreateApplicationDialog from '@/views/application/component/CreateApplicationDialog.vue'
import GenerateRelatedDialog from '@/components/generate-related-dialog/index.vue'
import ApplicaitonApi from '@/api/application/application'
import {MsgSuccess, MsgConfirm} from '@/utils/message'
import useStore from '@/stores'
import {numberFormat} from '@/utils/common'
import {t} from '@/locales'
import {useRouter} from 'vue-router'
import {isWorkFlow} from '@/utils/application'

const router = useRouter()
const {folder} = useStore()

const loading = ref(false)

const search_type = ref('name')
const search_form = ref<{
  name: string
  create_user: string
}>({
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
const applicationList = ref<any[]>([])
const currentFolder = ref<any>({})

const CreateApplicationDialogRef = ref()

function openCreateDialog(type?: string) {
  CreateApplicationDialogRef.value.open(currentFolder.value?.id || 'root', type)
  // common
  //   .asyncGetValid(ValidType.Application, ValidCount.Application, loading)
  //   .then(async (res: any) => {
  //     if (res?.data) {
  //       CreateApplicationDialogRef.value.open()
  //     } else if (res?.code === 400) {
  //       MsgConfirm(t('common.tip'), t('views.application.tip.professionalMessage'), {
  //         cancelButtonText: t('common.confirm'),
  //         confirmButtonText: t('common.professional'),
  //       }).then(() => {
  //         window.open('https://maxkb.cn/pricing.html', '_blank')
  //       })
  //     }
  //   })
}

const search_type_change = () => {
  search_form.value = {name: '', create_user: ''}
}

function getList() {
  const params = {
    folder_id: currentFolder.value?.id || 'root',
  }
  ApplicaitonApi.getApplication(paginationConfig, params, loading).then((res) => {
    paginationConfig.total = res.data.total
    applicationList.value = [...applicationList.value, ...res.data.records]
  })
}

function getFolder() {
  const params = {}
  folder.asyncGetFolder('APPLICATION', params, loading).then((res: any) => {
    folderList.value = res.data
    currentFolder.value = res.data?.[0] || {}
    getList()
  })
}

function folderClickHandel(row: any) {
  currentFolder.value = row
  applicationList.value = []
  getList()
}

onMounted(() => {
  getFolder()
})
</script>

<style lang="scss" scoped></style>
