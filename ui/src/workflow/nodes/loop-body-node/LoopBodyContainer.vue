<template>
  <div @mousedown="mousedown" class="workflow-node-container p-16" style="overflow: visible">
    <div
      class="step-container app-card p-16"
      :class="{ isSelected: props.nodeModel.isSelected, error: node_status !== 200 }"
      style="overflow: visible; background: #fff"
    >
      <div>
        <div class="flex-between">
          <div class="flex align-center">
            <component
              :is="iconComponent(`${nodeModel.type}-icon`)"
              class="mr-8"
              :size="24"
              :item="nodeModel?.properties.node_data"
            />
            <h4 class="ellipsis-1 break-all">{{ nodeModel.properties.stepName }}</h4>
          </div>
          <!-- 放大缩小按钮 -->
          <el-button link @click="enlargeHandle">
            <AppIcon
              :iconName="enlarge ? 'app-minify' : 'app-magnify'"
              class="color-secondary"
              style="font-size: 20px"
            >
            </AppIcon>
          </el-button>
        </div>
        <el-collapse-transition>
          <div @mousedown.stop @keydown.stop @click.stop v-show="showNode" class="mt-16">
            <el-alert
              v-if="node_status != 200"
              class="mb-16"
              :title="
                props.nodeModel.type === 'application-node'
                  ? $t('views.applicationWorkflow.tip.applicationNodeError')
                  : $t('views.applicationWorkflow.tip.functionNodeError')
              "
              type="error"
              show-icon
              :closable="false"
            />
            <div :style="`height:${height}px`">
              <slot></slot>
            </div>

            <template v-if="nodeFields.length > 0">
              <h5 class="title-decoration-1 mb-8 mt-8">
                {{ $t('common.param.outputParam') }}
              </h5>
              <template v-for="(item, index) in nodeFields" :key="index">
                <div
                  class="flex-between border-r-4 p-8-12 mb-8 layout-bg lighter"
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
import { ref, computed, provide } from 'vue'
import { set } from 'lodash'
import { iconComponent } from '../../icons/utils'
import { copyClick } from '@/utils/clipboard'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { t } from '@/locales'
import { WorkflowMode } from '@/enums/application'

provide('workflowMode', WorkflowMode.ApplicationLoop)

const titleFormRef = ref()
const nodeNameDialogVisible = ref<boolean>(false)
const form = ref<any>({
  title: '',
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

const node_status = computed(() => {
  if (props.nodeModel.properties.status) {
    return props.nodeModel.properties.status
  }
  return 200
})

const editName = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      if (
        !props.nodeModel.graphModel.nodes?.some(
          (node: any) => node.properties.stepName === form.value.title,
        )
      ) {
        set(props.nodeModel.properties, 'stepName', form.value.title)
        nodeNameDialogVisible.value = false
        formEl.resetFields()
      } else {
        ElMessage.error(t('views.applicationWorkflow.tip.repeatedNodeError'))
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

const height = ref<number>(600)

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

const enlarge = ref(false)

function enlargeHandle() {
  enlarge.value = !enlarge.value
  if (enlarge.value) {
    props.nodeModel.graphModel.transformModel.focusOn(
      props.nodeModel.x,
      props.nodeModel.y,
      props.nodeModel.width + window.innerWidth - props.nodeModel.width,
      props.nodeModel.height - 30,
    )
    height.value =
      (props.nodeModel.graphModel.height - 100) / props.nodeModel.graphModel.transformModel.SCALE_Y
    const width = window.innerWidth / props.nodeModel.graphModel.transformModel.SCALE_X
    props.nodeModel.width = width
    props.nodeModel.setHeight(height.value)
  } else {
    height.value = 600
    const width = 1920
    props.nodeModel.width = width
    props.nodeModel.setHeight(height.value)
  }
}
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
</style>
