<template>
  <div class="p-16-24">
    <h2 class="mb-16">{{ $t('common.setting') }}</h2>
    <el-card style="--el-card-padding: 0">
      <div class="knowledge-setting main-calc-height">
        <el-scrollbar>
          <div class="p-24" v-loading="loading">
            <h4 class="title-decoration-1 mb-16">
              {{ $t('common.info') }}
            </h4>
            <BaseForm ref="BaseFormRef" :data="detail"/>

            <el-form
              ref="webFormRef"
              :rules="rules"
              :model="form"
              label-position="top"
              require-asterisk-position="right"
            >
              <el-form-item :label="$t('views.knowledge.knowledgeType.label')" required>
                <el-card shadow="never" class="mb-8" style="width: 50%" v-if="detail.type === 0">
                  <div class="flex align-center">
                    <el-avatar class="mr-8 avatar-blue" shape="square" :size="32">
                      <img src="@/assets/knowledge/icon_document.svg" style="width: 58%" alt=""/>
                    </el-avatar>
                    <div>
                      <div>{{ $t('views.knowledge.knowledgeType.generalKnowledge') }}</div>
                      <el-text type="info"
                      >{{ $t('views.knowledge.knowledgeType.generalInfo') }}
                      </el-text>
                    </div>
                  </div>
                </el-card>
                <el-card shadow="never" class="mb-8" style="width: 50%" v-if="detail?.type === 1">
                  <div class="flex align-center">
                    <el-avatar class="mr-8 avatar-purple" shape="square" :size="32">
                      <img src="@/assets/knowledge/icon_web.svg" style="width: 58%" alt=""/>
                    </el-avatar>
                    <div>
                      <div>{{ $t('views.knowledge.knowledgeType.webKnowledge') }}</div>
                      <el-text type="info">
                        {{ $t('views.knowledge.knowledgeType.webInfo') }}
                      </el-text>
                    </div>
                  </div>
                </el-card>
                <el-card shadow="never" class="mb-8" style="width: 50%" v-if="detail?.type === 2">
                  <div class="flex align-center">
                    <el-avatar shape="square" :size="32" style="background: none">
                      <img src="@/assets/knowledge/logo_lark.svg" style="width: 100%" alt=""/>
                    </el-avatar>
                    <div>
                      <p>
                        <el-text>{{ $t('views.knowledge.knowledgeType.larkKnowledge') }}</el-text>
                      </p>
                      <el-text type="info"
                      >{{ $t('views.knowledge.knowledgeType.larkInfo') }}
                      </el-text>
                    </div>
                  </div>
                </el-card>
              </el-form-item>
              <el-form-item
                :label="$t('views.knowledge.form.source_url.label')"
                prop="source_url"
                v-if="detail.type === 1"
              >
                <el-input
                  v-model="form.source_url"
                  :placeholder="$t('views.knowledge.form.source_url.placeholder')"
                  @blur="form.source_url = form.source_url.trim()"
                />
              </el-form-item>
              <el-form-item
                :label="$t('views.knowledge.form.selector.label')"
                v-if="detail.type === 1"
              >
                <el-input
                  v-model="form.selector"
                  :placeholder="$t('views.knowledge.form.selector.placeholder')"
                  @blur="form.selector = form.selector.trim()"
                />
              </el-form-item>
              <el-form-item label="App ID" prop="app_id" v-if="detail.type === 2">
                <el-input
                  v-model="form.app_id"
                  :placeholder="
                    $t('views.application.applicationAccess.larkSetting.appIdPlaceholder')
                  "
                />
              </el-form-item>
              <el-form-item label="App Secret" prop="app_id" v-if="detail.type === 2">
                <el-input
                  v-model="form.app_secret"
                  type="password"
                  show-password
                  :placeholder="
                    $t('views.application.applicationAccess.larkSetting.appSecretPlaceholder')
                  "
                />
              </el-form-item>
              <el-form-item label="Folder Token" prop="folder_token" v-if="detail.type === 2">
                <el-input
                  v-model="form.folder_token"
                  :placeholder="
                    $t('views.application.applicationAccess.larkSetting.folderTokenPlaceholder')
                  "
                />
              </el-form-item>
            </el-form>
            <div v-if="application_id_list.length > 0">
              <h4 class="title-decoration-1 mb-16">
                {{ $t('views.dataset.relatedApplications') }}
              </h4>
              <el-row :gutter="12">
                <el-col
                  :span="12"
                  v-for="(item, index) in application_list.filter((obj: any) =>
                    application_id_list.some((v: any) => v === obj?.id),
                  )"
                  :key="index"
                  class="mb-16"
                >
                  <el-card shadow="never">
                    <div class="flex-between">
                      <div class="flex align-center">
                        <el-avatar
                          v-if="isAppIcon(item?.icon)"
                          shape="square"
                          :size="32"
                          style="background: none"
                          class="mr-12"
                        >
                          <img :src="item?.icon" alt=""/>
                        </el-avatar>
                        <el-avatar
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
    </el-card>
  </div>
</template>
<script setup lang="ts">
import {ref, onMounted, reactive} from 'vue'
import {useRoute} from 'vue-router'
import BaseForm from '@/views/knowledge/component/BaseForm.vue'
import KnowledgeApi from '@/api/knowledge/knowledge'
import type {ApplicationFormType} from '@/api/type/application'
import {MsgSuccess, MsgConfirm} from '@/utils/message'
import {isAppIcon} from '@/utils/common'
import useStore from '@/stores'
import {t} from '@/locales'

const route = useRoute()
const {
  params: {id},
} = route as any

const {knowledge} = useStore()
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
  folder_token: '',
})

const rules = reactive({
  source_url: [
    {
      required: true,
      message: t('views.knowledge.form.source_url.requiredMessage'),
      trigger: 'blur',
    },
  ],
  app_id: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.appIdPlaceholder'),
      trigger: 'blur',
    },
  ],
  app_secret: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.appSecretPlaceholder'),
      trigger: 'blur',
    },
  ],
  folder_token: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.folderTokenPlaceholder'),
      trigger: 'blur',
    },
  ],
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
              ...BaseFormRef.value.form,
            }
            : {
              application_id_list: application_id_list.value,
              ...BaseFormRef.value.form,
            }

        if (cloneModelId.value !== BaseFormRef.value.form.embedding_mode_id) {
          MsgConfirm(t('common.tip'), t('views.knowledge.tip.updateModeMessage'), {
            confirmButtonText: t('views.knowledge.setting.vectorization'),
          })
            .then(() => {
              if (detail.value.type === 2) {
                KnowledgeApi.putLarkDataset(id, obj, loading).then((res) => {
                  KnowledgeApi.putReEmbeddingDataset(id).then(() => {
                    MsgSuccess(t('common.saveSuccess'))
                  })
                })
              } else {
                KnowledgeApi.putKnowledge(id, obj, loading).then((res) => {
                  KnowledgeApi.putReEmbeddingDataset(id).then(() => {
                    MsgSuccess(t('common.saveSuccess'))
                  })
                })
              }
            })
            .catch(() => {
            })
        } else {
          if (detail.value.type === 2) {
            KnowledgeApi.putLarkDataset(id, obj, loading).then((res) => {
              KnowledgeApi.putReEmbeddingDataset(id).then(() => {
                MsgSuccess(t('common.saveSuccess'))
              })
            })
          } else {
            KnowledgeApi.putKnowledge(id, obj, loading).then((res) => {
              MsgSuccess(t('common.saveSuccess'))
            })
          }
        }
      }
    })
  }
}

function getDetail() {
  knowledge.asyncGetDatasetDetail(id, loading).then((res: any) => {
    detail.value = res.data
    cloneModelId.value = res.data?.embedding_mode_id
    if (detail.value.type === '1' || detail.value.type === '2') {
      form.value = res.data.meta
    }
    application_id_list.value = res.data?.application_id_list
    KnowledgeApi.listUsableApplication(id, loading).then((ok) => {
      application_list.value = ok.data
    })
  })
}

onMounted(() => {
  getDetail()
})
</script>
<style lang="scss" scoped>
.knowledge-setting {
  width: 70%;
  margin: 0 auto;
}
</style>
