<script setup lang="ts">
import { ref } from 'vue'
import AvatarDropdown from './avatar-dropdown/index.vue'
import MKFilterableDropdown from '@/components/mk-filterable-dropdown/index.vue'
import { ArrowDown, Collection, Setting } from '@element-plus/icons-vue'
import { isWorkspace, isSystem } from '@/router/admin/utils'
import type { LayoutMode } from './types'
const router = useRouter()
const currentWorkspace = ref<string | number>('maxkb')
const workspaceOptions = [
  { label: 'MaxKB 工作空间工作空间', value: 'maxkb-default' },
  { label: 'MaxKB 工作空间', value: 'maxkb' },
  { label: 'MaxKB 工作空间 1', value: 'maxkb-1' },
  { label: 'MaxKB 工作空间 2', value: 'maxkb-2' },
  { label: '工作空间名称比较长的展示效果如下', value: 'long-name' },
  { label: '研发工作空间', value: 'development' },
  { label: '测试工作空间', value: 'testing' },
]
const props = withDefaults(
  defineProps<{
    mode?: LayoutMode
  }>(),
  {
    mode: 'workspace',
  },
)
function switchMode() {
  router.push({ name: isWorkspace(props.mode) ? 'system-users' : 'workspace-home' })
}
</script>

<template>
  <header class="flex h-header items-center justify-between px-6">
    <div class="flex items-center">
      <img src="@/assets/logo/MaxKB-logo.svg" style="height: 36px" />
      <div class="flex items-center gap-5 ml-5">
        <el-divider direction="vertical" />
        <!-- 企业版: 工作空间下拉框 -->
        <MKFilterableDropdown
          v-if="isWorkspace(mode)"
          v-model="currentWorkspace"
          :options="workspaceOptions"
          placeholder="请选择工作空间"
        >
          <template #default="{ text }">
            <button type="button" class="flex max-w-50 items-center gap-1 rounded-md px-2 py-1">
              <MkIcon :icon="Collection" />
              <span class="truncate">{{ text }}</span>
              <MkIcon :icon="ArrowDown" class="shrink-0" />
            </button>
          </template>
          <template #itemIcon>
            <MkIcon :icon="Collection" />
          </template>
        </MKFilterableDropdown>
        <span v-if="isSystem(mode)" class="text-lg">系统管理</span>
      </div>
    </div>

    <div class="flex items-center gap-5">
      <el-button class="bg-primary-gradient" round>
        <MkIcon name="icon_start_outlined" :size="16" />
        <span>升级</span>
      </el-button>
      <el-divider direction="vertical" />
      <el-button v-if="isWorkspace(mode)" class="-mx-1" text @click="switchMode">
        <MkIcon :icon="Setting" />
        <span>系统管理</span>
      </el-button>
      <el-button v-if="isSystem(mode)" class="-mx-1" text @click="switchMode">
        <MkIcon name="icon_left_outlined" :size="16" />
        <span>返回工作空间</span>
      </el-button>
      <AvatarDropdown> <!-- 头像  --> </AvatarDropdown>
    </div>
  </header>
</template>
