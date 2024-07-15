<template>
  <el-dialog title="选择知识库" v-model="dialogVisible" width="600" class="select-dataset-dialog">
    <template #header="{ titleId, titleClass }">
      <div class="my-header flex">
        <h4 :id="titleId" :class="titleClass">选择知识库</h4>
        <el-button link class="ml-16" @click="refresh">
          <el-icon class="mr-4"><Refresh /></el-icon>刷新
        </el-button>
      </div>
    </template>
    <div class="content-height">
      <el-radio-group v-model="selectDataset" class="card__radio">
        <el-scrollbar height="500">
          <div class="p-16">
            <el-row :gutter="12" v-loading="loading">
              <el-col :span="12" v-for="(item, index) in datasetList" :key="index" class="mb-16">
                <el-card
                  shadow="never"
                  class="mb-8"
                  :class="item.id === selectDataset ? 'active' : ''"
                >
                  <el-radio :value="item.id" size="large">
                    <div class="flex align-center">
                      <AppAvatar
                        v-if="item?.type === '0'"
                        class="mr-8 avatar-blue"
                        shape="square"
                        :size="32"
                      >
                        <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                      </AppAvatar>
                      <AppAvatar
                        v-if="item?.type === '1'"
                        class="mr-8 avatar-purple"
                        shape="square"
                        :size="32"
                      >
                        <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                      </AppAvatar>
                      <span class="ellipsis">
                        {{ item.name }}
                      </span>
                    </div>
                  </el-radio>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-scrollbar>
      </el-radio-group>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submitHandle" :disabled="!selectDataset || loading">
          确认
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import documentApi from '@/api/document'

import useStore from '@/stores'
const { dataset } = useStore()
const route = useRoute()
const {
  params: { id } // id为datasetID
} = route as any

const emit = defineEmits(['refresh'])

const loading = ref<boolean>(false)

const dialogVisible = ref<boolean>(false)
const selectDataset = ref('')
const datasetList = ref<any>([])
const documentList = ref<any>([])

watch(dialogVisible, (bool) => {
  if (!bool) {
    selectDataset.value = ''
    datasetList.value = []
    documentList.value = []
  }
})

const open = (list: any) => {
  documentList.value = list
  getDataset()
  dialogVisible.value = true
}
const submitHandle = () => {
  documentApi
    .putMigrateMulDocument(id, selectDataset.value, documentList.value, loading)
    .then((res) => {
      emit('refresh')
      dialogVisible.value = false
    })
}

function getDataset() {
  dataset.asyncGetAllDataset(loading).then((res: any) => {
    datasetList.value = res.data?.filter((v: any) => v.id !== id)
  })
}

const refresh = () => {
  getDataset()
}

defineExpose({ open })
</script>
<style lang="scss" scope>
.select-dataset-dialog {
  padding: 0;
  .el-dialog__header {
    padding: 24px 24px 0 24px;
  }
  .el-dialog__body {
    padding: 8px !important;
  }
  .el-dialog__footer {
    padding: 0 24px 24px;
  }
}
</style>
