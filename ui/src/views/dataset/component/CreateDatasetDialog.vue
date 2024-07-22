<template>
  <el-dialog title="创建知识库" v-model="dialogVisible" width="680" append-to-body>
    <!-- 基本信息 -->
    <BaseForm ref="BaseFormRef" v-if="dialogVisible" />
    <el-form
      ref="DatasetFormRef"
      :rules="rules"
      :model="datasetForm"
      label-position="top"
      require-asterisk-position="right"
    >
      <el-form-item label="知识库类型" required>
        <el-radio-group v-model="datasetForm.type" class="card__radio" @change="radioChange">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card
                shadow="never"
                class="mb-16"
                :class="datasetForm.type === '0' ? 'active' : ''"
              >
                <el-radio value="0" size="large">
                  <div class="flex align-center">
                    <AppAvatar class="mr-8 avatar-blue" shape="square" :size="32">
                      <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                    </AppAvatar>
                    <div>
                      <p class="mb-4">通用型</p>
                      <el-text type="info">上传本地文件或手动录入</el-text>
                    </div>
                  </div>
                </el-radio>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card
                shadow="never"
                class="mb-16"
                :class="datasetForm.type === '1' ? 'active' : ''"
              >
                <el-radio value="1" size="large">
                  <div class="flex align-center">
                    <AppAvatar class="mr-8 avatar-purple" shape="square" :size="32">
                      <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                    </AppAvatar>
                    <div>
                      <p class="mb-4">Web 站点</p>
                      <el-text type="info">同步Web网站文本数据 </el-text>
                    </div>
                  </div>
                </el-radio>
              </el-card>
            </el-col>
          </el-row>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="Web 根地址" prop="source_url" v-if="datasetForm.type === '1'">
        <el-input
          v-model="datasetForm.source_url"
          placeholder="请输入 Web 根地址"
          @blur="datasetForm.source_url = datasetForm.source_url.trim()"
        />
      </el-form-item>
      <el-form-item label="选择器" v-if="datasetForm.type === '1'">
        <el-input
          v-model="datasetForm.selector"
          placeholder="默认为 body，可输入 .classname/#idname/tagname"
          @blur="datasetForm.selector = datasetForm.selector.trim()"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false" :loading="loading">
          {{ $t('views.application.applicationForm.buttons.cancel') }}
        </el-button>
        <el-button type="primary" @click="submitValid" :loading="loading">
          {{ $t('views.application.applicationForm.buttons.create') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import BaseForm from './BaseForm.vue'
import datasetApi from '@/api/dataset'
import { MsgSuccess, MsgAlert } from '@/utils/message'
import useStore from '@/stores'
import { ValidType, ValidCount } from '@/enums/common'

const emit = defineEmits(['refresh'])

const { common, user } = useStore()
const router = useRouter()
const BaseFormRef = ref()
const DatasetFormRef = ref()

const loading = ref(false)
const dialogVisible = ref<boolean>(false)

const datasetForm = ref<any>({
  type: '0',
  source_url: '',
  selector: ''
})

const rules = reactive({
  source_url: [{ required: true, message: '请输入 Web 根地址', trigger: 'blur' }]
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    datasetForm.value = {
      type: '0',
      source_url: '',
      selector: ''
    }
    DatasetFormRef.value?.clearValidate()
  }
})

const open = () => {
  dialogVisible.value = true
}

const submitValid = () => {
  if (user.isEnterprise()) {
    submitHandle()
  } else {
    common.asyncGetValid(ValidType.Dataset, ValidCount.Dataset, loading).then(async (res: any) => {
      if (res?.data) {
        submitHandle()
      } else {
        MsgAlert('提示', '社区版最多支持 50 个知识库，如需拥有更多知识库，请升级为专业版。')
      }
    })
  }
}
const submitHandle = async () => {
  if (await BaseFormRef.value?.validate()) {
    await DatasetFormRef.value.validate((valid: any) => {
      if (valid) {
        if (datasetForm.value.type === '0') {
          const obj = {
            ...BaseFormRef.value.form,
            type: datasetForm.value.type
          }
          datasetApi.postDataset(obj, loading).then((res) => {
            MsgSuccess('创建成功')
            router.push({ path: `/dataset/${res.data.id}/document` })
            emit('refresh')
          })
        } else {
          const obj = { ...BaseFormRef.value.form, ...datasetForm.value }
          datasetApi.postWebDataset(obj, loading).then((res) => {
            MsgSuccess('创建成功')
            router.push({ path: `/dataset/${res.data.id}/document` })
            emit('refresh')
          })
        }
      } else {
        return false
      }
    })
  } else {
    return false
  }
}
function radioChange() {
  datasetForm.value.source_url = ''
  datasetForm.value.selector = ''
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
