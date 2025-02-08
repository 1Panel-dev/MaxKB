<template>
  <el-drawer v-model="visible" size="60%" :before-close="close">
    <template #header>
      <h4>{{ title }}</h4>
    </template>
    <div>
      <h4 class="title-decoration-1 mb-16">
        {{ $t('views.functionLib.functionForm.title.baseInfo') }}
      </h4>
      <el-form
        ref="FormRef"
        :model="form"
        :rules="rules"
        label-position="top"
        require-asterisk-position="right"
        v-loading="loading"
      >
        <el-form-item
          :label="$t('views.functionLib.functionForm.form.functionName.label')"
          prop="name"
        >
          <el-input
            v-model="form.name"
            :placeholder="$t('views.functionLib.functionForm.form.functionName.placeholder')"
            maxlength="64"
            show-word-limit
            @blur="form.name = form.name?.trim()"
          />
        </el-form-item>
        <el-form-item :label="$t('views.functionLib.functionForm.form.functionDescription.label')">
          <el-input
            v-model="form.desc"
            type="textarea"
            :placeholder="$t('views.functionLib.functionForm.form.functionDescription.placeholder')"
            maxlength="128"
            show-word-limit
            :autosize="{ minRows: 3 }"
            @blur="form.desc = form.desc?.trim()"
          />
        </el-form-item>
        <el-form-item prop="permission_type">
          <template #label>
            <span>{{ $t('views.functionLib.functionForm.form.permission_type.label') }}</span>
          </template>

          <el-radio-group v-model="form.permission_type" class="card__radio">
            <el-row :gutter="16">
              <template v-for="(value, key) of PermissionType" :key="key">
                <el-col :span="12">
                  <el-card
                    shadow="never"
                    class="mb-16"
                    :class="form.permission_type === key ? 'active' : ''"
                  >
                    <el-radio :value="key" size="large">
                      <p class="mb-4">{{ $t(value) }}</p>
                      <el-text type="info">
                        {{ $t(PermissionDesc[key]) }}
                      </el-text>
                    </el-radio>
                  </el-card>
                </el-col>
              </template>
            </el-row>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <div class="flex-between">
        <h4 class="title-decoration-1 mb-16">
          {{ $t('common.param.inputParam') }}
          <el-text type="info" class="color-secondary">
            {{ $t('views.functionLib.functionForm.form.param.paramInfo1') }}
          </el-text>
        </h4>
        <el-button link type="primary" @click="openAddDialog()">
          <el-icon class="mr-4"><Plus /></el-icon> {{ $t('common.add') }}
        </el-button>
      </div>

      <el-table :data="form.input_field_list" class="mb-16">
        <el-table-column
          prop="name"
          :label="$t('views.functionLib.functionForm.form.paramName.label')"
        />
        <el-table-column :label="$t('views.functionLib.functionForm.form.dataType.label')">
          <template #default="{ row }">
            <el-tag type="info" class="info-tag">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.required')">
          <template #default="{ row }">
            <div @click.stop>
              <el-switch size="small" v-model="row.is_required" />
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="source"
          :label="$t('views.functionLib.functionForm.form.source.label')"
        >
          <template #default="{ row }">
            {{
              row.source === 'custom'
                ? $t('views.functionLib.functionForm.form.source.custom')
                : $t('views.functionLib.functionForm.form.source.reference')
            }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.operation')" align="left" width="90">
          <template #default="{ row, $index }">
            <span class="mr-4">
              <el-tooltip effect="dark" :content="$t('common.modify')" placement="top">
                <el-button type="primary" text @click.stop="openAddDialog(row, $index)">
                  <el-icon><EditPen /></el-icon>
                </el-button>
              </el-tooltip>
            </span>
            <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
              <el-button type="primary" text @click="deleteField($index)">
                <el-icon>
                  <Delete />
                </el-icon>
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
      <h4 class="title-decoration-1 mb-16">
        {{ $t('views.functionLib.functionForm.form.param.code') }}
        <el-text type="info" class="color-secondary">
          {{ $t('views.functionLib.functionForm.form.param.paramInfo2') }}
        </el-text>
      </h4>

      <div class="function-CodemirrorEditor mb-8" v-if="showEditor">
        <CodemirrorEditor v-model="form.code" />
        <div class="function-CodemirrorEditor__footer">
          <el-button text type="info" @click="openCodemirrorDialog" class="magnify">
            <AppIcon iconName="app-magnify" style="font-size: 16px"></AppIcon>
          </el-button>
        </div>
      </div>
      <h4 class="title-decoration-1 mb-16 mt-16">
        {{ $t('common.param.outputParam') }}
        <el-text type="info" class="color-secondary">
          {{ $t('views.functionLib.functionForm.form.param.paramInfo1') }}
        </el-text>
      </h4>
      <div class="flex-between border-r-4 p-8-12 mb-8 layout-bg lighter">
        <span>{{ $t('common.result') }} {result}</span>
      </div>
    </div>

    <template #footer>
      <div>
        <el-button :loading="loading" @click="visible = false">{{ $t('common.cancel') }}</el-button>
        <el-button :loading="loading" @click="openDebug">{{ $t('common.debug') }}</el-button>
        <el-button type="primary" @click="submit(FormRef)" :loading="loading">
          {{ isEdit ? $t('common.save') : $t('common.create') }}</el-button
        >
      </div>
    </template>

    <!-- Codemirror 弹出层 -->
    <el-dialog
      v-model="dialogVisible"
      :title="$t('views.functionLib.functionForm.form.param.code')"
      append-to-body
      fullscreen
    >
      <CodemirrorEditor
        v-model="cloneContent"
        style="
          height: calc(100vh - 160px) !important;
          border: 1px solid #bbbfc4;
          border-radius: 4px;
        "
      />
      <template #footer>
        <div class="dialog-footer mt-24">
          <el-button type="primary" @click="submitDialog"> {{ $t('common.confirm') }}</el-button>
        </div>
      </template>
    </el-dialog>
    <FunctionDebugDrawer ref="FunctionDebugDrawerRef" />
    <FieldFormDialog ref="FieldFormDialogRef" @refresh="refreshFieldList" />
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import FieldFormDialog from './FieldFormDialog.vue'
import FunctionDebugDrawer from './FunctionDebugDrawer.vue'
import type { functionLibData } from '@/api/type/function-lib'
import functionLibApi from '@/api/function-lib'
import type { FormInstance } from 'element-plus'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { cloneDeep } from 'lodash'
import { PermissionType, PermissionDesc } from '@/enums/model'
import { t } from '@/locales'
const props = defineProps({
  title: String
})

const emit = defineEmits(['refresh'])
const FieldFormDialogRef = ref()
const FunctionDebugDrawerRef = ref()

const FormRef = ref()

const isEdit = ref(false)
const loading = ref(false)
const visible = ref(false)
const showEditor = ref(false)
const currentIndex = ref<any>(null)

const form = ref<functionLibData>({
  name: '',
  desc: '',
  code: '',
  input_field_list: [],
  permission_type: 'PRIVATE'
})

const dialogVisible = ref(false)
const cloneContent = ref<any>('')

watch(visible, (bool) => {
  if (!bool) {
    isEdit.value = false
    showEditor.value = false
    currentIndex.value = null
    form.value = {
      name: '',
      desc: '',
      code: '',
      input_field_list: [],
      permission_type: 'PRIVATE'
    }
    FormRef.value?.clearValidate()
  }
})

const rules = reactive({
  name: [
    {
      required: true,
      message: t('views.functionLib.functionForm.form.functionName.requiredMessage'),
      trigger: 'blur'
    }
  ],
  permission_type: [
    {
      required: true,
      message: t('views.functionLib.functionForm.form.permission_type.requiredMessage'),
      trigger: 'change'
    }
  ]
})

function openCodemirrorDialog() {
  cloneContent.value = form.value.code
  dialogVisible.value = true
}

function submitDialog() {
  form.value.code = cloneContent.value
  dialogVisible.value = false
}

function close() {
  if (isEdit.value || !areAllValuesNonEmpty(form.value)) {
    visible.value = false
  } else {
    MsgConfirm(t('common.tip'), t('views.functionLib.tip.saveMessage'), {
      confirmButtonText: t('common.confirm'),
      type: 'warning'
    })
      .then(() => {
        visible.value = false
      })
      .catch(() => {})
  }
}

function areAllValuesNonEmpty(obj: any) {
  return Object.values(obj).some((value) => {
    return Array.isArray(value)
      ? value.length !== 0
      : value !== null && value !== undefined && value !== ''
  })
}

function openDebug() {
  FunctionDebugDrawerRef.value.open(form.value)
}

function deleteField(index: any) {
  form.value.input_field_list?.splice(index, 1)
}

function openAddDialog(data?: any, index?: any) {
  if (typeof index !== 'undefined') {
    currentIndex.value = index
  }

  FieldFormDialogRef.value.open(data)
}

function refreshFieldList(data: any) {
  if (currentIndex.value !== null) {
    form.value.input_field_list?.splice(currentIndex.value, 1, data)
  } else {
    form.value.input_field_list?.push(data)
  }
  currentIndex.value = null
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid: any) => {
    if (valid) {
      if (isEdit.value) {
        functionLibApi.putFunctionLib(form.value?.id as string, form.value, loading).then((res) => {
          MsgSuccess(t('common.editSuccess'))
          emit('refresh', res.data)
          visible.value = false
        })
      } else {
        functionLibApi.postFunctionLib(form.value, loading).then((res) => {
          MsgSuccess(t('common.createSuccess'))
          emit('refresh')
          visible.value = false
        })
      }
    }
  })
}

const open = (data: any) => {
  if (data) {
    isEdit.value = data?.id ? true : false
    form.value = cloneDeep(data)
  }
  visible.value = true
  setTimeout(() => {
    showEditor.value = true
  }, 100)
}

defineExpose({
  open
})
</script>
<style lang="scss" scoped>
.function-CodemirrorEditor__footer {
  position: absolute;
  bottom: 10px;
  right: 10px;
}
.function-CodemirrorEditor {
  position: relative;
}
</style>
