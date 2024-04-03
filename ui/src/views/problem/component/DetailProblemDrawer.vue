<template>
  <el-drawer v-model="visible" size="60%" @close="closeHandel">
    <template #header>
      <h4>问题详情</h4>
    </template>
    <div class="paragraph-source-height">
      <!-- <el-scrollbar>
        <div class="p-16">
          <el-form label-position="top">
            <el-form-item label="问题">
              <el-input v-model="detail.problem_text" disabled />
            </el-form-item>
            <el-form-item label="关联分段">
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
      </el-scrollbar> -->
    </div>
    <template #footer>
      <div>
        <el-button @click="pre" :disabled="pre_disable || loading">上一条</el-button>
        <el-button @click="next" :disabled="next_disable || loading">下一条</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import problemApi from '@/api/problem'
import { type chatType } from '@/api/type/application'

const props = withDefaults(
  defineProps<{
    /**
     * 当前的id
     */
    currentId: string
    currentContent: string
    /**
     * 下一条
     */
    next: () => void
    /**
     * 上一条
     */
    pre: () => void

    pre_disable: boolean

    next_disable: boolean
  }>(),
  {}
)

const emit = defineEmits(['update:currentId', 'update:currentContent', 'refresh'])

const route = useRoute()
const {
  params: { id }
} = route
const loading = ref(false)
const visible = ref(false)
const paragraphList = ref<chatType[]>([])

function closeHandel() {
  paragraphList.value = []
}

function getRecord() {
  if (props.currentId && visible.value) {
    problemApi.getDetailProblems(id as string, props.currentId, loading).then((res) => {
      paragraphList.value = res.data.records
    })
  }
}

watch(
  () => props.currentId,
  () => {
    paragraphList.value = []
    getRecord()
  }
)

watch(visible, (bool) => {
  if (!bool) {
    emit('update:currentId', '')
    emit('update:currentContent', '')
    emit('refresh')
  }
})

const open = () => {
  getRecord()
  visible.value = true
}

defineExpose({
  open
})
</script>
<style lang="scss"></style>
