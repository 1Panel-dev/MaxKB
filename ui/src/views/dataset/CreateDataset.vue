<template>
  <LayoutContainer header="创建数据集" back-to="-1" class="create-dataset">
    <template #header>
      <el-steps :active="active" finish-status="success" align-center class="create-dataset__steps">
        <el-step v-for="(item, index) in steps" :key="index">
          <template #icon>
            <div class="app-step">
              <div class="el-step__icon is-text">
                <div class="el-step__icon-inner">{{ index + 1 }}</div>
              </div>
              {{ item.name }}
            </div>
          </template>
        </el-step>
      </el-steps>
    </template>
    <div class="create-dataset__main flex">
      <div class="create-dataset__component">
        <component :is="steps[active].component" :ref="steps[active]?.ref" />
      </div>
    </div>
    <div class="create-dataset__footer text-right border-t">
      <el-button @click="router.go(-1)">取 消</el-button>
      <el-button @click="prev">上一步</el-button>
      <el-button @click="next" type="primary">下一步</el-button>
      <el-button @click="next" type="primary">开始导入</el-button>
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import UploadDocument from './step/UploadDocument.vue'
import SetRules from './step/SetRules.vue'

const router = useRouter()

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
const prev = () => {
  active.value = 0
}
</script>
<style lang="scss" scoped>
.create-dataset {
  &__steps {
    min-width: 450px;
    max-width: 800px;
    width: 80%;
    margin: 0 auto;
    padding-right: 60px;

    :deep(.el-step__line) {
      left: 64% !important;
      right: -33% !important;
    }
  }

  &__component {
    width: 100%;
    height: var(--create-dataset-height);
    margin: 0 auto;
    overflow: hidden;
    box-sizing: border-box;
  }
  &__footer {
    padding: 16px 24px;
    position: fixed;
    bottom: 0;
    left: 0;
    background: #ffffff;
    width: 100%;
    box-sizing: border-box;
  }
}
</style>
