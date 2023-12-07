<template>
  <div class="application-list-container p-24" style="padding-top: 16px">
    <div class="flex-between mb-16">
      <h3>应用</h3>
      <el-input
        v-model="searchValue"
        @change="searchHandle"
        placeholder="按 名称 搜索"
        prefix-icon="Search"
        class="w-240"
      />
    </div>
    <div v-loading.fullscreen.lock="pageConfig.current_page === 1 && loading">
      <el-row
        :gutter="15"
        v-infinite-scroll="loadDataset"
        :infinite-scroll-disabled="disabledScroll"
      >
        <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4" class="mb-16">
          <CardAdd title="创建应用" @click="router.push({ path: '/application/create' })" />
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
            @click="router.push({ path: `/application/${item.id}/overview` })"
          >
            <template #icon>
              <AppAvatar
                v-if="item.name"
                :name="item.name"
                pinyinColor
                class="mr-12"
                shape="square"
                :size="32"
              />
            </template>

            <template #footer>
              <div class="footer-content">
                <el-tooltip effect="dark" content="演示" placement="top">
                  <el-button text @click.stop @click="getAccessToken(item.id)">
                    <AppIcon iconName="app-view"></AppIcon>
                  </el-button>
                </el-tooltip>
                <el-divider direction="vertical" />
                <el-tooltip effect="dark" content="设置" placement="top">
                  <el-button
                    text
                    @click.stop="router.push({ path: `/application/${item.id}/setting` })"
                  >
                    <AppIcon iconName="Setting"></AppIcon>
                  </el-button>
                </el-tooltip>
                <el-divider direction="vertical" />
                <el-tooltip effect="dark" content="删除" placement="top">
                  <el-button text @click.stop="deleteApplication(item)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </div>
            </template>
          </CardBox>
        </el-col>
      </el-row>
      <div style="padding: 16px 10px">
        <el-divider class="custom-divider" v-if="applicationList.length > 0 && loading">
          <el-text type="info"> 加载中...</el-text>
        </el-divider>
        <el-divider class="custom-divider" v-if="noMore">
          <el-text type="info"> 到底啦！</el-text>
        </el-divider>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import applicationApi from '@/api/application'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { useRouter } from 'vue-router'
import useStore from '@/stores'
const { application } = useStore()
const router = useRouter()

const loading = ref(false)

const applicationList = ref<any[]>([])

const pageConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})

const searchValue = ref('')

const noMore = computed(
  () =>
    applicationList.value.length > 0 &&
    applicationList.value.length === pageConfig.total &&
    pageConfig.total > 20
)
const disabledScroll = computed(
  () => applicationList.value.length > 0 && (loading.value || noMore.value)
)

function loadDataset() {
  if (pageConfig.total > pageConfig.page_size) {
    pageConfig.current_page += 1
    getList()
  }
}

function searchHandle() {
  pageConfig.total = 0
  pageConfig.current_page = 1
  applicationList.value = []
  getList()
}
function getAccessToken(id: string) {
  application.asyncGetAccessToken(id, loading).then((res) => {
    window.open(application.location + res?.data?.access_token)
  })
}

function deleteApplication(row: any) {
  MsgConfirm(`是否删除应用：${row.name} ?`, `删除后该应用将不再提供服务，请谨慎操作。`, {
    confirmButtonText: '删除',
    confirmButtonClass: 'danger'
  })
    .then(() => {
      loading.value = true
      applicationApi
        .delApplication(row.id)
        .then(() => {
          MsgSuccess('删除成功')
          getList()
        })
        .catch(() => {
          loading.value = false
        })
    })
    .catch(() => {})
}


function getList() {
  applicationApi
    .getApplication(pageConfig, searchValue.value && { name: searchValue.value }, loading)
    .then((res) => {
      applicationList.value = [...applicationList.value, ...res.data.records]
      pageConfig.total = res.data.total
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
