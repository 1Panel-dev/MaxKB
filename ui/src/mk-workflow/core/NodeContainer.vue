<script setup lang="ts">
import { ArrowDownBold, CopyDocument, Delete, Edit, MoreFilled } from '@element-plus/icons-vue'
import type { Model } from '@logicflow/core'
import type { FormInstance } from 'element-plus'
import WorkflowNodeMenu from '@/mk-workflow/extension/WorkflowNodeMenu.vue'
import type { AppNodeModel } from '@/mk-workflow/core/app-node'
import { BasicComponentsNode, type WorkflowField } from '@/mk-workflow/core/data'
import { iconComponent } from '@/mk-workflow/icons/utils'
import { WorkflowNodeType } from '@/mk-workflow/types'
import { copyText } from '@/utils/clipboard'
import { MsgConfirm, MsgError } from '@/utils/message'

defineOptions({ name: 'WorkflowNodeContainer' })

const props = defineProps<{ nodeModel: AppNodeModel }>()
const nodeModel = props.nodeModel

const titleFormRef = useTemplateRef<FormInstance>('titleFormRef')
const showNode = ref(nodeModel.properties.showNode ?? true)
const showAnchor = ref(false)
const anchorData = ref<Model.AnchorConfig>()
const nodeNameDialogVisible = ref(false)
const nodeNameForm = reactive({ title: '' })

const isFixedNode = computed(() =>
  [WorkflowNodeType.Base, WorkflowNodeType.Start].includes(
    String(nodeModel.type) as WorkflowNodeType,
  ),
)
const nodeFields = computed(
  () => (nodeModel.properties.config?.fields ?? []) as unknown as WorkflowField[],
)
const menuStyle = computed(() => ({
  top: anchorData.value ? `${anchorData.value.y - nodeModel.y + nodeModel.height / 2}px` : '0',
}))

function toggleNode() {
  showNode.value = !showNode.value
  nodeModel.properties.showNode = showNode.value
}

function openRenameDialog() {
  nodeNameForm.title = String(nodeModel.properties.stepName ?? '')
  nodeNameDialogVisible.value = true
}

function saveNodeName() {
  titleFormRef.value?.validate((valid) => {
    if (!valid) return
    const nodeName = nodeNameForm.title.trim()
    const duplicated = nodeModel.graphModel.nodes.some(
      (node) => node.id !== nodeModel.id && node.properties.stepName?.trim() === nodeName,
    )
    if (duplicated) {
      MsgError('节点名称已存在')
      return
    }
    nodeModel.properties.stepName = nodeName
    nodeNameDialogVisible.value = false
  })
}

function copyNode() {
  const clonedNode = nodeModel.graphModel.cloneNode(nodeModel.id)
  if (clonedNode) copyText(JSON.stringify(clonedNode), '节点已复制')
}

function deleteNode() {
  MsgConfirm('删除节点', '确定删除该节点？').then(() => {
    nodeModel.graphModel.deleteNode(nodeModel.id)
  })
}

function copyField(field: { value: string }) {
  copyText(`{{${nodeModel.properties.stepName}.${field.value}}}`)
}

function formatFieldReference(fieldValue: string) {
  return `{${fieldValue}}`
}

function closeNodeMenu() {
  showAnchor.value = false
  anchorData.value = undefined
}

function addConnectedNode(nodeType: WorkflowNodeType) {
  const definition = BasicComponentsNode[nodeType]
  if (!definition || !anchorData.value) return

  const addedNode = nodeModel.graphModel.addNode({
    type: definition.type,
    properties: structuredClone({ ...definition.properties, height: definition.height }),
    x: anchorData.value.x + 400,
    y: anchorData.value.y,
  })
  nodeModel.graphModel.addEdge({
    type: 'app-edge',
    sourceNodeId: nodeModel.id,
    sourceAnchorId: anchorData.value.id,
    targetNodeId: addedNode.id,
    targetAnchorId: `${addedNode.id}_left`,
  })
  closeNodeMenu()
}

function handleWheel(event: WheelEvent) {
  if (event.ctrlKey) event.preventDefault()
  else event.stopPropagation()
}

const height = ref<{
  stepContainerHeight: number
  inputContainerHeight: number
  outputContainerHeight: number
}>({
  stepContainerHeight: 0,
  inputContainerHeight: 0,
  outputContainerHeight: 0,
})
const resizeStepContainer = (wh: any) => {
  if (wh.height) {
    if (!props.nodeModel.virtual) {
      height.value.stepContainerHeight = wh.height
      props.nodeModel.setHeight(height.value.stepContainerHeight)
    }
  }
}

onMounted(() => {
  nodeModel.openNodeMenu = (nextAnchorData: Model.AnchorConfig) => {
    if (showAnchor.value) closeNodeMenu()
    else {
      anchorData.value = nextAnchorData
      showAnchor.value = true
    }
  }
})

</script>

<template>
  <div class="p-4" @mousedown="nodeModel.setSelected(true)" style="overflow: visible">
    <div
      class="step-container bg-white w-full rounded-lg p-4"
      :class="nodeModel.isSelected ? 'border-primary' : 'border'"
      style="overflow: visible"
    >
      <div ref="contentRef" v-resize="resizeStepContainer">
        <div class="flex-between gap-3">
          <div class="flex min-w-0 items-center gap-2">
            <component :is="iconComponent(`${nodeModel.type}-icon`)" class="size-6 shrink-0" />
            <h6 class="truncate" :title="nodeModel.properties.stepName">
              {{ nodeModel.properties.stepName }}
            </h6>
          </div>

          <div class="flex shrink-0 items-center" @mousedown.stop @click.stop>
            <el-button text @click="toggleNode">
              <MkIcon
                :icon="ArrowDownBold"
                class="transition-transform"
                :class="showNode ? 'rotate-180' : ''"
              />
            </el-button>
            <el-dropdown v-if="!isFixedNode" :teleported="false" trigger="click">
              <el-button text><MkIcon :icon="MoreFilled" /></el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="openRenameDialog">
                    <MkIcon :icon="Edit" />重命名
                  </el-dropdown-item>
                  <el-dropdown-item @click="copyNode">
                    <MkIcon :icon="CopyDocument" />复制
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="deleteNode">
                    <MkIcon :icon="Delete" />删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <el-collapse-transition>
          <div v-show="showNode" class="mt-4" @mousedown.stop @click.stop @keydown.stop>
            <slot />

            <template v-if="nodeFields.length">
              <h6 class="mb-2 mt-4">输出参数</h6>
              <div class="rounded-md bg-N100 px-3 py-1 text-N600">
                <div
                  v-for="field in nodeFields"
                  :key="field.value"
                  class="flex items-center justify-between gap-2 py-2"
                >
                  <span>{{ field.label }} {{ formatFieldReference(field.value) }}</span>
                  <el-button link @click="copyField(field)">
                    <MkIcon :icon="CopyDocument" />
                  </el-button>
                </div>
              </div>
            </template>
          </div>
        </el-collapse-transition>
      </div>
    </div>

    <el-collapse-transition>
      <WorkflowNodeMenu
        v-if="showAnchor"
        class="absolute left-full z-[2000] -translate-y-1/2"
        :style="menuStyle"
        @select="addConnectedNode"
        @wheel="handleWheel"
      />
    </el-collapse-transition>

    <MkDialog v-model="nodeNameDialogVisible" title="节点名称" width="480">
      <el-form ref="titleFormRef" :model="nodeNameForm" label-position="top">
        <el-form-item
          label="名称"
          prop="title"
          :rules="{ required: true, message: '请输入节点名称', trigger: 'blur' }"
        >
          <el-input v-model="nodeNameForm.title" maxlength="64" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="nodeNameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNodeName">保存</el-button>
      </template>
    </MkDialog>
  </div>
</template>
<style lang="scss" scoped>
.step-container {
  box-sizing: border-box;
  &:hover {
  }
  &.isSelected {
    border: 2px solid var(--el-color-primary) !important;
  }
  &.error {
    border: 1px solid #f54a45 !important;
  }
}

:deep(.el-card) {
  overflow: visible;
}
.app-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0px 2px 4px 0px rgba(31, 35, 41, 0.12);
}
</style>
