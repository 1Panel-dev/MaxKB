<script setup lang="ts">
import { ref } from 'vue'
import type { UploadFile, UploadInstance } from 'element-plus'
import ApplicationApi from '@/api/admin/workspace/application/application'
import { APPLICATION_TYPE } from '@/api/enums'
import type { ApplicationType } from '@/api/types'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'ApplicationCreateDropdown' })

const { auth } = useStore()

const props = defineProps<{ folderId: string }>()

const emit = defineEmits<{ create: [type: ApplicationType]; refresh: [] }>()

defineSlots<{
  /** 创建菜单触发器，只能渲染一个有效根节点 */
  trigger?(): unknown
}>()

/* 导入创建 */
const elUploadRef = ref<UploadInstance>()
function handleImportCreate(file: UploadFile) {
  if (!file.raw) return
  ApplicationApi.postApplicationImport(file.raw, props.folderId)
    .then(() => {
      return auth.loadAuthBaseProfile().then(() => {
        MsgSuccess('导入成功')
        handleRefresh()
      })
    })
    .finally(() => {
      elUploadRef.value?.clearFiles()
    })
}

// 发送刷新列表
function handleRefresh() {
  emit('refresh')
}
</script>

<template>
  <MkDropdown trigger="click" placement="bottom-end" persistent>
    <slot name="trigger">
      <el-button type="primary">
        <span class="mr-1">创建</span>
        <MkIcon name="icon_down_outlined" :size="14" />
      </el-button>
    </slot>

    <template #dropdown>
      <MkDropdownMenu class="w-77!">
        <MkDropdownItem class="py-2!">
          <template #icon>
            <el-avatar shape="square" :size="24">
              <img style="width: 65%" src="@/assets/application/icon_simple_application.svg" alt="" />
            </el-avatar>
          </template>
          <div class="min-w-0">
            <p>简易智能体</p>
            <p class="text-sm text-N500">通过表单设置方式，快速搭建基础功能的智能体</p>
          </div>
        </MkDropdownItem>
        <MkDropdownItem class="py-2!">
          <template #icon>
            <el-avatar shape="square" class="bg-warning! -mt-5!" :size="24">
              <img style="width: 65%" src="@/assets/application/icon_workflow_application.svg" alt="" />
            </el-avatar>
          </template>
          <div class="min-w-0">
            <p class="leading-5">高级智能体</p>
            <p class="whitespace-normal text-sm text-N500">使用低代码拖拉拽方式，灵活编排复杂逻辑、功能丰富的智能体</p>
          </div>
        </MkDropdownItem>
        <el-upload ref="elUploadRef" action="#" :auto-upload="false" class="w-full" :file-list="[]" :limit="1" :on-change="handleImportCreate" :show-file-list="false">
          <MkDropdownItem class="py-2!">
            <template #icon>
              <img class="size-7" src="@/assets/mk_icon_import.svg" alt="" />
            </template>
            <span>导入创建</span>
          </MkDropdownItem>
        </el-upload>
      </MkDropdownMenu>
    </template>
  </MkDropdown>
</template>
