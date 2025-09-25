<template>
  <div @mousedown="mousedown" class="workflow-node-container p-16" style="overflow: visible">
    <div
      class="step-container app-card p-16"
      :class="{ isSelected: props.nodeModel.isSelected, error: node_status !== 200 }"
      style="overflow: visible"
    >
      <div v-resize="resizeStepContainer">
        <div class="flex-between">
          <div
            class="flex align-center"
            @dragstart.prevent
            @drag.prevent
            @dragover.prevent
            @dragend.prevent
            style="width: 69%"
          >
            <component
              :is="iconComponent(`${nodeModel.type}-icon`)"
              class="mr-8"
              :size="24"
              :item="nodeModel?.properties.node_data"
            />
            <h4 class="ellipsis-1 break-all">{{ nodeModel.properties.stepName }}</h4>
          </div>

          <div @mousemove.stop @mousedown.stop @keydown.stop @click.stop>
            <el-button text @click="showNode = !showNode">
              <el-icon class="arrow-icon color-secondary" :class="showNode ? 'rotate-180' : ''"
                ><ArrowDownBold />
              </el-icon>
            </el-button>
            <el-dropdown
              v-if="showOperate(nodeModel.type)"
              :teleported="false"
              trigger="click"
              placement="bottom-start"
            >
              <el-button text>
                <img src="@/assets/workflow/icon_or.svg" alt="" v-if="condition === 'OR'" />
                <img src="@/assets/workflow/icon_and.svg" alt="" v-if="condition === 'AND'" />
              </el-button>
              <template #dropdown>
                <div style="width: 280px" class="p-12-16">
                  <h5>{{ $t('views.applicationWorkflow.condition.title') }}</h5>
                  <p class="mt-8 lighter">
                    <span>{{ $t('views.applicationWorkflow.condition.front') }}</span>
                    <el-select v-model="condition" size="small" style="width: 60px; margin: 0 8px">
                      <el-option
                        :label="$t('views.applicationWorkflow.condition.AND')"
                        value="AND"
                      />
                      <el-option :label="$t('views.applicationWorkflow.condition.OR')" value="OR" />
                    </el-select>
                    <span>{{ $t('views.applicationWorkflow.condition.text') }}</span>
                  </p>
                </div>
              </template>
            </el-dropdown>
            <el-dropdown v-if="showOperate(nodeModel.type)" :teleported="false" trigger="click">
              <el-button text>
                <AppIcon iconName="app-more"></AppIcon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu style="min-width: 80px">
                  <el-dropdown-item @click="renameNode" class="p-8">{{
                    $t('common.rename')
                  }}</el-dropdown-item>
                  <el-dropdown-item @click="copyNode" class="p-8">{{
                    $t('common.copy')
                  }}</el-dropdown-item>
                  <el-dropdown-item @click="deleteNode" class="border-t p-8">{{
                    $t('common.delete')
                  }}</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
        <el-collapse-transition>
          <div @mousedown.stop @keydown.stop @click.stop v-show="showNode" class="mt-16">
            <el-alert
              v-if="node_status != 200"
              class="mb-16"
              :title="
                props.nodeModel.type === 'application-node'
                  ? $t('views.applicationWorkflow.tip.applicationNodeError')
                  : $t('views.applicationWorkflow.tip.toolNodeError')
              "
              type="error"
              show-icon
              :closable="false"
            />
            <slot></slot>
            <template v-if="nodeFields.length > 0">
              <h5 class="title-decoration-1 mb-8 mt-8">
                {{ $t('common.param.outputParam') }}
              </h5>
              <template v-for="(item, index) in nodeFields" :key="index">
                <div
                  class="flex-between border-r-6 p-8-12 mb-8 layout-bg lighter"
                  @mouseenter="showicon = index"
                  @mouseleave="showicon = null"
                >
                  <span style="max-width: 92%">{{ item.label }} {{ '{' + item.value + '}' }}</span>
                  <el-tooltip
                    effect="dark"
                    :content="$t('views.applicationWorkflow.setting.copyParam')"
                    placement="top"
                    v-if="showicon === index"
                  >
                    <el-button link @click="copyClick(item.globeLabel)" style="padding: 0">
                      <AppIcon iconName="app-copy"></AppIcon>
                    </el-button>
                  </el-tooltip>
                </div>
              </template>
            </template>
          </div>
        </el-collapse-transition>
      </div>
    </div>

    <el-collapse-transition>
      <DropdownMenu
        v-if="showAnchor"
        @mousemove.stop
        @mousedown.stop
        @click.stop
        @wheel="handleWheel"
        :show="showAnchor"
        :id="id"
        style="left: 100%; top: 50%; transform: translate(0, -50%)"
        @clickNodes="clickNodes"
      />
    </el-collapse-transition>

    <el-dialog
      :title="$t('views.applicationWorkflow.nodeName')"
      v-model="nodeNameDialogVisible"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :destroy-on-close="true"
      append-to-body
      @submit.prevent
    >
      <el-form label-position="top" ref="titleFormRef" :model="form">
        <el-form-item
          prop="title"
          :rules="[
            {
              required: true,
              message: $t('common.inputPlaceholder'),
              trigger: 'blur',
            },
          ]"
        >
          <el-input v-model="form.title" @blur="form.title = form.title.trim()" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click.prevent="nodeNameDialogVisible = false">
            {{ $t('common.cancel') }}
          </el-button>
          <el-button type="primary" @click="editName(titleFormRef)">
            {{ $t('common.save') }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import DropdownMenu from '@/views/application-workflow/component/DropdownMenu.vue'
import { set } from 'lodash'
import { iconComponent } from '../icons/utils'
import { copyClick } from '@/utils/clipboard'
import { WorkflowType } from '@/enums/application'
import { MsgError, MsgConfirm } from '@/utils/message'
import type { FormInstance } from 'element-plus'
import { t } from '@/locales'
import { useRoute } from 'vue-router'
const route = useRoute()
const {
  params: { id },
} = route as any

const height = ref<{
  stepContainerHeight: number
  inputContainerHeight: number
  outputContainerHeight: number
}>({
  stepContainerHeight: 0,
  inputContainerHeight: 0,
  outputContainerHeight: 0,
})
const showAnchor = ref<boolean>(false)
const anchorData = ref<any>()
const titleFormRef = ref()
const nodeNameDialogVisible = ref<boolean>(false)
const form = ref<any>({
  title: '',
})

const condition = computed({
  set: (v) => {
    set(props.nodeModel.properties, 'condition', v)
  },
  get: () => {
    if (props.nodeModel.properties.condition) {
      return props.nodeModel.properties.condition
    }
    set(props.nodeModel.properties, 'condition', 'AND')
    return true
  },
})
const showNode = computed({
  set: (v) => {
    set(props.nodeModel.properties, 'showNode', v)
  },
  get: () => {
    if (props.nodeModel.properties.showNode !== undefined) {
      return props.nodeModel.properties.showNode
    }
    set(props.nodeModel.properties, 'showNode', true)
    return true
  },
})

const handleWheel = (event: any) => {
  const isCombinationKeyPressed = event.ctrlKey || event.metaKey
  if (!isCombinationKeyPressed) {
    event.stopPropagation()
  }
}
const node_status = computed(() => {
  if (props.nodeModel.properties.status) {
    return props.nodeModel.properties.status
  }
  return 200
})

function renameNode() {
  form.value.title = props.nodeModel.properties.stepName
  nodeNameDialogVisible.value = true
}
const editName = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      if (
        !props.nodeModel.graphModel.nodes
          .filter((node: any) => node.id !== props.nodeModel.id)
          ?.some((node: any) => node.properties.stepName === form.value.title)
      ) {
        set(props.nodeModel.properties, 'stepName', form.value.title)
        nodeNameDialogVisible.value = false
        formEl.resetFields()
      } else {
        MsgError(t('views.applicationWorkflow.tip.repeatedNodeError'))
      }
    }
  })
}

const mousedown = () => {
  props.nodeModel.graphModel.clearSelectElements()
  set(props.nodeModel, 'isSelected', true)
  set(props.nodeModel, 'isHovered', true)
  props.nodeModel.graphModel.toFront(props.nodeModel.id)
}
const showicon = ref<number | null>(null)
const copyNode = () => {
  props.nodeModel.graphModel.clearSelectElements()
  const cloneNode = props.nodeModel.graphModel.cloneNode(props.nodeModel.id)
  set(cloneNode, 'isSelected', true)
  set(cloneNode, 'isHovered', true)
  props.nodeModel.graphModel.toFront(cloneNode.id)
}
const deleteNode = () => {
  MsgConfirm(t('common.tip'), t('views.applicationWorkflow.delete.confirmTitle'), {
    confirmButtonText: t('common.confirm'),
    confirmButtonClass: 'danger',
  }).then(() => {
    if (props.nodeModel.type === WorkflowType.LoopNode) {
      const next = props.nodeModel.graphModel.getNodeOutgoingNode(props.nodeModel.id)
      next.forEach((n: any) => {
        if (n.type === 'loop-body-node') {
          props.nodeModel.graphModel.deleteNode(n.id)
        }
      })
    }
    props.nodeModel.graphModel.deleteNode(props.nodeModel.id)
  })
  props.nodeModel.graphModel.eventCenter.emit('delete_node')
}
const resizeStepContainer = (wh: any) => {
  if (wh.height) {
    if (!props.nodeModel.virtual) {
      height.value.stepContainerHeight = wh.height
      props.nodeModel.setHeight(height.value.stepContainerHeight)
    }
  }
}

function clickNodes(item: any) {
  const width = item.properties.width ? item.properties.width : 214
  const nodeModel = props.nodeModel.graphModel.addNode({
    type: item.type,
    properties: item.properties,
    x: anchorData.value?.x + width / 2 + 200,
    y: anchorData.value?.y - item.height,
  })
  props.nodeModel.graphModel.addEdge({
    type: 'app-edge',
    sourceNodeId: props.nodeModel.id,
    sourceAnchorId: anchorData.value?.id,
    targetNodeId: nodeModel.id,
  })

  closeNodeMenu()
}

const props = defineProps<{
  nodeModel: any
}>()
const nodeFields = computed(() => {
  if (props.nodeModel.properties.config.fields) {
    const fields = props.nodeModel.properties.config.fields?.map((field: any) => {
      return {
        label: field.label,
        value: field.value,
        globeLabel: `{{${props.nodeModel.properties.stepName}.${field.value}}}`,
        globeValue: `{{context['${props.nodeModel.id}'].${field.value}}}`,
      }
    })
    return fields
  }
  return []
})

function showOperate(type: string) {
  return ![WorkflowType.Start, WorkflowType.Base, WorkflowType.LoopStartNode.toString()].includes(
    type,
  )
}
const openNodeMenu = (anchorValue: any) => {
  showAnchor.value = true
  anchorData.value = anchorValue
}
const closeNodeMenu = () => {
  showAnchor.value = false
  anchorData.value = undefined
}
onMounted(() => {
  set(props.nodeModel, 'openNodeMenu', (anchorData: any) => {
    showAnchor.value ? closeNodeMenu() : openNodeMenu(anchorData)
  })
})
</script>
<style lang="scss" scoped>
.workflow-node-container {
  .step-container {
    border: 2px solid #ffffff !important;
    box-sizing: border-box;
    &:hover {
      box-shadow: 0px 6px 24px 0px rgba(31, 35, 41, 0.08);
    }
    &.isSelected {
      border: 2px solid var(--el-color-primary) !important;
    }
    &.error {
      border: 1px solid #f54a45 !important;
    }
  }
  .arrow-icon {
    transition: 0.2s;
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
