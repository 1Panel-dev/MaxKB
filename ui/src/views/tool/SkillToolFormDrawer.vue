<template>
  <el-drawer v-model="visible" size="60%" :before-close="close">
    <template #header>
      <h4>{{ title }}</h4>
    </template>
    <div>
      <h4 class="title-decoration-1 mb-16">
        {{ $t('views.model.modelForm.title.baseInfo') }}
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
        <el-form-item :label="$t('common.name')" prop="name">
          <div class="flex w-full">
            <div
              v-if="form.id"
              class="edit-avatar mr-12"
              @mouseenter="showEditIcon = true"
              @mouseleave="showEditIcon = false"
            >
              <el-Avatar
                v-if="isAppIcon(form.icon)"
                :id="form.id"
                shape="square"
                :size="32"
                style="background: none"
              >
                <img :src="String(form.icon)" alt="" />
              </el-Avatar>

              <el-avatar v-else shape="square" :size="32">
                <img src="@/assets/tool/icon_skill.svg" style="width: 75%" alt="" />
              </el-avatar>
              <el-Avatar
                v-if="showEditIcon"
                :id="form.id"
                shape="square"
                class="edit-mask"
                :size="32"
                @click="openEditAvatar"
              >
                <AppIcon iconName="app-edit"></AppIcon>
              </el-Avatar>
            </div>

            <el-avatar v-else shape="square" :size="32" class="mr-12">
              <img src="@/assets/tool/icon_skill.svg" style="width: 65%" alt="" />
            </el-avatar>
            <el-input
              v-model="form.name"
              :placeholder="$t('views.tool.form.skillName.placeholder')"
              maxlength="64"
              show-word-limit
              @blur="form.name = form.name?.trim()"
            />
          </div>
        </el-form-item>

        <el-form-item :label="$t('common.desc')">
          <el-input
            v-model="form.desc"
            type="textarea"
            :placeholder="$t('common.descPlaceholder')"
            maxlength="128"
            show-word-limit
            :autosize="{ minRows: 3 }"
            @blur="form.desc = form.desc?.trim()"
          />
        </el-form-item>
        <div class="flex-between">
          <h4 class="title-decoration-1 mb-16">
            {{ $t('common.param.initParam') }}
            <el-text type="info" class="color-secondary lighter">
              {{ $t('views.tool.skill.initParamPlaceholder') }}
            </el-text>
          </h4>
          <el-button link type="primary" @click="openAddInitDialog()">
            <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
            {{ $t('common.add') }}
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
              <el-tag size="small" type="info" class="info-tag">{{
                input_type_list.find((item) => item.value === row.input_type)?.label
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
                    <AppIcon iconName="app-edit"></AppIcon>
                  </el-button>
                </el-tooltip>
              </span>
              <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
                <el-button type="primary" text @click="deleteInitField($index)">
                  <AppIcon iconName="app-delete"></AppIcon>
                </el-button>
              </el-tooltip>
            </template>
          </el-table-column>
        </el-table>
        <h4 class="title-decoration-1 mb-16">
          {{ $t('views.tool.skill.skillFile') }}
        </h4>

        <el-form-item prop="fileList">
          <div v-if="form.fileList?.length" class="w-full">
            <template v-for="(item, index) in form.fileList" :key="index">
              <el-card shadow="never" style="--el-card-padding: 8px 12px; line-height: normal">
                <div class="flex-between">
                  <div class="flex">
                    <img :src="getImgUrl(item && item?.name)" alt="" width="40" />
                    <div class="ml-8">
                      <p class="ellipsis-1" :title="item && item?.name">
                        {{ item && item?.name }}
                      </p>
                      <el-text type="info" size="small">{{
                        filesize(item && item?.size) || '0K'
                      }}</el-text>
                    </div>
                  </div>
                </div>
              </el-card>
            </template>

            <el-upload
              v-model:file-list="form.fileList"
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              accept=".zip"
              :on-change="fileHandleChange"
            >
              <el-button link type="primary">{{ $t('views.tool.skill.reUpload') }}</el-button>
            </el-upload>
          </div>
          <el-upload
            v-else
            class="w-full mb-4"
            drag
            v-model:file-list="form.fileList"
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            accept=".zip"
            :on-change="fileHandleChange"
          >
            <img src="@/assets/upload-icon.svg" alt="" />
            <div class="el-upload__text">
              <p>
                {{ $t('views.document.upload.uploadMessage') }}
                <em class="hover">
                  {{ $t('views.document.upload.selectFile') }}
                </em>
              </p>
              <div class="upload__decoration">
                <p>
                  {{ $t('views.document.upload.formats') }}ZIP,
                  {{ $t('views.document.upload.fileLimitSizeTip') }} {{ file_size_limit }} MB
                </p>
              </div>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div>
        <el-button :loading="loading" @click="visible = false">{{ $t('common.cancel') }}</el-button>
        <el-button
          type="primary"
          @click="submit(FormRef)"
          :loading="loading"
          v-if="isEdit ? permissionPrecise.edit(form?.id as string) : permissionPrecise.create()"
        >
          {{ isEdit ? $t('common.save') : $t('common.create') }}
        </el-button>
      </div>
    </template>
    <EditAvatarDialog ref="EditAvatarDialogRef" @refresh="refreshTool" iconType="SKILL" />
    <UserFieldFormDialog ref="UserFieldFormDialogRef" @refresh="refreshInitFieldList" />
  </el-drawer>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import EditAvatarDialog from '@/views/tool/component/EditAvatarDialog.vue'
import UserFieldFormDialog from '@/views/tool/component/UserFieldFormDialog.vue'
import { input_type_list } from '@/components/dynamics-form/constructor/data'
import type { toolData } from '@/api/type/tool'
import type { FormInstance, UploadFiles } from 'element-plus'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'
import { cloneDeep } from 'lodash'
import { t } from '@/locales'
import { filesize, getImgUrl, isAppIcon } from '@/utils/common'
import { useRoute } from 'vue-router'
import useStore from '@/stores'
import permissionMap from '@/permission'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

const route = useRoute()

const props = defineProps({
  title: String,
})
const { folder, user } = useStore()

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const UserFieldFormDialogRef = ref()
const uploadRef = ref()
const permissionPrecise = computed(() => {
  return permissionMap['tool'][apiType.value]
})

const emit = defineEmits(['refresh'])
const EditAvatarDialogRef = ref()
const FormRef = ref()

const isEdit = ref(false)
const loading = ref(false)
const visible = ref(false)
const showEditor = ref(false)
const currentIndex = ref<any>(null)
const showEditIcon = ref(false)
const file_size_limit = ref(100)

const form = ref<toolData>({
  name: '',
  desc: '',
  code: '',
  icon: '',
  input_field_list: [],
  init_field_list: [],
  tool_type: 'SKILL',
  fileList: [],
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
      tool_type: 'SKILL',
      fileList: [],
    }
    FormRef.value?.clearValidate()
  }
})

const rules = reactive({
  name: [
    {
      required: true,
      message: t('views.tool.form.skillName.requiredMessage'),
      trigger: 'blur',
    },
  ],
  fileList: [
    { required: true, message: t('views.document.upload.requiredMessage'), trigger: 'change' },
  ],
})

function close() {
  if (!areAllValuesNonEmpty(form.value)) {
    visible.value = false
  } else {
    MsgConfirm(t('common.tip'), t('views.tool.tip.saveMessage'), {
      confirmButtonText: t('common.confirm'),
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

function refreshTool(data: any) {
  form.value.icon = data
}

function openEditAvatar() {
  EditAvatarDialogRef.value.open(form.value)
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

function deleteInitField(index: any) {
  form.value.init_field_list?.splice(index, 1)
}

const fileHandleChange = (file: any, fileList: UploadFiles) => {
  //1、判断文件大小是否合法，文件限制不能大于100M
  const isLimit = file?.size / 1024 / 1024 < file_size_limit.value
  if (!isLimit) {
    MsgError(t('views.document.tip.fileLimitSizeTip1') + file_size_limit.value + 'MB')
    fileList.splice(-1, 1) //移除当前超出大小的文件
    return false
  }

  if (file?.size === 0) {
    MsgError(t('views.document.upload.errorMessage3'))
    fileList.splice(-1, 1)
    return false
  }
  if (fileList.length > 1) {
    form.value.fileList = fileList.slice(-1) // 截取最后一个文件
  }
  const fd = new FormData()
  fd.append('file', file.raw)
  loadSharedApi({ type: 'tool', systemType: apiType.value })
    .uploadSkillFile(fd, loading)
    .then((res: any) => {
      form.value.code = res.data
      loading.value = false
    })
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid: any) => {
    if (valid) {
      loading.value = true
      if (isEdit.value) {
        loadSharedApi({ type: 'tool', systemType: apiType.value })
          .putTool(form.value?.id as string, form.value)
          .then((res: any) => {
            MsgSuccess(t('common.editSuccess'))
            emit('refresh', res.data)
            return user.profile().then(() => {
              visible.value = false
              uploadRef.value?.clearFiles()
            })
          })

          .finally(() => {
            loading.value = false
          })
      } else {
        const obj = {
          folder_id: folder.currentFolder?.id,
          ...form.value,
        }
        loadSharedApi({ type: 'tool', systemType: apiType.value })
          .postTool(obj)
          .then((res: any) => {
            MsgSuccess(t('common.createSuccess'))
            emit('refresh')
            return user.profile().then(() => {
              visible.value = false
              uploadRef.value?.clearFiles()
            })
          })
          .finally(() => {
            loading.value = false
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
  open,
})
</script>
<style lang="scss" scoped></style>
