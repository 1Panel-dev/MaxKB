<template>
  <LayoutContainer class="knowledge-manage">
    <template #left>
      <div class="p-8"></div>
    </template>
    <ContentContainer>
      <div class="flex-between mb-16">
        <h4>{{ $t('views.knowledge.title') }}</h4>
        <div class="flex-between"></div>
      </div>
      <div>
        <el-row v-if="datasetList.length > 0" :gutter="15">
          <template v-for="(item, index) in datasetList" :key="index">
            <el-col :xs="24" :sm="12" :md="12" :lg="8" :xl="6" class="mb-16">
              <CardBox :title="item.name" :description="item.desc" class="cursor">
                <template #icon>
                  <el-avatar
                    v-if="item.type === '1'"
                    class="mr-8 avatar-purple"
                    shape="square"
                    :size="32"
                  >
                    <img src="@/assets/knowledge/icon_web.svg" style="width: 58%" alt="" />
                  </el-avatar>
                  <el-avatar
                    v-else-if="item.type === '2'"
                    class="mr-8 avatar-purple"
                    shape="square"
                    :size="32"
                    style="background: none"
                  >
                    <img src="@/assets/knowledge/logo_lark.svg" style="width: 100%" alt="" />
                  </el-avatar>
                  <el-avatar v-else class="mr-8 avatar-blue" shape="square" :size="32">
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

const datasetList = ref<any[]>([])
const folderId = ref<string>('root')

function getList() {
  const params = {
    folder_id: folderId.value,
  }
  KnowledgeApi.getKnowledgeList('default', paginationConfig, params, loading).then((res) => {
    paginationConfig.total = res.data.total
    datasetList.value = [...datasetList.value, ...res.data.records]
  })
}

function getFolder() {
  const params = {}
  folder.asynGetFolder('default', 'KNOWLEDGE', params, loading).then((res) => {
    // paginationConfig.total = res.data.total
    // datasetList.value = [...datasetList.value, ...res.data.records]
  })
}

onMounted(() => {
  getFolder()
  getList()
})
</script>

<style lang="scss" scoped></style>
