<template>
  <el-row :gutter="16">
    <el-col :xs="12" :sm="12" :md="12" :lg="6" :xl="6" class="mb-16">
      <el-dropdown
        trigger="click"
        class="w-full"
        @visible-change="(visible: boolean) => handleVisibleChange('application', visible)"
      >
        <el-card shadow="never" class="cursor w-full">
          <div class="flex-between">
            <div class="flex align-center">
              <img src="@/assets/home/icon_create-agent.svg" alt="" />
              <div class="ml-8">
                <p>{{ $t('layout.home.createAgent') }}</p>
                <p class="color-secondary font-small mt-8">
                  {{ $t('layout.home.createAgentDescribe') }}
                </p>
              </div>
            </div>
            <el-icon
              class="arrow-icon"
              :class="{ 'rotate-180': isDropdownVisible === 'application' }"
              ><ArrowDown
            /></el-icon>
          </div>
        </el-card>
        <template #dropdown>
          <el-dropdown-menu class="create-dropdown">
            <el-dropdown-item @click="openCreateDialog('SIMPLE')">
              <div class="flex">
                <el-avatar shape="square" class="avatar-blue mt-4" :size="32">
                  <img
                    src="@/assets/application/icon_simple_application.svg"
                    style="width: 65%"
                    alt=""
                  />
                </el-avatar>
                <div class="pre-wrap ml-8">
                  <div class="lighter">
                    {{ $t('views.application.simpleAgent') }}
                  </div>
                  <el-text type="info" size="small" class="color-secondary"
                    >{{ $t('views.application.simplePlaceholder') }}
                  </el-text>
                </div>
              </div>
            </el-dropdown-item>
            <el-dropdown-item @click="openCreateDialog('WORK_FLOW')">
              <div class="flex">
                <el-avatar shape="square" class="avatar-purple mt-4" :size="32">
                  <img
                    src="@/assets/application/icon_workflow_application.svg"
                    style="width: 65%"
                    alt=""
                  />
                </el-avatar>
                <div class="pre-wrap ml-8">
                  <div class="lighter">{{ $t('views.application.AdvancedAgent') }}</div>
                  <el-text type="info" size="small" class="color-secondary"
                    >{{ $t('views.application.advancedPlaceholder') }}
                  </el-text>
                </div>
              </div>
            </el-dropdown-item>
            <el-upload
              class="import-button"
              ref="elUploadRef"
              :file-list="[]"
              action="#"
              multiple
              :auto-upload="false"
              :show-file-list="false"
              :limit="1"
              :on-change="(file: any, fileList: any) => importApplication(file)"
            >
              <el-dropdown-item>
                <div class="flex align-center w-full">
                  <el-avatar shape="square" class="mt-4" :size="32" style="background: none">
                    <img src="@/assets/icon_import.svg" alt="" />
                  </el-avatar>
                  <div class="pre-wrap ml-8">
                    <div class="lighter">
                      {{ $t('views.application.importApplication') }}
                    </div>
                  </div>
                </div>
              </el-dropdown-item>
            </el-upload>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </el-col>
  </el-row>
  <CreateApplicationDialog ref="CreateApplicationDialogRef" />
</template>
<script setup lang="ts">
import { ref } from 'vue'
import CreateApplicationDialog from '@/views/application/component/CreateApplicationDialog.vue'
import ApplicationApi from '@/api/application/application'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import { useRouter, useRoute } from 'vue-router'
import useStore from '@/stores'
import { t } from '@/locales'
const { user } = useStore()
const router = useRouter()
const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
  tokenUsage: {
    type: Array,
    default: () => [],
  },
  topQuestions: {
    type: Array,
    default: () => [],
  },
})

// 智能体快捷方式

const isDropdownVisible = ref('')

const handleVisibleChange = (val: string, visible: boolean) => {
  isDropdownVisible.value = visible ? val : ''
}
const CreateApplicationDialogRef = ref()

function openCreateDialog(type?: string) {
  CreateApplicationDialogRef.value.open('default', type)
}
const elUploadRef = ref()
const importApplication = (file: any) => {
  const formData = new FormData()
  formData.append('file', file.raw, file.name)
  elUploadRef.value.clearFiles()
  ApplicationApi.importApplication('default', formData)
    .then(async (res: any) => {
      if (res?.data) {
        user.profile()
        router.push({ path: `/application` })
      }
    })
    .catch((e) => {
      if (e.code === 400) {
        MsgConfirm(t('common.tip'), t('views.application.tip.professionalMessage'), {
          cancelButtonText: t('common.confirm'),
          confirmButtonText: t('common.professional'),
        }).then(() => {
          window.open('https://maxkb.cn/pricing.html', '_blank')
        })
      }
    })
}
</script>
<style lang="scss" scoped></style>
