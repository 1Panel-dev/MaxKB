<template>
  <div class="set-rules">
    <el-row>
      <el-col :span="12">
        <h4 class="title-decoration-1 mb-10">分段规则</h4>
        <el-radio-group v-model="radio1" class="set-rules__radio">
          <div>
            <el-radio label="1" size="large">智能分段（推荐）</el-radio>
          </div>
          <div>
            <el-radio label="2" size="large">高级分段</el-radio>
          </div>
        </el-radio-group>
        <div>
          <el-button @click="splitDocument">生成预览</el-button>
        </div>
      </el-col>

      <el-col :span="12">
        <h4 class="title-decoration-1 mb-10">分段预览</h4>
        <SegmentPreview />
      </el-col>
    </el-row>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import SegmentPreview from '@/views/dataset/component/SegmentPreview.vue'
import DatasetApi from '@/api/dataset'
import useStore from '@/stores'
const { dataset } = useStore()
const documentsFiles = computed(() => dataset.documentsFiles)

const radio1 = ref('1')
const loading = ref(false)

function splitDocument() {
  loading.value = true
  let fd = new FormData()
  console.log(documentsFiles.value)
  documentsFiles.value.forEach((item) => {
    if (item?.raw) {
      fd.append('file', item?.raw)
    }
  })

  DatasetApi.postSplitDocument(fd)
    .then((res) => {
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

onMounted(() => {})
</script>
<style scoped lang="scss">
.set-rules {
  &__radio {
    display: block;
  }
}
</style>
