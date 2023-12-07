<template>
  <div class="dataset-list-container p-24" style="padding-top: 16px">
    <div class="flex-between mb-16">
      <h3>数据集</h3>
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
          <CardAdd title="创建数据集" @click="router.push({ path: '/dataset/create' })" />
        </el-col>
        <template v-for="(item, index) in datasetList" :key="index">
          <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4" class="mb-16">
            <CardBox
              :title="item.name"
              :description="item.desc"
              class="cursor"
              @click="router.push({ path: `/dataset/${item.id}/document` })"
            >
              <template #mouseEnter>
                <el-tooltip effect="dark" content="删除" placement="top">
                  <el-button text @click.stop="deleteDateset(item)" class="delete-button">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </template>

              <template #footer>
                <div class="footer-content">
                  <span class="bold">{{ item?.document_count || 0 }}</span>
                  文档<el-divider direction="vertical" />
                  <span class="bold">{{ numberFormat(item?.char_length) || 0 }}</span>
                  字符<el-divider direction="vertical" />
                  <span class="bold">{{ item?.application_mapping_count || 0 }}</span>
                  关联应用
                </div>
              </template>
            </CardBox>
          </el-col>
        </template>
      </el-row>
      <div style="padding: 16px 10px">
        <el-divider class="custom-divider" v-if="datasetList.length > 0 && loading">
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
import datasetApi from '@/api/dataset'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { useRouter } from 'vue-router'
import { numberFormat } from '@/utils/utils'
const router = useRouter()

const loading = ref(false)
const datasetList = ref<any[]>([])
const pageConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})

const searchValue = ref('')

const noMore = computed(
  () =>
    datasetList.value.length > 0 &&
    datasetList.value.length === pageConfig.total &&
    pageConfig.total > 20 &&
    !loading.value
)
const disabledScroll = computed(
  () => datasetList.value.length > 0 && (loading.value || noMore.value)
)

function loadDataset() {
  if (pageConfig.total > pageConfig.page_size) {
    pageConfig.current_page += 1
    getList()
  }
}

function searchHandle() {
  pageConfig.current_page = 1
  datasetList.value = []
  getList()
}

function deleteDateset(row: any) {
  MsgConfirm(
    `是否删除数据集：${row.name} ?`,
    `此数据集关联 ${row.char_length} 个应用，删除后无法恢复，请谨慎操作。`,
    {
      confirmButtonText: '删除',
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      loading.value = true
      datasetApi
        .delDateset(row.id)
        .then(() => {
          const index = datasetList.value.findIndex((v) => v.id === row.id)
          datasetList.value.splice(index, 1)
          MsgSuccess('删除成功')
        })
        .catch(() => {
          loading.value = false
        })
    })
    .catch(() => {})
}

function getList() {
  datasetApi
    .getDateset(pageConfig, searchValue.value && { name: searchValue.value }, loading)
    .then((res) => {
      pageConfig.total = res.data.total
      datasetList.value = [...datasetList.value, ...res.data.records]
    })
}

onMounted(() => {
  getList()
})
</script>
<style lang="scss" scoped>
.dataset-list-container {
  .delete-button {
    position: absolute;
    right: 12px;
    top: 18px;
    height: auto;
  }
  .footer-content {
    .bold {
      color: var(--app-text-color);
    }
  }
}
</style>
