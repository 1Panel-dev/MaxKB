<template>
  <LayoutContainer :header="$t('views.document.importDocument')" class="create-dataset">
    <template #backButton>
      <back-button @click="back"></back-button>
    </template>
    <div class="create-dataset__main flex" v-loading="loading">
      <div class="create-dataset__component main-calc-height">
        <div class="upload-document p-24" style="min-width: 850px">
          <h4 class="title-decoration-1 mb-8">
            {{ $t('views.document.feishu.selectDocument') }}
          </h4>
          <el-form
            ref="FormRef"
            :model="form"
            :rules="rules"
            label-position="top"
            require-asterisk-position="right"
          >
            <div class="mt-16 mb-16">
              <el-radio-group v-model="form.fileType" class="app-radio-button-group">
                <el-radio-button value="txt"
                  >{{ $t('views.document.fileType.txt.label') }}
                </el-radio-button>
              </el-radio-group>
            </div>
            <div class="update-info flex p-8-12 border-r-4 mb-16">
              <div class="mt-4">
                <AppIcon iconName="app-warning-colorful" style="font-size: 16px"></AppIcon>
              </div>
              <div class="ml-16 lighter">
                <p>{{ $t('views.document.feishu.tip1') }}</p>
                <p>{{ $t('views.document.feishu.tip2') }}</p>
              </div>
            </div>
            <div class="card-never border-r-4 mb-16">
              <el-checkbox
                v-model="allCheck"
                :label="$t('views.document.feishu.allCheck')"
                size="large"
                class="ml-24"
                @change="handleAllCheckChange"
              />
            </div>
            <div style="height: calc(100vh - 450px)">
              <el-scrollbar>
                <el-tree
                  :props="props"
                  :load="loadNode"
                  lazy
                  show-checkbox
                  node-key="token"
                  ref="treeRef"
                >
                  <template #default="{ node, data }">
                    <div class="custom-tree-node flex align-center lighter">
                      <img
                        src="@/assets/fileType/file-icon.svg"
                        alt=""
                        height="20"
                        v-if="data.type === 'folder'"
                      />
                      <img
                        src="@/assets/fileType/docx-icon.svg"
                        alt=""
                        height="22"
                        v-else-if="data.type === 'docx' || data.name.endsWith('.docx')"
                      />
                      <img
                        src="@/assets/fileType/xlsx-icon.svg"
                        alt=""
                        height="22"
                        v-else-if="data.type === 'sheet' || data.name.endsWith('.xlsx')"
                      />
                      <img
                        src="@/assets/fileType/xls-icon.svg"
                        alt=""
                        height="22"
                        v-else-if="data.name.endsWith('xls')"
                      />
                      <img
                        src="@/assets/fileType/csv-icon.svg"
                        alt=""
                        height="22"
                        v-else-if="data.name.endsWith('csv')"
                      />
                      <img
                        src="@/assets/fileType/pdf-icon.svg"
                        alt=""
                        height="22"
                        v-else-if="data.name.endsWith('.pdf')"
                      />
                      <img
                        src="@/assets/fileType/html-icon.svg"
                        alt=""
                        height="22"
                        v-else-if="data.name.endsWith('.html')"
                      />
                      <img
                        src="@/assets/fileType/txt-icon.svg"
                        alt=""
                        height="22"
                        v-else-if="data.name.endsWith('.txt')"
                      />
                      <img
                        src="@/assets/fileType/zip-icon.svg"
                        alt=""
                        height="22"
                        v-else-if="data.name.endsWith('.zip')"
                      />
                      <img
                        src="@/assets/fileType/md-icon.svg"
                        alt=""
                        height="22"
                        v-else-if="data.name.endsWith('.md')"
                      />

                      <span class="ml-4">{{ node.label }}</span>
                    </div>
                  </template>
                </el-tree>
              </el-scrollbar>
            </div>
          </el-form>
        </div>
      </div>
    </div>
    <div class="create-dataset__footer text-right border-t">
      <el-button @click="router.go(-1)">{{ $t('common.cancel') }}</el-button>

      <el-button @click="submit" type="primary" :disabled="disabled">
        {{ $t('views.document.buttons.import') }}
      </el-button>
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, reactive, computed, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { MsgConfirm, MsgSuccess, MsgWarning } from '@/utils/message'
import { getImgUrl } from '@/utils/utils'
import { t } from '@/locales'
import type Node from 'element-plus/es/components/tree/src/model/node'
import dataset from '@/api/dataset'

const router = useRouter()
const route = useRoute()
const {
  query: { id, folder_token } // id为datasetID，有id的是上传文档 folder_token为飞书文件夹token
} = route
const datasetId = id as string
const folderToken = folder_token as string

const loading = ref(false)
const disabled = ref(false)
const allCheck = ref(false)
const treeRef = ref<any>(null)

interface Tree {
  name: string
  leaf?: boolean
  type: string
  token: string
  is_exist: boolean
}

const form = ref({
  fileType: 'txt',
  fileList: [] as any
})

const rules = reactive({
  fileList: [
    { required: true, message: t('views.document.upload.requiredMessage'), trigger: 'change' }
  ]
})

const props = {
  label: 'name',
  children: 'zones',
  isLeaf: (data: any) => data.type !== 'folder',
  disabled: (data: any) => data.is_exist
}

const loadNode = (node: Node, resolve: (nodeData: Tree[]) => void) => {
  const token = node.level === 0 ? folderToken : node.data.token // 根节点使用 folder_token，其他节点使用 node.data.token
  dataset
    .getLarkDocumentList(datasetId, token, {}, loading)
    .then((res: any) => {
      const nodes = res.data.files as Tree[]
      resolve(nodes)
      nodes.forEach((childNode) => {
        if (childNode.is_exist) {
          treeRef.value?.setChecked(childNode.token, true, false)
        }
      })
    })

    .catch((err) => {
      console.error('Failed to load tree nodes:', err)
    })
}

const handleAllCheckChange = (checked: boolean) => {
  if (checked) {
    // 获取所有已加载的节点
    const nodes = Object.values(treeRef.value?.store.nodesMap || {}) as any[]
    nodes.forEach((node) => {
      // 只选择未禁用且是文件的节点
      if (!node.disabled) {
        treeRef.value?.setChecked(node.data, true, false)
      }
    })
  } else {
    treeRef.value?.setCheckedKeys([])
  }
}

function submit() {
  loading.value = true
  disabled.value = true
  // 选中的节点的token
  const checkedNodes = treeRef.value?.getCheckedNodes() || []
  const filteredNodes = checkedNodes.filter((node: any) => !node.is_exist)
  const newList = filteredNodes.map((node: any) => {
    return {
      name: node.name,
      token: node.token,
      type: node.type
    }
  })
  if (newList.length === 0) {
    disabled.value = false
    MsgWarning(t('views.document.feishu.errorMessage1'))
    loading.value = false
    return
  }
  dataset
    .importLarkDocument(datasetId, newList, loading)
    .then((res) => {
      MsgSuccess(t('views.document.tip.importMessage'))
      disabled.value = false
      router.go(-1)
    })
    .catch((err) => {
      console.error('Failed to load tree nodes:', err)
    })
    .finally(() => {
      disabled.value = false
    })
  loading.value = false
}

function back() {
  router.go(-1)
}
</script>
<style lang="scss" scoped>
.create-dataset {
  &__component {
    width: 100%;
    margin: 0 auto;
    overflow: hidden;
  }

  &__footer {
    padding: 16px 24px;
    position: fixed;
    bottom: 0;
    left: 0;
    background: #ffffff;
    width: 100%;
    box-sizing: border-box;
  }

  .upload-document {
    width: 70%;
    margin: 0 auto;
    margin-bottom: 20px;
  }
}

.xlsx-icon {
  svg {
    width: 24px;
    height: 24px;
    stroke: #000000 !important;
    fill: #ffffff !important;
  }
}
</style>
