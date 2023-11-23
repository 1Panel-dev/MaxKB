<template>
  <div class="application-list-container p-24">
    <div class="flex-between">
      <h3>应用</h3>
      <el-input
        v-model="pageConfig.name"
        @change="search"
        placeholder="按 名称 搜索"
        prefix-icon="Search"
        class="w-240"
      />
    </div>
    <div v-loading.fullscreen.lock="loading">
      <el-row
        :gutter="15"
        v-infinite-scroll="loadDataset"
        :infinite-scroll-disabled="disabledScroll"
        class="app-list-row"
      >
        <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4" class="mt-8">
          <CardAdd title="创建应用" @click="router.push({ path: '/application/create' })" />
        </el-col>
        <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4" class="mt-8">
          <CardBox
            title="应用"
            description="XXXXXX"
            class="application-card cursor"
            @click="router.push({ path: '/application/1/overview' })"
          >
            <div class="status-tag">
              <el-tag class="warning-tag">已停用</el-tag>
              <el-tag class="success-tag">运行中</el-tag>
            </div>

            <template #footer>
              <div class="footer-content">
                <el-tooltip effect="dark" content="演示" placement="top">
                  <el-button text @click.stop>
                    <AppIcon iconName="app-view"></AppIcon>
                  </el-button>
                </el-tooltip>
                <el-divider direction="vertical" />
                <el-tooltip effect="dark" content="设置" placement="top">
                  <el-button text @click.stop>
                    <AppIcon iconName="Setting"></AppIcon>
                  </el-button>
                </el-tooltip>
                <el-divider direction="vertical" />
                <span @click.stop>
                  <el-dropdown trigger="click" placement="bottom-start">
                    <span class="el-dropdown-link">
                      <el-button text>
                        <AppIcon iconName="MoreFilled"></AppIcon>
                      </el-button>
                    </span>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <div class="dropdown-custom-switch">
                          <span>运行中</span><el-switch v-model="state" />
                        </div>
                        <el-dropdown-item divided>删除</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </span>
              </div>
            </template>
          </CardBox>
        </el-col>
      </el-row>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import applicationApi from '@/api/application'
import type { pageRequest } from '@/api/type/common'
//   import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { useRouter } from 'vue-router'
//   import { numberFormat } from '@/utils/utils'
const router = useRouter()

const loading = ref(false)
const disabledScroll = ref(false)
const pageConfig = reactive<pageRequest>({
  current_page: 1,
  page_size: 20,
  name: ''
})

const applicationList = ref<any[]>([])
const state = ref(false)

function loadDataset() {}

function search() {
  pageConfig.current_page = 1
  getList()
}

//   function deleteDateset(row: any) {
//     MsgConfirm(
//       `是否删除数据集：${row.name} ?`,
//       `此数据集关联 ${row.char_length} 个应用，删除后无法恢复，请谨慎操作。`,
//       {
//         confirmButtonText: '删除',
//         confirmButtonClass: 'danger'
//       }
//     )
//       .then(() => {
//         loading.value = true
//         datasetApi
//           .delDateset(row.id)
//           .then(() => {
//             MsgSuccess('删除成功')
//             getList()
//           })
//           .catch(() => {
//             loading.value = false
//           })
//       })
//       .catch(() => {})
//   }

function getList() {
  loading.value = true
  applicationApi
    .getApplication(pageConfig)
    .then((res) => {
      applicationList.value = res.data?.records
      loading.value = false
    })
    .catch(() => {
      loading.value = false
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
