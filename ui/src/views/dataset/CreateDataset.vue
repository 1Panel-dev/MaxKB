<template>
  <LayoutContent header="创建数据集" back-to="-1">
    <div class="create-dataset flex main-calc-height">
      <div class="p-24">
        <el-steps :active="active" finish-status="success" align-center>
          <el-step v-for="(item, index) in steps" :key="index" :title="item.name" />
        </el-steps>
      </div>
      <div class="create-dataset__component p-24">
        <el-scrollbar>
          <component :is="steps[active].component" :ref="steps[active]?.ref" />
        </el-scrollbar>
      </div>
      <div class="create-dataset__footer text-right p-24 border-t">
        <el-button @click="next">取 消</el-button>
        <el-button @click="prev">上一步</el-button>
        <el-button @click="next" type="primary">下一步</el-button>
        <el-button @click="next" type="primary">开始导入</el-button>
      </div>
    </div>
  </LayoutContent>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import UploadDocument from './step/UploadDocument.vue'
import SetRules from './step/SetRules.vue'

const steps = [
  {
    ref: 'UploadDocumentRef',
    name: '上传文档',
    component: UploadDocument
  },
  {
    ref: 'SetRulesRef',
    name: '设置分段规则',
    component: SetRules
  }
]

const UploadDocumentRef = ref()

const active = ref(0)

async function next() {
  if (await UploadDocumentRef.value.onSubmit()) {
    if (active.value++ > 2) active.value = 0
  }
}
const prev = () => {}
</script>
<style lang="scss" scoped>
.create-dataset {
  flex-direction: column;
  // height: 100%;
  &__component {
    flex: 1;
    flex-basis: auto;
    min-width: 70%;
    margin: 0 auto;
    overflow: hidden;
  }
  &__footer {
    flex: 0 0 auto;
  }
}
</style>
