<template>
  <LayoutContainer header="设置">
    <div class="dataset-setting">
      <div class="p-24" v-loading="loading">
        <BaseForm ref="BaseFormRef" :data="detail" />
        <div class="text-right">
          <el-button @click="submit" type="primary"> 保存 </el-button>
        </div>
      </div>
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import BaseForm from '@/views/dataset/component/BaseForm.vue'
import datasetApi from '@/api/dataset'
import { MsgSuccess } from '@/utils/message'
const route = useRoute()
const {
  params: { id }
} = route as any

const BaseFormRef = ref()
const loading = ref(false)
const detail = ref({})

async function submit() {
  if (await BaseFormRef.value?.validate()) {
    loading.value = true
    datasetApi
      .putDateset(id, BaseFormRef.value.form)
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
      loading.value = false
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
