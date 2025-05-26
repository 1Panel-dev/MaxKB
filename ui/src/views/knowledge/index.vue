<template>
  <LayoutContainer class="knowledge-manage">
    <template #left>
      <h4 class="p-16 pb-0">{{ $t('views.knowledge.title') }}</h4>
      <folder-tree
        :data="folderList"
        :currentNodeKey="currentFolder?.id"
        @handleNodeClick="folderClickHandel"
      />
    </template>
    <ContentContainer>
      <div class="flex-between mb-16">
        <h4>{{ currentFolder?.name }}</h4>
        <div class="flex-between"></div>
      </div>
      <div>
        <el-row v-if="datasetList.length > 0 || datasetFolderList.length > 0" :gutter="15">
          <template v-for="(item, index) in datasetFolderList" :key="index">
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
          </template>
          <template v-for="(item, index) in datasetList" :key="index">
            <el-col :xs="24" :sm="12" :md="12" :lg="8" :xl="6" class="mb-16">
              <CardBox :title="item.name" :description="item.desc" class="cursor">
                <template #icon>
                  <el-avatar
                    v-if="item.type === '1'"
                    class="avatar-purple"
                    shape="square"
                    :size="32"
                  >
                    <img src="@/assets/knowledge/icon_web.svg" style="width: 58%" alt="" />
                  </el-avatar>
                  <el-avatar
                    v-else-if="item.type === '2'"
                    class="avatar-purple"
                    shape="square"
                    :size="32"
                    style="background: none"
                  >
                    <img src="@/assets/knowledge/logo_lark.svg" style="width: 100%" alt="" />
                  </el-avatar>
                  <el-avatar v-else class="avatar-blue" shape="square" :size="32">
                    <img src="@/assets/knowledge/icon_document.svg" style="width: 58%" alt="" />
                  </el-avatar>
                </template>
                <template #subTitle>
                  <el-text class="color-secondary" size="small">
                    <auto-tooltip :content="item.username">
                      {{ $t('common.creator') }}: {{ item.username }}
                    </auto-tooltip>
                  </el-text>
                </template>

                <template #footer>
                  <div class="footer-content flex-between">
                    <div>
                      <span class="bold mr-4">{{ item?.document_count || 0 }}</span>
                      <span class="color-secondary">{{
                        $t('views.knowledge.document_count')
                      }}</span>
                      <el-divider direction="vertical" />
                      <span class="bold mr-4">{{ numberFormat(item?.char_length) || 0 }}</span>
                      <span class="color-secondary">{{ $t('common.character') }}</span
                      ><el-divider direction="vertical" />
                      <span class="bold mr-4">{{ item?.application_mapping_count || 0 }}</span>
                      <span class="color-secondary">{{
                        $t('views.knowledge.relatedApp_count')
                      }}</span>
                    </div>
                  </div>
                </template>
              </CardBox>
            </el-col>
          </template>
        </el-row>
        <el-empty :description="$t('common.noData')" v-else />
      </div>
    </ContentContainer>
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, computed } from 'vue'
import KnowledgeApi from '@/api/knowledge/knowledge'
import useStore from '@/stores'
import { numberFormat } from '@/utils/common'
import { t } from '@/locales'

const { folder } = useStore()
const loading = ref(false)
const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0,
})

const folderList = ref<any[]>([])
const datasetList = ref<any[]>([])
const datasetFolderList = ref<any[]>([])
const currentFolder = ref<any>({})

function getList() {
  const params = {
    folder_id: currentFolder.value?.id || 'root',
  }
  KnowledgeApi.getKnowledgeList('default', paginationConfig, params, loading).then((res) => {
    datasetFolderList.value = res.data?.folders
    paginationConfig.total = res.data.total
    datasetList.value = [...datasetList.value, ...res.data.knowledge.records]
  })
}

function getFolder() {
  const params = {}
  folder.asynGetFolder('default', 'KNOWLEDGE', params, loading).then((res: any) => {
    folderList.value = res.data
    currentFolder.value = res.data?.[0] || {}
    getList()
  })
}

function folderClickHandel(row: any) {
  // currentFolder.value = row
  // toolList.value = []
  // getList()
}

onMounted(() => {
  getFolder()
})
</script>

<style lang="scss" scoped></style>
