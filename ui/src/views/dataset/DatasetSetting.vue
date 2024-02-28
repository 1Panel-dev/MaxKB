<template>
  <LayoutContainer header="设置">
    <div class="dataset-setting main-calc-height">
      <el-scrollbar>
        <div class="p-24" v-loading="loading">
          <BaseForm ref="BaseFormRef" :data="detail" />

          <el-form
            ref="webFormRef"
            :rules="rules"
            :model="form"
            label-position="top"
            require-asterisk-position="right"
          >
            <el-form-item label="知识库类型" required>
              <el-card shadow="never" class="mb-8" v-if="detail.type === '0'">
                <div class="flex align-center">
                  <AppAvatar class="mr-8" shape="square" :size="32">
                    <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                  </AppAvatar>
                  <div>
                    <div>通用型</div>
                    <el-text type="info">可以通过上传文件或手动录入方式构建知识库</el-text>
                  </div>
                </div>
              </el-card>
              <el-card shadow="never" class="mb-8" v-if="detail?.type === '1'">
                <div class="flex align-center">
                  <AppAvatar class="mr-8 avatar-purple" shape="square" :size="32">
                    <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                  </AppAvatar>
                  <div>
                    <div>Web 站点</div>
                    <el-text type="info"> 通过网站链接同步方式构建知识库 </el-text>
                  </div>
                </div>
              </el-card>
            </el-form-item>
            <el-form-item label="Web 根地址" prop="source_url" v-if="detail.type === '1'">
              <el-input
                v-model="form.source_url"
                placeholder="请输入 Web 根地址"
                @blur="form.source_url = form.source_url.trim()"
              />
            </el-form-item>
            <el-form-item label="选择器" v-if="detail.type === '1'">
              <el-input
                v-model="form.selector"
                placeholder="默认为 body，可输入 .classname/#idname/tagname"
                @blur="form.selector = form.selector.trim()"
              />
            </el-form-item>
          </el-form>

          <h4 class="title-decoration-1 mb-16">关联应用</h4>

          <el-row :gutter="12">
            <el-col :span="12" v-for="(item, index) in application_list" :key="index" class="mb-16">
              <CardCheckbox value-field="id" :data="item" v-model="application_id_list">
                <template #icon>
                  <AppAvatar
                    v-if="item.name"
                    :name="item.name"
                    pinyinColor
                    class="mr-12"
                    shape="square"
                    :size="32"
                  />
                </template>
                {{ item.name }}
              </CardCheckbox>
            </el-col>
          </el-row>

          <div class="text-right">
            <el-button @click="submit" type="primary"> 保存 </el-button>
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
import { MsgSuccess } from '@/utils/message'
import useStore from '@/stores'
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
const form = ref<any>({
  source_url: '',
  selector: ''
})

const rules = reactive({
  source_url: [{ required: true, message: '请输入 Web 根地址', trigger: 'blur' }]
})

async function submit() {
  if (await BaseFormRef.value?.validate()) {
    await webFormRef.value.validate((valid: any) => {
      if (valid) {
        loading.value = true
        const obj =
          detail.value.type === '1'
            ? {
                application_id_list: application_id_list.value,
                meta: form.value,
                ...BaseFormRef.value.form
              }
            : {
                application_id_list: application_id_list.value,
                ...BaseFormRef.value.form
              }
        datasetApi
          .putDateset(id, obj)
          .then((res) => {
            MsgSuccess('保存成功')
            loading.value = false
          })
          .catch(() => {
            loading.value = false
          })
      }
    })
  }
}

function getDetail() {
  dataset.asyncGetDatesetDetail(id, loading).then((res: any) => {
    detail.value = res.data
    if (detail.value.type === '1') {
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
