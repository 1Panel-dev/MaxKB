<template>
  <el-dialog
    :title="$t('views.model.modelForm.title.paramSetting')"
    v-model="dialogVisible"
    width="800px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
  >
    <el-button type="primary" @click="openAddDrawer()" class="mb-12">
      {{ $t('common.param.addParam') }}
    </el-button>
    <el-table :data="modelParamsForm" class="mb-16">
      <el-table-column
        prop="label"
        :label="$t('dynamicsForm.paramForm.name.label')"
        show-overflow-tooltip
      >
        <template #default="{ row }">
          <span v-if="row.label && row.label.input_type === 'TooltipLabel'">{{
            row.label.label
          }}</span>
          <span v-else>{{ row.label }}</span>
        </template>
      </el-table-column>
      <el-table-column
        prop="field"
        :label="$t('dynamicsForm.paramForm.field.label')"
        show-overflow-tooltip
      />
      <el-table-column :label="$t('dynamicsForm.paramForm.input_type.label')" width="110px">
        <template #default="{ row }">
          <el-tag type="info" class="info-tag">{{
            input_type_list.find((item) => item.value === row.input_type)?.label
          }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column
        prop="default_value"
        :label="$t('dynamicsForm.default.label')"
        show-overflow-tooltip
      />
      <el-table-column :label="$t('common.required')">
        <template #default="{ row }">
          <div @click.stop>
            <el-switch disabled size="small" v-model="row.required" />
          </div>
        </template>
      </el-table-column>

      <el-table-column :label="$t('common.operation')" align="left" width="90">
        <template #default="{ row, $index }">
          <span class="mr-4">
            <el-tooltip effect="dark" :content="$t('common.modify')" placement="top">
              <el-button type="primary" text @click.stop="openAddDrawer(row, $index)">
                <AppIcon iconName="app-edit"></AppIcon>
              </el-button>
            </el-tooltip>
          </span>
          <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
            <el-button type="primary" text @click="deleteParam($index)">
              <AppIcon iconName="app-delete"></AppIcon>
            </el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="close">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
  <AddParamDrawer ref="AddParamRef" @refresh="refresh" />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import type { Model } from '@/api/type/model'
import AddParamDrawer from './AddParamDrawer.vue'
import { MsgError, MsgSuccess } from '@/utils/message'
import { input_type_list } from '@/components/dynamics-form/constructor/data'
import { t } from '@/locales'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

const route = useRoute()

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const loading = ref<boolean>(false)
const dialogVisible = ref<boolean>(false)
const modelParamsForm = ref<any[]>([])
const AddParamRef = ref()
const currentModel = ref<Model | null>(null)

const open = (model: Model) => {
  currentModel.value = model
  dialogVisible.value = true
  loading.value = true
  loadSharedApi({ type: 'model', systemType: apiType.value })
    .getModelParamsForm(model.id, loading)
    .then((ok: any) => {
      loading.value = false
      modelParamsForm.value = ok.data
    })
    .catch(() => {
      loading.value = false
    })
}

const close = () => {
  dialogVisible.value = false
}

function openAddDrawer(data?: any, index?: any) {
  AddParamRef.value?.open(data, index)
}

function deleteParam(index: any) {
  modelParamsForm.value.splice(index, 1)
}

function refresh(data: any, index: any) {
  for (let i = 0; i < modelParamsForm.value.length; i++) {
    const field = modelParamsForm.value[i].field
    let label = modelParamsForm.value[i].label
    if (label && label.input_type === 'TooltipLabel') {
      label = label.label
    }
    let label2 = data.label
    if (label2 && label2.input_type === 'TooltipLabel') {
      label2 = label2.label
    }

    if (field === data.field && index !== i) {
      MsgError(t('views.model.tip.errorMessage') + data.field)
      return
    }
    if (label === label2 && index !== i) {
      MsgError(t('views.model.tip.errorMessage') + label)
      return
    }
  }
  if (index !== null) {
    modelParamsForm.value.splice(index, 1, data)
  } else {
    modelParamsForm.value.push(data)
  }
}

function submit() {
  if (!currentModel.value) {
    return
  }
  loadSharedApi({ type: 'model', systemType: apiType.value })
    .updateModelParamsForm(currentModel.value.id, modelParamsForm.value, loading)
    .then((ok: any) => {
      MsgSuccess(t('views.model.tip.saveSuccessMessage'))
      close()
      // emit('submit')
    })
}

defineExpose({ open, close })
</script>

<style scoped lang="scss"></style>
