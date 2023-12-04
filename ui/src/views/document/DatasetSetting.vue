<template>
  <LayoutContainer header="设置">
    <div class="dataset-setting main-calc-height">
      <el-scrollbar>
        <div class="p-24" v-loading="loading">
          <BaseForm ref="BaseFormRef" :data="detail" />

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
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import BaseForm from '@/views/dataset/component/BaseForm.vue'
import datasetApi from '@/api/dataset'
import type { ApplicationFormType } from '@/api/type/application'
import { MsgSuccess } from '@/utils/message'
const route = useRoute()
const {
  params: { id }
} = route as any

const BaseFormRef = ref()
const loading = ref(false)
const detail = ref({})

const application_list = ref<Array<ApplicationFormType>>([])
const application_id_list = ref([])

async function submit() {
  if (await BaseFormRef.value?.validate()) {
    loading.value = true
    const obj = {
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
}

function getDetail() {
  loading.value = true
  datasetApi
    .getDatesetDetail(id)
    .then((res) => {
      detail.value = res.data
      application_id_list.value = res.data?.application_id_list
      datasetApi.listUsableApplication(id, loading).then((ok) => {
        application_list.value = ok.data
        loading.value = false
      })
    })
    .catch(() => {
      loading.value = false
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
