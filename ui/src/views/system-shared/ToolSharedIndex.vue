<template>
  <div class="tool-shared">
    <ToolListContainer>
      <template #header>
        <el-space wrap>
          <el-breadcrumb separator-icon="ArrowRight">
            <el-breadcrumb-item>{{ $t('views.shared.shared_resources') }}</el-breadcrumb-item>
            <el-breadcrumb-item>
              <h5 class="ml-4 color-text-primary">{{ $t('views.tool.title') }}</h5>
            </el-breadcrumb-item>
          </el-breadcrumb>
          <el-divider direction="vertical" />
          <el-radio-group v-model="toolType" @change="radioChange" class="app-radio-button-group">
            <el-radio-button value="">{{ $t('views.tool.all') }}</el-radio-button>
            <el-radio-button value="CUSTOM">{{ $t('views.tool.title') }}</el-radio-button>
            <el-radio-button value="MCP">MCP</el-radio-button>
            <el-radio-button value="DATA_SOURCE">{{ $t('views.tool.dataSource.title') }}</el-radio-button>
          </el-radio-group>
        </el-space>
      </template>
    </ToolListContainer>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, computed } from 'vue'

import ToolListContainer from '@/views/tool/component/ToolListContainer.vue'

import useStore from '@/stores'

const { tool } = useStore()

const toolType = ref('')

function radioChange() {
  tool.setToolType(toolType.value)
}

onMounted(() => {})
</script>

<style lang="scss" scoped></style>
