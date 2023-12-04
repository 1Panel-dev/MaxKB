<template>
  <div class="dataset-list-container p-24" style="padding-top: 16px">
    <div class="flex-between mb-16">
      <h3>数据集</h3>
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
        <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4" class="mb-16">
          <CardAdd title="创建数据集" @click="router.push({ path: '/dataset/create' })" />
        </el-col>
        <el-col
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
          :xl="4"
          v-for="(item, index) in datasetList"
          :key="index"
          class="mb-16"
        >
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
                <span class="bold">{{ item?.char_length || 0 }}</span>
                关联应用
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
import datasetApi from '@/api/dataset'
import type { pageRequest } from '@/api/type/common'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { useRouter } from 'vue-router'
import { numberFormat } from '@/utils/utils'
const router = useRouter()

const loading = ref(false)
const datasetList = ref<any[]>([])
const disabledScroll = ref(false)
const pageConfig = reactive<pageRequest>({
  current_page: 1,
  page_size: 20,
  name: ''
})

function loadDataset() {}

function search() {
  pageConfig.current_page = 1
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
  loading.value = true
  datasetApi
    .getDateset(pageConfig)
    .then((res) => {
      datasetList.value = res.data?.records
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
