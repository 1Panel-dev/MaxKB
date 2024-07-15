<template>
  <div class="application-list-container p-24" style="padding-top: 16px">
    <div class="flex-between mb-16">
      <h4>{{ $t('views.application.applicationList.title') }}</h4>
      <el-input
        v-model="searchValue"
        @change="searchHandle"
        :placeholder="$t('views.application.applicationList.searchBar.placeholder')"
        prefix-icon="Search"
        class="w-240"
        clearable
      />
    </div>
    <div v-loading.fullscreen.lock="paginationConfig.current_page === 1 && loading">
      <InfiniteScroll
        :size="applicationList.length"
        :total="paginationConfig.total"
        :page_size="paginationConfig.page_size"
        v-model:current_page="paginationConfig.current_page"
        @load="getList"
        :loading="loading"
      >
        <el-row :gutter="15">
          <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4" class="mb-16">
            <CardAdd
              :title="$t('views.application.applicationList.card.createApplication')"
              @click="openCreateDialog"
            />
          </el-col>
          <el-col
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
            :xl="4"
            v-for="(item, index) in applicationList"
            :key="index"
            class="mb-16"
          >
            <CardBox
              :title="item.name"
              :description="item.desc"
              class="application-card cursor"
              @click="router.push({ path: `/application/${item.id}/${item.type}/overview` })"
            >
              <template #icon>
                <AppAvatar
                  v-if="isAppIcon(item?.icon)"
                  shape="square"
                  :size="32"
                  style="background: none"
                  class="mr-8"
                >
                  <img :src="item?.icon" alt="" />
                </AppAvatar>
                <AppAvatar
                  v-else-if="item?.name"
                  :name="item?.name"
                  pinyinColor
                  shape="square"
                  :size="32"
                  class="mr-8"
                />
              </template>
              <div class="status-tag">
                <el-tag type="warning" v-if="isWorkFlow(item.type)">高级编排</el-tag>
                <el-tag class="blue-tag" v-else>简单配置</el-tag>
              </div>

              <template #footer>
                <div class="footer-content">
                  <el-tooltip
                    effect="dark"
                    :content="$t('views.application.applicationList.card.demo')"
                    placement="top"
                  >
                    <el-button text @click.stop @click="getAccessToken(item.id)">
                      <AppIcon iconName="app-view"></AppIcon>
                    </el-button>
                  </el-tooltip>
                  <el-divider direction="vertical" />
                  <el-tooltip
                    effect="dark"
                    :content="$t('views.application.applicationList.card.setting')"
                    placement="top"
                  >
                    <el-button text @click.stop="settingApplication(item)">
                      <AppIcon iconName="Setting"></AppIcon>
                    </el-button>
                  </el-tooltip>
                  <el-divider direction="vertical" />
                  <el-tooltip
                    effect="dark"
                    :content="$t('views.application.applicationList.card.delete.tooltip')"
                    placement="top"
                  >
                    <el-button text @click.stop="deleteApplication(item)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </template>
            </CardBox>
          </el-col>
        </el-row>
      </InfiniteScroll>
    </div>
    <CreateApplicationDialog ref="CreateApplicationDialogRef" />
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import applicationApi from '@/api/application'
import CreateApplicationDialog from './component/CreateApplicationDialog.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { isAppIcon } from '@/utils/application'
import { useRouter } from 'vue-router'
import { isWorkFlow } from '@/utils/application'
import useStore from '@/stores'
import { t } from '@/locales'
const { application } = useStore()
const router = useRouter()

const CreateApplicationDialogRef = ref()
const loading = ref(false)

const applicationList = ref<any[]>([])

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})

const searchValue = ref('')

function settingApplication(row: any) {
  if (isWorkFlow(row.type)) {
    router.push({ path: `/application/${row.id}/workflow` })
  } else {
    router.push({ path: `/application/${row.id}/${row.type}/setting` })
  }
}

function openCreateDialog() {
  CreateApplicationDialogRef.value.open()
}

function searchHandle() {
  paginationConfig.total = 0
  paginationConfig.current_page = 1
  applicationList.value = []
  getList()
}
function getAccessToken(id: string) {
  application.asyncGetAccessToken(id, loading).then((res: any) => {
    window.open(application.location + res?.data?.access_token)
  })
}

function deleteApplication(row: any) {
  MsgConfirm(
    // @ts-ignore
    `${t('views.application.applicationList.card.delete.confirmTitle')}${row.name} ?`,
    t('views.application.applicationList.card.delete.confirmMessage'),
    {
      confirmButtonText: t('views.application.applicationList.card.delete.confirmButton'),
      cancelButtonText: t('views.application.applicationList.card.delete.cancelButton'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      applicationApi.delApplication(row.id, loading).then(() => {
        const index = applicationList.value.findIndex((v) => v.id === row.id)
        applicationList.value.splice(index, 1)
        MsgSuccess(t('views.application.applicationList.card.delete.successMessage'))
      })
    })
    .catch(() => {})
}

function getList() {
  applicationApi
    .getApplication(paginationConfig, searchValue.value && { name: searchValue.value }, loading)
    .then((res) => {
      applicationList.value = [...applicationList.value, ...res.data.records]
      paginationConfig.total = res.data.total
    })
}

onMounted(() => {
  getList()
})
</script>
<style lang="scss" scoped>
.application-card {
  .status-tag {
    position: absolute;
    right: 16px;
    top: 20px;
  }
}
.dropdown-custom-switch {
  padding: 5px 11px;
  font-size: 14px;
  font-weight: 400;
  span {
    margin-right: 26px;
  }
}
</style>
