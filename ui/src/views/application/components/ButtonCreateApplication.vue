<script setup lang="ts">
import { computed, ref, useTemplateRef, type CSSProperties } from 'vue'
import type { UploadFile, UploadInstance } from 'element-plus'
import ApplicationApi from '@/api/admin/workspace/application/application'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import AdvancedCreateDialog from '@/views/application/create-application/AdvancedCreateDialog.vue'
import SimpleCreateDialog from '@/views/application/create-application/SimpleCreateDialog.vue'

defineOptions({ name: 'CreateApplicationDropdown' })

const { auth } = useStore()

const props = withDefaults(
  defineProps<{
    folderId: string
    trigger?: 'click' | 'hover' | 'contextmenu'
    popperStyle?: CSSProperties
    popperClass?: string
    fitTriggerWidth?: boolean
  }>(),
  { trigger: 'click', fitTriggerWidth: false },
)

const emit = defineEmits<{ refresh: [] }>()

defineSlots<{
  /** 创建菜单触发器，只能渲染一个有效根节点 */
  trigger?(): unknown
}>()

/* 自定义触发卡片与菜单等宽 */
const triggerRef = useTemplateRef<HTMLDivElement>('triggerRef')
const dropdownWidth = ref<number>()
const dropdownStyle = computed(() => ({
  ...props.popperStyle,
  ...(props.fitTriggerWidth && dropdownWidth.value ? { width: `${dropdownWidth.value}px` } : {}),
}))
const customDropdownWidth = computed(() => props.fitTriggerWidth || !!props.popperStyle?.width || !!props.popperClass)

function handleVisibleChange(visible: boolean) {
  if (visible && props.fitTriggerWidth) {
    dropdownWidth.value = triggerRef.value?.getBoundingClientRect().width
  }
}

/* 智能体创建表单 */
const simpleCreateDialogRef = useTemplateRef<InstanceType<typeof SimpleCreateDialog>>('simpleCreateDialogRef')
const advancedCreateDialogRef = useTemplateRef<InstanceType<typeof AdvancedCreateDialog>>('advancedCreateDialogRef')

function handleOpenSimpleApplicationCreate() {
  simpleCreateDialogRef.value?.open()
}

function handleOpenAdvancedApplicationCreate() {
  advancedCreateDialogRef.value?.open()
}

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
  <MkDropdown
    :trigger="trigger"
    placement="bottom-end"
    persistent
    :class="{ 'w-full': $slots.trigger }"
    :popper-style="dropdownStyle"
    :popper-class="popperClass"
    @visible-change="handleVisibleChange"
  >
    <div v-if="$slots.trigger" ref="triggerRef" class="w-full cursor-pointer">
      <slot name="trigger" />
    </div>
    <!-- 创建智能体 -->
    <el-button v-else type="primary">
      <span class="mr-1">创建</span>
      <MkIcon name="icon_down_outlined" :size="14" />
    </el-button>

    <template #dropdown>
      <MkDropdownMenu :class="[popperClass, customDropdownWidth ? 'w-full!' : 'w-77!']">
        <MkDropdownItem class="py-2! items-start!" @click="handleOpenSimpleApplicationCreate">
          <template #icon>
            <el-avatar shape="square" :size="24" class="mt-2">
              <img style="width: 65%" src="@/assets/application/icon_simple_application.svg" alt="" />
            </el-avatar>
          </template>
          <div class="min-w-0">
            <p>简易智能体</p>
            <p class="text-sm text-N500 whitespace-normal">通过表单设置方式，快速搭建基础功能的智能体</p>
          </div>
        </MkDropdownItem>
        <MkDropdownItem class="py-2! items-start!" @click="handleOpenAdvancedApplicationCreate">
          <template #icon>
            <el-avatar shape="square" class="bg-warning! mt-2" :size="24">
              <img style="width: 65%" src="@/assets/application/icon_workflow_application.svg" alt="" />
            </el-avatar>
          </template>
          <div class="min-w-0">
            <p class="leading-5">高级智能体</p>
            <p class="text-sm text-N500 whitespace-normal">使用低代码拖拉拽方式，灵活编排复杂逻辑、功能丰富的智能体</p>
          </div>
        </MkDropdownItem>
        <MkDropdownItem class="py-2!" @click="handleOpenAdvancedApplicationCreate">
          <template #icon>
            <el-avatar class="ai-avatar-gradient" shape="square" :size="24">
              <img src="@/assets/workflow/icon_ai_chat.svg" style="width: 75%" alt="" />
            </el-avatar>
          </template>
          <div class="min-w-0">
            <p class="leading-5">AI 创建</p>
            <p class="text-sm text-N500 whitespace-normal">根据描述，AI 自动生成工作流</p>
          </div>
        </MkDropdownItem>

        <el-upload
          ref="elUploadRef"
          action="#"
          :auto-upload="false"
          class="mk-import-button"
          :file-list="[]"
          :limit="1"
          :on-change="handleImportCreate"
          :show-file-list="false"
        >
          <MkDropdownItem class="w-full py-2!">
            <template #icon>
              <img class="size-7" src="@/assets/mk_icon_import.svg" alt="" />
            </template>
            <span>导入创建</span>
          </MkDropdownItem>
        </el-upload>
      </MkDropdownMenu>
    </template>
  </MkDropdown>

  <SimpleCreateDialog ref="simpleCreateDialogRef" :folder-id="folderId" />
  <AdvancedCreateDialog ref="advancedCreateDialogRef" :folder-id="folderId" />
</template>
