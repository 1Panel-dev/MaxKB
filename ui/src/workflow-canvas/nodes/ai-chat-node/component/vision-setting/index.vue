<script setup lang="ts">
import { QuestionFilled } from '@element-plus/icons-vue'
import { useTemplateRef } from 'vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { VisionSetting } from '../../types'

defineOptions({ name: 'AiChatNodeVisionSetting' })

const props = defineProps<{ nodeModel: WorkflowNodeModel; setting: VisionSetting }>()
const emit = defineEmits<{ update: [setting: VisionSetting] }>()

const imageCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('imageCascaderRef')

function updateSetting(changes: Partial<VisionSetting>) {
  emit('update', { ...props.setting, ...changes })
}

function changeVision(value: boolean | number | string) {
  updateSetting({ vision: Boolean(value) })
}

function validate() {
  return props.setting.vision ? imageCascaderRef.value?.validate() : Promise.resolve()
}

defineExpose({ validate })
</script>

<template>
  <el-form-item>
    <template #label>
      <div class="flex-between w-full">
        <span class="flex items-center gap-1">
          视觉理解
          <el-tooltip content="开启后，可把上游节点输出的图片和视频作为多模态模型输入" placement="right">
            <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
          </el-tooltip>
        </span>
        <el-switch :model-value="setting.vision" size="small" @change="changeVision" />
      </div>
    </template>
  </el-form-item>

  <template v-if="setting.vision">
    <el-form-item prop="image_list" :rules="{ type: 'array', required: true, message: '请选择图片变量', trigger: 'change' }">
      <template #label>
        <span class="flex items-center gap-1">
          图片
          <el-tooltip content="支持引用上游文件上传、图片生成或图片处理节点输出的图片变量" placement="right">
            <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
          </el-tooltip>
        </span>
      </template>
      <NodeCascader
        ref="imageCascaderRef"
        :model-value="setting.image_list"
        :node-model="nodeModel"
        class="w-full"
        placeholder="请选择图片变量"
        @update:model-value="updateSetting({ image_list: $event })"
      />
    </el-form-item>

    <el-form-item>
      <template #label>
        <span class="flex items-center gap-1">
          视频
          <el-tooltip content="可选，支持引用上游节点输出的视频变量" placement="right">
            <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
          </el-tooltip>
        </span>
      </template>
      <NodeCascader
        :model-value="setting.video_list"
        :node-model="nodeModel"
        class="w-full"
        placeholder="请选择视频变量（可选）"
        @update:model-value="updateSetting({ video_list: $event })"
      />
    </el-form-item>
  </template>
</template>
