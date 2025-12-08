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
        hide-required-asterisk
        v-loading="loading"
        @submit.prevent
      >
        <el-form-item :label="$t('views.tool.form.mcpName.label')" prop="name">
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
                <img src="@/assets/workflow/icon_mcp.svg" style="width: 75%" alt="" />
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
              <img src="@/assets/workflow/icon_mcp.svg" style="width: 75%" alt="" />
            </el-avatar>
            <el-input
              v-model="form.name"
              :placeholder="$t('views.tool.form.mcpName.placeholder')"
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
            :placeholder="$t('views.tool.form.mcpDescription.placeholder')"
            maxlength="128"
            show-word-limit
            :autosize="{ minRows: 3 }"
            @blur="form.desc = form.desc?.trim()"
          />
        </el-form-item>
        <h4 class="title-decoration-1 mb-16">
          {{ $t('views.tool.form.mcp.title') }}
        </h4>

        <el-form-item prop="code">
          <template #label>
            {{ $t('views.tool.form.mcp.label') }}
            <span class="color-danger">*</span>
            <el-text type="info" class="color-secondary">
              （{{ $t('views.tool.form.mcp.tip') }}）
            </el-text>
          </template>
          <el-input
            v-model="form.code"
            :placeholder="mcpServerJson"
            type="textarea"
            :autosize="{ minRows: 5 }"
          />
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div>
        <el-button :loading="loading" @click="testConnection">{{
          $t('views.system.test')
        }}</el-button>
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
    <EditAvatarDialog ref="EditAvatarDialogRef" @refresh="refreshTool" iconType="MCP" />
  </el-drawer>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import EditAvatarDialog from '@/views/tool/component/EditAvatarDialog.vue'
import type { toolData } from '@/api/type/tool'
import type { FormInstance } from 'element-plus'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'
import { cloneDeep } from 'lodash'
import { t } from '@/locales'
import { isAppIcon } from '@/utils/common'
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
const permissionPrecise = computed(() => {
  return permissionMap['tool'][apiType.value]
})

const emit = defineEmits(['refresh'])
const EditAvatarDialogRef = ref()
const mcpServerJson = `{
  "math": {
    "url": "your_server",
    "transport": "sse"
  }
}`

const FormRef = ref()

const isEdit = ref(false)
const loading = ref(false)
const visible = ref(false)
const showEditor = ref(false)
const currentIndex = ref<any>(null)
const showEditIcon = ref(false)

const form = ref<toolData>({
  name: '',
  desc: '',
  code: '',
  icon: '',
  input_field_list: [],
  init_field_list: [],
  tool_type: 'MCP',
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
      tool_type: 'MCP',
    }
    FormRef.value?.clearValidate()
  }
})

const rules = reactive({
  name: [
    {
      required: true,
      message: t('views.tool.form.mcpName.requiredMessage'),
      trigger: 'blur',
    },
  ],
  code: [
    {
      required: true,
      message: t('views.tool.form.mcp.requiredMessage'),
      trigger: 'blur',
    },
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

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid: any) => {
    if (valid) {
      try {
        const parsed = JSON.parse(form.value.code as string)
        if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
          throw new Error('Code must be a valid JSON object')
        }
      } catch (e) {
        MsgError(t('views.applicationWorkflow.nodes.mcpNode.mcpServerTip'))
        return
      }
      loading.value = true
      if (isEdit.value) {
        loadSharedApi({ type: 'tool', systemType: apiType.value })
          .putTool(form.value?.id as string, form.value)
          .then((res: any) => {
            MsgSuccess(t('common.editSuccess'))
            emit('refresh', res.data)
            return user.profile()
          })
          .then(() => {
            visible.value = false
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
            return user.profile()
          })
          .then(() => {
            visible.value = false
          })
          .finally(() => {
            loading.value = false
          })
      }
    }
  })
}

function testConnection() {
  if (!form.value.code) {
    return
  }
  loading.value = true
  loadSharedApi({ type: 'tool', systemType: apiType.value })
    .postToolTestConnection({ code: form.value.code }, loading)
    .then(() => {
      MsgSuccess(t('views.system.testSuccess'))
    })
    .finally(() => {
      loading.value = false
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
