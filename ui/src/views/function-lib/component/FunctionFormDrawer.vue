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
        @submit.prevent
      >
        <el-form-item
          :label="$t('views.functionLib.functionForm.form.functionName.label')"
          prop="name"
        >
          <div class="flex w-full">
            <div
              v-if="form.id"
              class="edit-avatar mr-12"
              @mouseenter="showEditIcon = true"
              @mouseleave="showEditIcon = false"
            >
              <AppAvatar
                v-if="isAppIcon(form.icon)"
                :id="form.id"
                shape="square"
                :size="32"
                style="background: none"
              >
                <img :src="String(form.icon)" alt="" />
              </AppAvatar>
              <AppAvatar
                v-else-if="form.name"
                :id="form.id"
                :name="form.name"
                pinyinColor
                shape="square"
                :size="32"
              />
              <AppAvatar
                v-if="showEditIcon"
                :id="form.id"
                shape="square"
                class="edit-mask"
                :size="32"
                @click="openEditAvatar"
              >
                <el-icon><EditPen /></el-icon>
              </AppAvatar>
            </div>
            <AppAvatar shape="square" style="background: #34c724" class="mr-12" v-else>
              <img src="@/assets/icon_function_outlined.svg" style="width: 75%" alt="" />
            </AppAvatar>
            <el-input
              v-model="form.name"
              :placeholder="$t('views.functionLib.functionForm.form.functionName.placeholder')"
              maxlength="64"
              show-word-limit
              @blur="form.name = form.name?.trim()"
            />
          </div>
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
        <!--
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
        -->
      </el-form>
      <div class="flex-between">
        <h4 class="title-decoration-1 mb-16">
          {{ $t('common.param.initParam') }}
        </h4>
        <el-button link type="primary" @click="openAddInitDialog()">
          <el-icon class="mr-4"><Plus /></el-icon> {{ $t('common.add') }}
        </el-button>
      </div>
      <el-table ref="initFieldTableRef" :data="form.init_field_list" class="mb-16">
        <el-table-column prop="field" :label="$t('dynamicsForm.paramForm.field.label')">
          <template #default="{ row }">
            <span :title="row.field" class="ellipsis-1">{{ row.field }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('dynamicsForm.paramForm.input_type.label')">
          <template #default="{ row }">
            <el-tag type="info" class="info-tag" v-if="row.input_type === 'TextInput'">{{
              $t('dynamicsForm.input_type_list.TextInput')
            }}</el-tag>
            <el-tag type="info" class="info-tag" v-if="row.input_type === 'PasswordInput'">{{
              $t('dynamicsForm.input_type_list.PasswordInput')
            }}</el-tag>
            <el-tag type="info" class="info-tag" v-if="row.input_type === 'Slider'">{{
              $t('dynamicsForm.input_type_list.Slider')
            }}</el-tag>
            <el-tag type="info" class="info-tag" v-if="row.input_type === 'SwitchInput'">{{
              $t('dynamicsForm.input_type_list.SwitchInput')
            }}</el-tag>
            <el-tag type="info" class="info-tag" v-if="row.input_type === 'SingleSelect'">{{
              $t('dynamicsForm.input_type_list.SingleSelect')
            }}</el-tag>
            <el-tag type="info" class="info-tag" v-if="row.input_type === 'MultiSelect'">{{
              $t('dynamicsForm.input_type_list.MultiSelect')
            }}</el-tag>
            <el-tag type="info" class="info-tag" v-if="row.input_type === 'RadioCard'">{{
              $t('dynamicsForm.input_type_list.RadioCard')
            }}</el-tag>
            <el-tag type="info" class="info-tag" v-if="row.input_type === 'DatePicker'">{{
              $t('dynamicsForm.input_type_list.DatePicker')
            }}</el-tag>
          </template>
        </el-table-column>
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
                <el-button type="primary" text @click.stop="openAddInitDialog(row, $index)">
                  <el-icon><EditPen /></el-icon>
                </el-button>
              </el-tooltip>
            </span>
            <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
              <el-button type="primary" text @click="deleteInitField($index)">
                <el-icon>
                  <Delete />
                </el-icon>
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
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

      <el-table ref="inputFieldTableRef" :data="form.input_field_list" class="mb-16">
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
        <span style="color: red; margin-left: -10px">*</span>
        <el-text type="info" class="color-secondary">
          {{ $t('views.functionLib.functionForm.form.param.paramInfo2') }}
        </el-text>
      </h4>

      <div class="mb-8" v-if="showEditor">
        <CodemirrorEditor
          :title="$t('views.functionLib.functionForm.form.param.code')"
          v-model="form.code"
          @submitDialog="submitCodemirrorEditor"
        />
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

    <FunctionDebugDrawer ref="FunctionDebugDrawerRef" />
    <FieldFormDialog ref="FieldFormDialogRef" @refresh="refreshFieldList" />
    <UserFieldFormDialog ref="UserFieldFormDialogRef" @refresh="refreshInitFieldList" />
    <EditAvatarDialog ref="EditAvatarDialogRef" @refresh="refreshFunctionLib" />
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, watch, nextTick } from 'vue'
import FieldFormDialog from './FieldFormDialog.vue'
import FunctionDebugDrawer from './FunctionDebugDrawer.vue'
import type { functionLibData } from '@/api/type/function-lib'
import functionLibApi from '@/api/function-lib'
import type { FormInstance } from 'element-plus'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { cloneDeep } from 'lodash'
import { PermissionType, PermissionDesc } from '@/enums/model'
import { t } from '@/locales'
import UserFieldFormDialog from '@/workflow/nodes/base-node/component/UserFieldFormDialog.vue'
import { isAppIcon } from '@/utils/application'
import EditAvatarDialog from './EditAvatarDialog.vue'
import Sortable from 'sortablejs'

const props = defineProps({
  title: String
})

const emit = defineEmits(['refresh'])
const FieldFormDialogRef = ref()
const FunctionDebugDrawerRef = ref()
const UserFieldFormDialogRef = ref()
const EditAvatarDialogRef = ref()
const initFieldTableRef = ref()
const inputFieldTableRef = ref()

const FormRef = ref()

const isEdit = ref(false)
const loading = ref(false)
const visible = ref(false)
const showEditor = ref(false)
const currentIndex = ref<any>(null)
const showEditIcon = ref(false)

const form = ref<functionLibData>({
  name: '',
  desc: '',
  code: '',
  icon: '',
  input_field_list: [],
  init_field_list: [],
  permission_type: 'PRIVATE'
})

watch(visible, (bool) => {
  if (!bool) {
    isEdit.value = false
    showEditor.value = false
    currentIndex.value = null
    form.value = {
      name: '',
      desc: '',
      code: '',
      icon: '',
      input_field_list: [],
      init_field_list: [],
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

function onDragHandle() {
  // For init_field_list table
  if (initFieldTableRef.value) {
    const el = initFieldTableRef.value.$el.querySelector('.el-table__body-wrapper tbody')
    Sortable.create(el, {
      animation: 150,
      ghostClass: 'sortable-ghost',
      onEnd: ({ newIndex, oldIndex }) => {
        if (newIndex === undefined || oldIndex === undefined) return
        if (newIndex !== oldIndex) {
          const item = form.value.init_field_list?.splice(oldIndex, 1)[0]
          form.value.init_field_list?.splice(newIndex, 0, item)
        }
      }
    })
  }

  // For input_field_list table
  if (inputFieldTableRef.value) {
    const el = inputFieldTableRef.value.$el.querySelector('.el-table__body-wrapper tbody')
    Sortable.create(el, {
      animation: 150,
      ghostClass: 'sortable-ghost',
      onEnd: ({ newIndex, oldIndex }) => {
        if (newIndex === undefined || oldIndex === undefined) return
        if (newIndex !== oldIndex) {
          const item = form.value.input_field_list?.splice(oldIndex, 1)[0]
          form.value.input_field_list?.splice(newIndex, 0, item)
        }
      }
    })
  }
}

function submitCodemirrorEditor(val: string) {
  form.value.code = val
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

function openAddInitDialog(data?: any, index?: any) {
  if (typeof index !== 'undefined') {
    currentIndex.value = index
  }

  UserFieldFormDialogRef.value.open(data)
}

function refreshInitFieldList(data: any) {
  if (currentIndex.value !== null) {
    form.value.init_field_list?.splice(currentIndex.value, 1, data)
  } else {
    form.value.init_field_list?.push(data)
  }
  currentIndex.value = null
  UserFieldFormDialogRef.value.close()
}

function refreshFunctionLib(data: any) {
  form.value.icon = data
  // console.log(data)
}

function deleteInitField(index: any) {
  form.value.init_field_list?.splice(index, 1)
}

function openEditAvatar() {
  EditAvatarDialogRef.value.open(form.value)
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid: any) => {
    if (valid) {
      // console.log(form.value)
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
<style lang="scss" scoped></style>
