<template>
  <LayoutContainer :header="$t('common.setting')">
    <div class="dataset-setting main-calc-height">
      <el-scrollbar>
        <div class="p-24" v-loading="loading">
          <h4 class="title-decoration-1 mb-16">
            {{ $t('views.dataset.datasetForm.title.info') }}
          </h4>
          <BaseForm ref="BaseFormRef" :data="detail" />

          <el-form
            ref="webFormRef"
            :rules="rules"
            :model="form"
            label-position="top"
            require-asterisk-position="right"
          >
            <el-form-item :label="$t('views.dataset.datasetForm.form.datasetType.label')" required>
              <el-card shadow="never" class="mb-8" style="width: 50%" v-if="detail.type === '0'">
                <div class="flex align-center">
                  <AppAvatar class="mr-8 avatar-blue" shape="square" :size="32">
                    <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                  </AppAvatar>
                  <div>
                    <div>{{ $t('views.dataset.general') }}</div>
                    <el-text type="info"
                      >{{ $t('views.dataset.datasetForm.form.datasetType.generalInfo') }}
                    </el-text>
                  </div>
                </div>
              </el-card>
              <el-card shadow="never" class="mb-8" style="width: 50%" v-if="detail?.type === '1'">
                <div class="flex align-center">
                  <AppAvatar class="mr-8 avatar-purple" shape="square" :size="32">
                    <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                  </AppAvatar>
                  <div>
                    <div>{{ $t('views.dataset.web') }}</div>
                    <el-text type="info">
                      {{ $t('views.dataset.datasetForm.form.datasetType.webInfo') }}
                    </el-text>
                  </div>
                </div>
              </el-card>
              <el-card shadow="never" class="mb-8" style="width: 50%" v-if="detail?.type === '2'">
                <div class="flex align-center">
                  <AppAvatar shape="square" :size="32" style="background: none">
                    <img src="@/assets/logo_lark.svg" style="width: 100%" alt="" />
                  </AppAvatar>
                  <div>
                    <p>
                      <el-text>{{ $t('views.dataset.lark') }}</el-text>
                    </p>
                    <el-text type="info"
                      >{{ $t('views.dataset.datasetForm.form.datasetType.larkInfo') }}
                    </el-text>
                  </div>
                </div>
              </el-card>
            </el-form-item>
            <el-form-item
              :label="$t('views.dataset.datasetForm.form.source_url.label')"
              prop="source_url"
              v-if="detail.type === '1'"
            >
              <el-input
                v-model="form.source_url"
                :placeholder="$t('views.dataset.datasetForm.form.source_url.placeholder')"
                @blur="form.source_url = form.source_url.trim()"
              />
            </el-form-item>
            <el-form-item
              :label="$t('views.dataset.datasetForm.form.selector.label')"
              v-if="detail.type === '1'"
            >
              <el-input
                v-model="form.selector"
                :placeholder="$t('views.dataset.datasetForm.form.selector.placeholder')"
                @blur="form.selector = form.selector.trim()"
              />
            </el-form-item>
            <el-form-item label="App ID" prop="app_id" v-if="detail.type === '2'">
              <el-input
                v-model="form.app_id"
                :placeholder="
                  $t('views.application.applicationAccess.larkSetting.appIdPlaceholder')
                "
              />
            </el-form-item>
            <el-form-item label="App Secret" prop="app_id" v-if="detail.type === '2'">
              <el-input
                v-model="form.app_secret"
                type="password"
                show-password
                :placeholder="
                  $t('views.application.applicationAccess.larkSetting.appSecretPlaceholder')
                "
              />
            </el-form-item>
            <el-form-item label="Folder Token" prop="folder_token" v-if="detail.type === '2'">
              <el-input
                v-model="form.folder_token"
                :placeholder="
                  $t('views.application.applicationAccess.larkSetting.folderTokenPlaceholder')
                "
              />
            </el-form-item>
          </el-form>
          <div v-if="application_id_list.length > 0">
            <h4 class="title-decoration-1 mb-16">{{ $t('views.dataset.relatedApplications') }}</h4>
            <el-row :gutter="12">
              <el-col
                :span="12"
                v-for="(item, index) in application_list.filter((obj: any) =>
                  application_id_list.some((v: any) => v === obj?.id)
                )"
                :key="index"
                class="mb-16"
              >
                <el-card shadow="never">
                  <div class="flex-between">
                    <div class="flex align-center">
                      <AppAvatar
                        v-if="isAppIcon(item?.icon)"
                        shape="square"
                        :size="32"
                        style="background: none"
                        class="mr-12"
                      >
                        <img :src="item?.icon" alt="" />
                      </AppAvatar>
                      <AppAvatar
                        v-else-if="item?.name"
                        :name="item?.name"
                        pinyinColor
                        shape="square"
                        :size="32"
                        class="mr-12"
                      />
                      {{ item.name }}
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>

          <div class="text-right">
            <el-button @click="submit" type="primary"> {{ $t('common.save') }}</el-button>
          </div>
        </div>
      </el-scrollbar>
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'
import BaseForm from '@/views/dataset/component/BaseForm.vue'
import datasetApi from '@/api/dataset'
import type { ApplicationFormType } from '@/api/type/application'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { isAppIcon } from '@/utils/application'
import useStore from '@/stores'
import { t } from '@/locales'

const route = useRoute()
const {
  params: { id }
} = route as any

const { dataset } = useStore()
const webFormRef = ref()
const BaseFormRef = ref()
const loading = ref(false)
const detail = ref<any>({})
const application_list = ref<Array<ApplicationFormType>>([])
const application_id_list = ref([])
const cloneModelId = ref('')

const form = ref<any>({
  source_url: '',
  selector: '',
  app_id: '',
  app_secret: '',
  folder_token: ''
})

const rules = reactive({
  source_url: [
    {
      required: true,
      message: t('views.dataset.datasetForm.form.source_url.requiredMessage'),
      trigger: 'blur'
    }
  ],
  app_id: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.appIdPlaceholder'),
      trigger: 'blur'
    }
  ],
  app_secret: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.appSecretPlaceholder'),
      trigger: 'blur'
    }
  ],
  folder_token: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.folderTokenPlaceholder'),
      trigger: 'blur'
    }
  ]
})

async function submit() {
  if (await BaseFormRef.value?.validate()) {
    await webFormRef.value.validate((valid: any) => {
      if (valid) {
        const obj =
          detail.value.type === '1' || detail.value.type === '2'
            ? {
                application_id_list: application_id_list.value,
                meta: form.value,
                ...BaseFormRef.value.form
              }
            : {
                application_id_list: application_id_list.value,
                ...BaseFormRef.value.form
              }

        if (cloneModelId.value !== BaseFormRef.value.form.embedding_mode_id) {
          MsgConfirm(t('common.tip'), t('views.dataset.tip.updateModeMessage'), {
            confirmButtonText: t('views.dataset.setting.vectorization')
          })
            .then(() => {
              if (detail.value.type === '2') {
                datasetApi.putLarkDataset(id, obj, loading).then((res) => {
                  datasetApi.putReEmbeddingDataset(id).then(() => {
                    MsgSuccess(t('common.saveSuccess'))
                  })
                })
              } else {
                datasetApi.putDataset(id, obj, loading).then((res) => {
                  datasetApi.putReEmbeddingDataset(id).then(() => {
                    MsgSuccess(t('common.saveSuccess'))
                  })
                })
              }
            })
            .catch(() => {})
        } else {
          if (detail.value.type === '2') {
            datasetApi.putLarkDataset(id, obj, loading).then((res) => {
              datasetApi.putReEmbeddingDataset(id).then(() => {
                MsgSuccess(t('common.saveSuccess'))
              })
            })
          } else {
            datasetApi.putDataset(id, obj, loading).then((res) => {
              MsgSuccess(t('common.saveSuccess'))
            })
          }
        }
      }
    })
  }
}

function getDetail() {
  dataset.asyncGetDatasetDetail(id, loading).then((res: any) => {
    detail.value = res.data
    cloneModelId.value = res.data?.embedding_mode_id
    if (detail.value.type === '1' || detail.value.type === '2') {
      form.value = res.data.meta
    }
    application_id_list.value = res.data?.application_id_list
    datasetApi.listUsableApplication(id, loading).then((ok) => {
      application_list.value = ok.data
    })
  })
}

onMounted(() => {
  getDetail()
})
</script>
<style lang="scss" scoped>
.dataset-setting {
  width: 70%;
  margin: 0 auto;
}
</style>
