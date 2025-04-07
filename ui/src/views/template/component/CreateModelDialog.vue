<template>
  <el-dialog
    v-model="dialogVisible"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
    append-to-body
  >
    <template #header="{ close, titleId, titleClass }">
      <el-breadcrumb separator=">">
        <el-breadcrumb-item>
          <span @click="toSelectProvider" class="select-provider">
            {{ $t('views.template.providerPlaceholder') }}
          </span>
        </el-breadcrumb-item>
        <el-breadcrumb-item
          ><span class="active-breadcrumb">{{
            `${$t('common.add')} ${providerValue?.name}`
          }}</span></el-breadcrumb-item
        >
      </el-breadcrumb>
    </template>
    <el-tabs v-model="activeName">
      <el-tab-pane :label="$t('views.template.templateForm.title.baseInfo')" name="base-info">
        <DynamicsForm
          v-model="form_data"
          :render_data="model_form_field"
          :model="form_data"
          ref="dynamicsFormRef"
          label-position="top"
          require-asterisk-position="right"
          class="mb-24"
          label-width="auto"
        >
          <template #default>
            <el-form-item prop="name" :rules="base_form_data_rule.name">
              <template #label>
                <div class="flex align-center" style="display: inline-flex">
                  <div class="mr-4">
                    <span> {{ $t('views.template.templateForm.form.templateName.label') }} </span>
                  </div>
                  <el-tooltip effect="dark" placement="right">
                    <template #content>
                      <p>{{ $t('views.template.templateForm.form.templateName.tooltip') }}</p>
                    </template>
                    <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                  </el-tooltip>
                </div>
              </template>
              <el-input
                v-model="base_form_data.name"
                maxlength="64"
                show-word-limit
                :placeholder="$t('views.template.templateForm.form.templateName.placeholder')"
              />
            </el-form-item>
            <el-form-item prop="permission_type" :rules="base_form_data_rule.permission_type">
              <template #label>
                <span>{{ $t('views.template.templateForm.form.permissionType.label') }}</span>
              </template>
              <el-radio-group v-model="base_form_data.permission_type" class="card__radio">
                <el-row :gutter="16">
                  <template v-for="(value, key) of PermissionType" :key="key">
                    <el-col :span="12">
                      <el-card
                        shadow="never"
                        class="mb-16"
                        :class="base_form_data.permission_type === key ? 'active' : ''"
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
            <el-form-item prop="model_type" :rules="base_form_data_rule.model_type">
              <template #label>
                <div class="flex align-center" style="display: inline-flex">
                  <span class="mr-4"
                    >{{ $t('views.template.templateForm.form.model_type.label') }}
                  </span>
                  <el-tooltip effect="dark" placement="right">
                    <template #content>
                      <p>{{ $t('views.template.templateForm.form.model_type.tooltip1') }}</p>
                      <p>{{ $t('views.template.templateForm.form.model_type.tooltip2') }}</p>
                      <p>{{ $t('views.template.templateForm.form.model_type.tooltip3') }}</p>
                      <p>{{ $t('views.template.templateForm.form.model_type.tooltip4') }}</p>
                      <p>{{ $t('views.template.templateForm.form.model_type.tooltip5') }}</p>
                      <p>{{ $t('views.template.templateForm.form.model_type.tooltip6') }}</p>
                      <p>{{ $t('views.template.templateForm.form.model_type.tooltip7') }}</p>
                    </template>
                    <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                  </el-tooltip>
                </div>
              </template>
              <el-select
                v-loading="model_type_loading"
                @change="list_base_model($event, true)"
                v-model="base_form_data.model_type"
                class="w-full m-2"
                :placeholder="$t('views.template.templateForm.form.model_type.placeholder')"
              >
                <el-option
                  v-for="item in model_type_list"
                  :key="item.value"
                  :label="item.key"
                  :value="item.value"
                ></el-option>
              </el-select>
            </el-form-item>

            <el-form-item prop="model_name" :rules="base_form_data_rule.model_name">
              <template #label>
                <div class="flex align-center" style="display: inline-flex">
                  <div class="mr-4">
                    <span>{{ $t('views.template.templateForm.form.base_model.label') }} </span>
                    <span class="danger ml-4">{{
                      $t('views.template.templateForm.form.base_model.tooltip')
                    }}</span>
                  </div>
                </div>
              </template>
              <el-select
                @change="getModelForm($event)"
                v-loading="base_model_loading"
                v-model="base_form_data.model_name"
                class="w-full m-2"
                :placeholder="$t('views.template.templateForm.form.base_model.placeholder')"
                filterable
                allow-create
                default-first-option
              >
                <el-option v-for="item in base_model_list" :key="item.name" :value="item.name">
                  <template #default>
                    <div class="flex align-center" style="display: inline-flex">
                      <div class="flex-between mr-4">
                        <span>{{ item.name }} </span>
                      </div>
                      <el-tooltip effect="dark" placement="right" v-if="item.desc">
                        <template #content>
                          <p class="w-280">{{ item.desc }}</p>
                        </template>
                        <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                      </el-tooltip>
                    </div>
                  </template>
                </el-option>
              </el-select>
            </el-form-item>
          </template>
        </DynamicsForm>
      </el-tab-pane>
      <el-tab-pane
        :label="$t('views.template.templateForm.title.advancedInfo')"
        name="advanced-info"
      >
        <el-empty
          v-if="!base_form_data.model_type || !base_form_data.model_name"
          :description="$t('views.template.tip.emptyMessage1')"
        />
        <el-empty
          v-else-if="
            base_form_data.model_type === 'RERANKER' ||
            base_form_data.model_type === 'EMBEDDING' ||
            base_form_data.model_type === 'STT'
          "
          :description="$t('views.template.tip.emptyMessage2')"
        />
        <div class="flex-between mb-8" v-else>
          <h5>{{ $t('views.template.templateForm.title.modelParams') }}</h5>
          <el-button
            type="text"
            @click.stop="openAddDrawer()"
            :disabled="
              base_form_data.model_type !== 'TTS' &&
              base_form_data.model_type !== 'LLM' &&
              base_form_data.model_type !== 'IMAGE' &&
              base_form_data.model_type !== 'TTI'
            "
          >
            <AppIcon iconName="Plus" class="add-icon" />{{ $t('common.add') }}
          </el-button>
        </div>
        <el-table
          :data="base_form_data.model_params_form"
          v-if="base_form_data.model_params_form?.length > 0"
          class="mb-16"
        >
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
            width="95px"
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
                    <el-icon><EditPen /></el-icon>
                  </el-button>
                </el-tooltip>
              </span>
              <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
                <el-button type="primary" text @click="deleteParam($index)">
                  <el-icon>
                    <Delete />
                  </el-icon>
                </el-button>
              </el-tooltip>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
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
import type { Provider, BaseModel } from '@/api/type/model'
import type { Dict, KeyValue } from '@/api/type/common'
import ModelApi from '@/api/model'
import type { FormField } from '@/components/dynamics-form/type'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import type { FormRules } from 'element-plus'
import { MsgError, MsgSuccess, MsgWarning } from '@/utils/message'
import { PermissionType, PermissionDesc } from '@/enums/model'
import { input_type_list } from '@/components/dynamics-form/constructor/data'
import AddParamDrawer from '@/views/template/component/AddParamDrawer.vue'
import { t } from '@/locales'

const providerValue = ref<Provider>()
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const emit = defineEmits(['change', 'submit'])
const loading = ref<boolean>(false)
const model_type_loading = ref<boolean>(false)
const base_model_loading = ref<boolean>(false)
const model_type_list = ref<Array<KeyValue<string, string>>>([])

const base_model_list = ref<Array<BaseModel>>()
const model_form_field = ref<Array<FormField>>([])
const dialogVisible = ref<boolean>(false)
const activeName = ref('base-info')
const AddParamRef = ref()

const base_form_data_rule = ref<FormRules>({
  name: {
    required: true,
    trigger: 'blur',
    message: t('views.template.templateForm.form.templateName.requiredMessage')
  },
  permission_type: {
    required: true,
    trigger: 'change',
    message: t('views.template.templateForm.form.permissionType.requiredMessage')
  },
  model_type: {
    required: true,
    trigger: 'change',
    message: t('views.template.templateForm.form.model_type.requiredMessage')
  },
  model_name: {
    required: true,
    trigger: 'change',
    message: t('views.template.templateForm.form.base_model.requiredMessage')
  }
})

const base_form_data = ref<{
  name: string
  permission_type: string
  model_type: string
  model_name: string
  model_params_form: any
}>({ name: '', model_type: '', model_name: '', permission_type: 'PRIVATE', model_params_form: [] })

const credential_form_data = ref<Dict<any>>({})

const form_data = computed({
  get: () => {
    return {
      ...credential_form_data.value,
      name: base_form_data.value.name,
      model_type: base_form_data.value.model_type,
      model_name: base_form_data.value.model_name,
      permission_type: base_form_data.value.permission_type,
      model_params_form: base_form_data.value.model_params_form
    }
  },
  set: (event: any) => {
    credential_form_data.value = event
  }
})

const getModelForm = (model_name: string) => {
  if (!form_data.value.model_type) {
    MsgWarning(t('views.template.templateForm.form.model_type.requiredMessage'))
    base_form_data.value.model_name = ''
    return
  }
  if (providerValue.value) {
    ModelApi.getModelCreateForm(
      providerValue.value.provider,
      form_data.value.model_type,
      model_name
    ).then((ok) => {
      model_form_field.value = ok.data
      // 渲染动态表单
      dynamicsFormRef.value?.render(model_form_field.value, undefined)
    })

    ModelApi.listBaseModelParamsForm(
      providerValue.value.provider,
      form_data.value.model_type,
      model_name,
      base_model_loading
    ).then((ok) => {
      base_form_data.value.model_params_form = ok.data
    })
  }
}

const open = (provider: Provider, model_type?: string) => {
  ModelApi.listModelType(provider.provider, model_type_loading).then((ok) => {
    model_type_list.value = ok.data
  })
  providerValue.value = provider
  dialogVisible.value = true
  base_form_data.value.model_type = model_type || ''
  activeName.value = 'base-info'
  if (model_type) {
    list_base_model(model_type)
  }
}

const list_base_model = (model_type: any, change?: boolean) => {
  if (change) {
    base_form_data.value.model_name = ''
    base_form_data.value.model_params_form = []
  }
  if (providerValue.value) {
    ModelApi.listBaseModel(providerValue.value.provider, model_type, base_model_loading).then(
      (ok) => {
        base_model_list.value = ok.data
      }
    )
  }
}

const close = () => {
  base_form_data.value = {
    name: '',
    model_type: '',
    model_name: '',
    permission_type: 'PRIVATE',
    model_params_form: []
  }
  credential_form_data.value = {}
  model_form_field.value = []
  base_model_list.value = []
  loading.value = false
  dialogVisible.value = false
}
const submit = () => {
  dynamicsFormRef.value
    ?.validate()
    .then(() => {
      if (providerValue.value) {
        ModelApi.createModel(
          {
            ...base_form_data.value,
            credential: credential_form_data.value,
            provider: providerValue.value.provider
          },
          loading
        ).then((ok) => {
          close()
          MsgSuccess(t('views.template.tip.createSuccessMessage'))
          emit('submit')
        })
      }
    })
    .catch(() => {
      MsgError(t('views.template.tip.createErrorMessage'))
    })
}

function openAddDrawer(data?: any, index?: any) {
  AddParamRef.value?.open(data, index)
}

function deleteParam(index: any) {
  base_form_data.value.model_params_form.splice(index, 1)
}

function refresh(data: any, index: any) {
  for (let i = 0; i < base_form_data.value.model_params_form.length; i++) {
    let field = base_form_data.value.model_params_form[i].field
    let label = base_form_data.value.model_params_form[i].label
    if (label && label.input_type === 'TooltipLabel') {
      label = label.label
    }
    let label2 = data.label
    if (label2 && label2.input_type === 'TooltipLabel') {
      label2 = label2.label
    }

    if (field === data.field && index !== i) {
      MsgError(t('views.template.tip.errorMessage') + data.field)
      return
    }
    if (label === label2 && index !== i) {
      MsgError(t('views.template.tip.errorMessage') + label)
      return
    }
  }
  if (index !== null) {
    base_form_data.value.model_params_form.splice(index, 1, data)
  } else {
    base_form_data.value.model_params_form.push(data)
  }
}

const toSelectProvider = () => {
  close()
  emit('change')
}
defineExpose({ open, close })
</script>
<style lang="scss" scoped>
.select-provider {
  font-size: 16px;
  color: rgba(100, 106, 115, 1);
  font-weight: 400;
  line-height: 24px;
  cursor: pointer;

  &:hover {
    color: var(--el-color-primary);
  }
}

.active-breadcrumb {
  font-size: 16px;
  color: rgba(31, 35, 41, 1);
  font-weight: 500;
  line-height: 24px;
}
</style>
