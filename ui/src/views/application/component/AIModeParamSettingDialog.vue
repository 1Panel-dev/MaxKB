<template>
  <el-dialog
    align-center
    :title="$t('views.application.applicationForm.dialogues.paramSettings')"
    class="aiMode-param-dialog"
    v-model="dialogVisible"
    style="width: 550px"
    append-to-body
  >
    <el-form label-position="top" ref="paramFormRef" :model="form">
      <el-form-item v-for="(item, key) in form" :key="key">
        <template #label>
          <div class="flex align-center">
            <div class="flex-between mr-4">
              <span>{{ item.label }}</span>
            </div>
            <el-tooltip effect="dark" placement="right">
              <template #content>{{ item.tooltip }}</template>
              <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
            </el-tooltip>
          </div>
        </template>
        <el-slider
          v-model="item.value"
          show-input
          :show-input-controls="false"
          :min="item.min"
          :max="item.max"
          :precision="item.precision || 0"
          :step="item.step || 1"
          class="custom-slider"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer p-16">
        <el-button @click.prevent="dialogVisible = false">
          {{ $t('views.application.applicationForm.buttons.cancel') }}
        </el-button>
        <el-button type="primary" @click="submit" :loading="loading">
          {{ $t('views.application.applicationForm.buttons.confirm') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { cloneDeep, set } from 'lodash'
import type { FormInstance } from 'element-plus'
import useStore from '@/stores'

const { application } = useStore()

const emit = defineEmits(['refresh'])

const paramFormRef = ref<FormInstance>()
const form = reactive<Form>({})
const dialogVisible = ref(false)
const loading = ref(false)
const props = defineProps<{
  id: string
  nodeId?: string
}>()
const resetForm = () => {
  // 清空 form 对象，等待新的数据
  Object.keys(form).forEach((key) => delete form[key])
}

interface Form {
  [key: string]: FormField
}

interface FormField {
  value: any
  min?: number
  max?: number
  step?: number
  label?: string
  precision?: number
  tooltip?: string
}

const open = (data: any) => {
  const newData = cloneDeep(data)
  Object.keys(form).forEach((key) => {
    delete form[key]
  })
  Object.keys(newData).forEach((key) => {
    set(form, key, newData[key])
  })
  dialogVisible.value = true
}

const submit = async () => {
  if (paramFormRef.value) {
    await paramFormRef.value.validate((valid, fields) => {
      if (valid) {
        const data = Object.keys(form).reduce(
          (acc, key) => {
            acc[key] = form[key].value
            return acc
          },
          {} as Record<string, any>
        )
        if (props.nodeId) {
          data.node_id = props.nodeId
        }
        application.asyncPostModelConfig(props.id, data, loading).then(() => {
          emit('refresh', data)
          dialogVisible.value = false
        })
      }
    })
  }
}

watch(dialogVisible, (bool) => {
  if (!bool) {
    resetForm()
  }
})

defineExpose({ open })
</script>

<style lang="scss" scoped>
.aiMode-param-dialog {
  padding: 8px 8px 24px 8px;

  .el-dialog__header {
    padding: 16px 16px 0 16px;
  }

  .el-dialog__body {
    padding: 16px !important;
  }

  .dialog-max-height {
    height: 550px;
  }

  .custom-slider {
    .el-input-number.is-without-controls .el-input__wrapper {
      padding: 0 !important;
    }
  }
}
</style>
