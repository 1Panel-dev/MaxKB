<template>
  <el-dialog
    class="paragraph-source"
    title="知识库引用"
    v-model="dialogVisible"
    destroy-on-close
    append-to-body
  >
    <el-scrollbar height="450">
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
                  <AppAvatar :name="index + 1 + ''" class="mr-12 avatar-light" :size="22" />
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
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { cloneDeep } from 'lodash'
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
  dialogVisible.value = true
}

defineExpose({ open })
</script>
<style lang="scss">
.paragraph-source {
  .el-dialog__body {
    padding: 8px !important;
  }
}
.paragraph-source-card {
  height: 210px;
  width: 100%;
  .active-button {
    position: absolute;
    right: 16px;
    top: 16px;
  }
}
</style>
