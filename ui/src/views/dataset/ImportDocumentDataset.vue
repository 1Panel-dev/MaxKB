<template>
  <LayoutContainer :header="$t('views.document.importDocument')" class="create-dataset">
    <template #backButton>
      <back-button @click="back"></back-button>
    </template>
    <div class="create-dataset__main flex" v-loading="loading">
      <div class="create-dataset__component main-calc-height">
        <el-scrollbar>
          <div class="upload-document p-24">
            <h4 class="title-decoration-1 mb-8">
              {{ $t('views.document.feishu.selectDocument') }}
            </h4>
            <el-form
              ref="FormRef"
              :model="form"
              :rules="rules"
              label-position="top"
              require-asterisk-position="right"
            >
              <div class="mt-16 mb-16">
                <el-radio-group v-model="form.fileType" class="app-radio-button-group">
                  <el-radio-button value="txt">{{
                    $t('views.document.fileType.txt.label')
                  }}</el-radio-button>
                </el-radio-group>
              </div>
              <div class="update-info flex p-8-12 border-r-4 mb-16">
                <div class="mt-4">
                  <AppIcon iconName="app-warning-colorful" style="font-size: 16px"></AppIcon>
                </div>
                <div class="ml-16 lighter">
                  <p>{{ $t('views.document.feishu.tip1') }}</p>
                  <p>{{ $t('views.document.feishu.tip2') }}</p>
                </div>
              </div>
              <div class="card-never border-r-4 mb-16">
                <el-checkbox
                  v-model="allCheck"
                  :label="$t('views.document.feishu.allCheck')"
                  size="large"
                  class="ml-24"
                />
              </div>

              <el-tree :props="props" :load="loadNode" lazy show-checkbox />
            </el-form>
          </div>
        </el-scrollbar>
      </div>
    </div>
    <div class="create-dataset__footer text-right border-t">
      <el-button @click="router.go(-1)">{{ $t('common.cancel') }}</el-button>

      <el-button @click="submit" type="primary">
        {{ $t('views.document.buttons.import') }}
      </el-button>
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, reactive, computed, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

import documentApi from '@/api/document'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import type Node from 'element-plus/es/components/tree/src/model/node'

interface Tree {
  name: string
  leaf?: boolean
}
const router = useRouter()
const route = useRoute()
const {
  query: { id } // id为datasetID，有id的是上传文档
} = route

const loading = ref(false)
const disabled = ref(false)
const allCheck = ref(false)
const form = ref({
  fileType: 'txt',
  fileList: [] as any
})

const rules = reactive({
  fileList: [
    { required: true, message: t('views.document.upload.requiredMessage'), trigger: 'change' }
  ]
})

const props = {
  label: 'name',
  children: 'zones',
  isLeaf: 'leaf'
}

const loadNode = (node: Node, resolve: (data: Tree[]) => void) => {
  if (node.level === 0) {
    return resolve([{ name: 'region' }])
  }
  if (node.level > 1) return resolve([])

  setTimeout(() => {
    const data: Tree[] = [
      {
        name: 'leaf',
        leaf: true
      },
      {
        name: 'zone'
      }
    ]

    resolve(data)
  }, 500)
}

function submit() {
  loading.value = true
}
function back() {
  router.go(-1)
}
</script>
<style lang="scss" scoped>
.create-dataset {
  &__component {
    width: 100%;
    margin: 0 auto;
    overflow: hidden;
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
  .upload-document {
    width: 70%;
    margin: 0 auto;
    margin-bottom: 20px;
  }
}
</style>
