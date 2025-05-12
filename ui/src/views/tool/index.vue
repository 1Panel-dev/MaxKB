<template>
  <LayoutContainer class="tool-manage">
    <template #left>
      <h4 class="p-8">{{ $t('views.tool.title') }}</h4>
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
        <el-row v-if="toolList.length > 0" :gutter="15">
          <template v-for="(item, index) in toolList" :key="index">
            <el-col :xs="24" :sm="12" :md="12" :lg="8" :xl="6" class="mb-16">
              <CardBox :title="item.name" :description="item.desc" class="cursor">
                <template #icon>
                  <el-avatar class="mr-8 avatar-green" shape="square" :size="32">
                    <img src="@/assets/node/icon_tool.svg" style="width: 58%" alt="" />
                  </el-avatar>
                </template>
                <template #subTitle>
                  <el-text class="color-secondary" size="small">
                    <auto-tooltip :content="item.username">
                      {{ $t('common.creator') }}: {{ item.username }}
                    </auto-tooltip>
                  </el-text>
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
import ToolApi from '@/api/tool/tool'
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
const toolList = ref<any[]>([])
const currentFolder = ref<any>({})

function getList() {
  const params = {
    folder_id: currentFolder.value?.id || 'root',
    tool_type: 'CUSTOM',
  }
  ToolApi.getToolList('default', paginationConfig, params, loading).then((res) => {
    paginationConfig.total = res.data.total
    toolList.value = [...toolList.value, ...res.data.records]
  })
}

function getFolder() {
  const params = {}
  folder.asynGetFolder('default', 'TOOL', params, loading).then((res: any) => {
    folderList.value = res.data
    currentFolder.value = res.data?.[0] || {}
    getList()
  })
}

onMounted(() => {
  getFolder()
})
</script>

<style lang="scss" scoped></style>
