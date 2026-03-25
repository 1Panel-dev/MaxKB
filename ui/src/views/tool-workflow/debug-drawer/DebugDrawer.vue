<template>
  <el-drawer
    v-model="drawer"
    :title="$t('common.debug')"
    direction="rtl"
    :before-close="close"
    :destroy-on-close="true"
    size="800px"
  >
    <h4 class="title-decoration-1 mb-16" v-if="userInputFieldList.length > 0">
      {{ $t('common.param.inputParam') }}
    </h4>
    <el-form
      v-if="userInputFieldList.length > 0"
      ref="formRef"
      :model="userInputForm"
      label-position="top"
      require-asterisk-position="right"
      hide-required-asterisk
      @submit.prevent
    >
      <template v-for="(item, index) in userInputFieldList" :key="index">
        <el-form-item
          :label="item.label"
          :prop="item.field"
          :rules="{
            required: item.is_required,
            message: $t('views.tool.form.param.inputPlaceholder'),
            trigger: 'blur',
          }"
        >
          <template #label>
            <div class="flex">
              <span
                >{{ item.label }} <span class="color-danger" v-if="item.is_required">*</span></span
              >
              <el-tag type="info" class="info-tag ml-4">{{ item.type }}</el-tag>
            </div>
          </template>
          <el-input
            v-if="['string'].includes(item.type)"
            v-model="userInputForm[item.field]"
            :placeholder="$t('views.tool.form.param.inputPlaceholder')"
          />
          <JsonInput
            v-if="['array', 'dict'].includes(item.type)"
            v-model="userInputForm[item.field]"
          />
          <el-input-number
            v-if="['int', 'float'].includes(item.type)"
            v-model="userInputForm[item.field]"
          />
          <el-switch
            v-if="['boolean'].includes(item.type)"
            v-model="userInputForm[item.field]"
            :active-value="true"
            :inactive-value="false"
          />
        </el-form-item>
      </template>
    </el-form>
    <template #footer>
      <el-button @click="close">{{ $t('common.cancel') }}</el-button>
      <el-button type="primary" @click="run"> {{ $t('views.tool.form.debug.run') }}</el-button>
    </template>
    <ResultDrawer @close="closeResult" :key="index" ref="ToolResultDrawerRef" />
  </el-drawer>
</template>
<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import JsonInput from '@/components/dynamics-form/items/JsonInput.vue'
import { type FormInstance } from 'element-plus'
import ResultDrawer from './ResultDrawer.vue'
import { number } from 'echarts'
const index = ref<number>(0)
const route = useRoute()
const {
  params: { folderId },
  /*
  folderId 可以区分 resource-management shared还是 workspace
  */
} = route as any
const isShared = computed(() => {
  return folderId === 'share'
})
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else if (route.path.includes('share/')) {
    return 'workspaceShare'
  } else {
    return 'workspace'
  }
})

const toolDetail = ref<any>(null)
const userInputFieldList = computed(() => {
  return (
    toolDetail.value?.work_flow?.nodes?.find((node: any) => node.id === 'tool-base-node')
      ?.properties?.user_input_field_list || []
  )
})
const closeResult = () => {
  index.value++
}
function getDetail(toolId: string) {
  loadSharedApi({ type: 'tool', isShared: isShared.value, systemType: apiType.value })
    .getToolById(toolId)
    .then((res: any) => {
      toolDetail.value = res.data
    })
}

const formRef = ref<FormInstance>()
const userInputForm = ref<any>({})
const ToolResultDrawerRef = ref()

const run = () => {
  if (userInputFieldList.value.length === 0) {
    ToolResultDrawerRef.value?.open(toolDetail.value.id, userInputForm.value)
  } else {
    formRef.value?.validate((valid: boolean) => {
      if (!valid) return
      ToolResultDrawerRef.value?.open(toolDetail.value.id, userInputForm.value)
    })
  }
}

const drawer = ref<boolean>(false)
const open = (toolId: any) => {
  getDetail(toolId)
  drawer.value = true
}
const close = () => {
  drawer.value = false
  toolDetail.value = null
  userInputForm.value = {}
}
defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
