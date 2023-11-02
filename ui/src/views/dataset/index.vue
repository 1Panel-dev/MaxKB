<template>
  <div class="dataset-list-container p-15">
    <div class="flex-between">
      <h3>数据集</h3>
      <el-input
        v-model="filterText"
        placeholder="搜索内容"
        suffix-icon="Search"
        style="width: 300px"
      />
    </div>
    <div>
      <el-row
        :gutter="15"
        v-infinite-scroll="loadDataset"
        :infinite-scroll-disabled="disabledScroll"
      >
        <el-col :xs="24" :sm="12" :md="6" :lg="5" :xl="4" class="mt-10">
          <CardAdd title="创建数据集" @click="router.push({ path: '/dataset/create' })" />
        </el-col>
        <el-col
          :xs="24"
          :sm="12"
          :md="6"
          :lg="5"
          :xl="4"
          v-for="(item, index) in datasetList"
          :key="index"
          class="mt-10"
        >
          <CardBox :title="item.name" :description="item.desc" class="cursor">
            <template #mouseEnter>
              <div class="delete-button">
                <el-button type="primary" link @click.stop="deleteDateset(item)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </template>

            <template #footer>
              <div class="footer-content">
                {{ item?.document_count || 0 }}文档数 {{ item?.char_length || 0 }}字符数
                {{ item?.char_length || 0 }}关联应用
              </div>
            </template>
          </CardBox>
        </el-col>
      </el-row>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import datasetApi from '@/api/dataset'
import type { datasetListRequest } from '@/api/type/dataset'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { useRouter } from 'vue-router'
const router = useRouter()

const loading = ref(false)
const filterText = ref('')
const datasetList = ref<any[]>([])
const disabledScroll = ref(false)
const pageConfig = ref<datasetListRequest>({
  current_page: 1,
  page_size: 20,
  search_text: ''
})

function loadDataset() {}

function deleteDateset(row: any) {
  MsgConfirm(
    {
      title: `是否删除数据集：${row.name}？`,
      decription: '此数据集关联2个应用，删除后无法恢复，请谨慎操作。',
      confirmButtonText: '删除'
    },
    {
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
    .getDateset(pageConfig.value)
    .then((res) => {
      datasetList.value = res.data
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
    right: 10px;
    top: 10px;
  }
}
</style>
