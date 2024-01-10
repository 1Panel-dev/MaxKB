<template>
  <el-scrollbar>
    <div class="upload-document p-24">
      <!-- 基本信息 -->
      <BaseForm ref="BaseFormRef" v-if="isCreate" />
      <el-form
        ref="webFormRef"
        :rules="rules"
        :model="form"
        label-position="top"
        require-asterisk-position="right"
      >
        <el-form-item label="知识库类型" required>
          <el-radio-group v-model="form.type" class="card__radio" @change="radioChange">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card shadow="never" class="mb-16" :class="form.type === '0' ? 'active' : ''">
                  <el-radio label="0" size="large">
                    <div class="flex align-center">
                      <el-icon size="32" class="mr-8 info"><Document /></el-icon>
                      <div>
                        <p class="mb-4">通用型</p>
                        <el-text type="info">可以通过上传文件或手动录入方式构建知识库</el-text>
                      </div>
                    </div>
                  </el-radio>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card shadow="never" class="mb-16" :class="form.type === '1' ? 'active' : ''">
                  <el-radio label="1" size="large">
                    <div class="flex align-center">
                      <el-icon size="32" class="mr-8 info"><Monitor /></el-icon>
                      <div>
                        <p class="mb-4">Web 站点</p>
                        <el-text type="info"> 通过网站链接同步方式构建知识库 </el-text>
                      </div>
                    </div>
                  </el-radio>
                </el-card>
              </el-col>
            </el-row>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Web 根地址" prop="url" v-if="form.type === '1'">
          <el-input
            v-model="form.url"
            placeholder="请输入 Web 根地址"
            @blur="form.url = form.url.trim()"
          />
        </el-form-item>
        <el-form-item label="选择器" v-if="form.type === '1'">
          <el-input
            v-model="form.selector"
            placeholder="请输入选择器"
            @blur="form.selector = form.selector.trim()"
          />
        </el-form-item>
      </el-form>

      <!-- 上传文档 -->
      <UploadComponent ref="UploadComponentRef" v-if="form.type === '0'" />
    </div>
  </el-scrollbar>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import BaseForm from '@/views/dataset/component/BaseForm.vue'
import UploadComponent from '@/views/dataset/component/UploadComponent.vue'
import { isAllPropertiesEmpty } from '@/utils/utils'
import datasetApi from '@/api/dataset'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import useStore from '@/stores'
const { dataset } = useStore()

const route = useRoute()
const router = useRouter()
const {
  params: { type }
} = route
const isCreate = type === 'create'
const BaseFormRef = ref()
const UploadComponentRef = ref()
const webFormRef = ref()
const loading = ref(false)

const form = ref<any>({
  type: '0',
  url: '',
  selector: ''
})

const rules = reactive({
  url: [{ required: true, message: '请输入 Web 根地址', trigger: 'blur' }]
})

watch(form.value, (value) => {
  if (isAllPropertiesEmpty(value)) {
    dataset.saveWebInfo(null)
  } else {
    dataset.saveWebInfo(value)
  }
})

function radioChange() {
  dataset.saveDocumentsFile([])
  form.value.url = ''
  form.value.selector = ''
}

const onSubmit = async () => {
  if (isCreate) {
    if (form.value.type === '0') {
      if ((await BaseFormRef.value?.validate()) && (await UploadComponentRef.value.validate())) {
        /*
        stores保存数据
      */
        dataset.saveBaseInfo(BaseFormRef.value.form)
        dataset.saveDocumentsFile(UploadComponentRef.value.form.fileList)
        return true
      } else {
        return false
      }
    } else {
      if (await BaseFormRef.value?.validate()) {
        await webFormRef.value.validate((valid: any) => {
          if (valid) {
            const obj = { ...BaseFormRef.value.form, ...form.value }
            datasetApi.postWebDateset(obj, loading).then((res) => {
              MsgSuccess('提交成功')
              dataset.saveBaseInfo(null)
              dataset.saveWebInfo(null)
              router.push({ path: `/dataset/${res.data.id}/document` })
            })
          } else {
            return false
          }
        })
      } else {
        return false
      }
    }
  } else {
    if (await UploadComponentRef.value.validate()) {
      /*
        stores保存数据
      */
      dataset.saveDocumentsFile(UploadComponentRef.value.form.fileList)
      return true
    } else {
      return false
    }
  }
}

onMounted(() => {})

defineExpose({
  onSubmit
})
</script>
<style scoped lang="scss">
.upload-document {
  width: 70%;
  margin: 0 auto;
  margin-bottom: 20px;
}
</style>
