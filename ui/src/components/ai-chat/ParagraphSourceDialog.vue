<template>
  <el-dialog
    class="paragraph-source"
    title="知识库引用"
    v-model="dialogVisible"
    destroy-on-close
    append-to-body
  >
    <div class="paragraph-source-height">
      <el-scrollbar>
        <div class="p-16">
          <el-form label-position="top">
            <el-form-item label="用户问题">
              <el-input v-model="detail.problem_text" disabled />
            </el-form-item>
            <el-form-item label="优化后问题">
              <el-input v-model="detail.padding_problem_text" disabled />
            </el-form-item>
            <el-form-item label="引用分段">
              <template v-for="(item, index) in detail.paragraph_list" :key="index">
                <CardBox
                  shadow="never"
                  :title="item.title || '-'"
                  class="paragraph-source-card cursor mb-8"
                  :class="item.is_active ? '' : 'disabled'"
                  :showIcon="false"
                >
                  <template #icon>
                    <AppAvatar class="mr-12 avatar-light" :size="22">
                      {{ index + 1 + '' }}</AppAvatar
                    >
                  </template>
                  <div class="active-button primary">{{ item.similarity?.toFixed(3) }}</div>
                  <template #description>
                    <el-scrollbar height="90">
                      {{ item.content }}
                    </el-scrollbar>
                  </template>
                  <template #footer>
                    <div class="footer-content flex-between">
                      <el-text>
                        <el-icon>
                          <Document />
                        </el-icon>
                        {{ item?.document_name }}
                      </el-text>
                      <div class="flex align-center">
                        <AppAvatar class="mr-8" shape="square" :size="18">
                          <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                        </AppAvatar>

                        <span class="ellipsis"> {{ item?.dataset_name }}</span>
                      </div>
                    </div>
                  </template>
                </CardBox>
              </template>
            </el-form-item>
          </el-form>
        </div>
      </el-scrollbar>
    </div>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { cloneDeep } from 'lodash'
import { arraySort } from '@/utils/utils'
const emit = defineEmits(['refresh'])

const ParagraphDialogRef = ref()
const dialogVisible = ref(false)
const detail = ref<any>({})

watch(dialogVisible, (bool) => {
  if (!bool) {
    detail.value = {}
  }
})

const open = (data: any, id?: string) => {
  detail.value = cloneDeep(data)
  detail.value.paragraph_list = id
    ? detail.value.paragraph_list.filter((v: any) => v.dataset_id === id)
    : detail.value.paragraph_list
  detail.value.paragraph_list = arraySort(detail.value.paragraph_list, 'similarity', true)
  dialogVisible.value = true
}

defineExpose({ open })
</script>
<style lang="scss">
.paragraph-source {
  padding: 0;
  .el-dialog__header {
    padding: 24px 24px 0 24px;
  }
  .el-dialog__body {
    padding: 8px !important;
  }
  .paragraph-source-height {
    height: calc(100vh - 260px);
  }
}
</style>
