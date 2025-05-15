<template>
  <el-drawer v-model="visibleInternalDesc" size="60%" :append-to-body="true">
    <template #header>
      <div class="flex align-center" style="margin-left: -8px">
        <el-button class="cursor mr-4" link @click.prevent="visibleInternalDesc = false">
          <el-icon :size="20">
            <Back />
          </el-icon>
        </el-button>
        <h4>详情</h4>
      </div>
    </template>

    <div>
      <div class="card-header">
        <div class="flex-between">
          <div class="title flex align-center">
            <AppAvatar
              v-if="isAppIcon(functionDetail?.icon)"
              shape="square"
              :size="64"
              style="background: none"
              class="mr-8"
            >
              <img :src="functionDetail?.icon" alt="" />
            </AppAvatar>
            <AppAvatar
              v-else-if="functionDetail?.name"
              :name="functionDetail?.name"
              pinyinColor
              shape="square"
              :size="64"
              class="mr-8"
            />
            <div class="ml-16">
              <h3 class="mb-8">{{ functionDetail.name }}</h3>
              <el-text type="info" v-if="functionDetail?.desc">
                {{ functionDetail.desc }}
              </el-text>
            </div>
          </div>
          <div @click.stop>
            <el-button type="primary" @click="addInternalFunction(functionDetail)">
              {{ $t('common.add') }}
            </el-button>
          </div>
        </div>

        <div class="mt-16">
          <el-text type="info">
            <div>{{ $t('common.author') }}: MaxKB</div>
          </el-text>
        </div>
      </div>
      <MdPreview
        ref="editorRef"
        editorId="preview-only"
        :modelValue="markdownContent"
        style="background: none"
        noImgZoomIn
      />
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

import { cloneDeep } from 'lodash'
import { isAppIcon } from '@/utils/application'
const emit = defineEmits(['refresh', 'addFunction'])

const visibleInternalDesc = ref(false)
const markdownContent = ref('')
const functionDetail = ref<any>({})

watch(visibleInternalDesc, (bool) => {
  if (!bool) {
    markdownContent.value = ''
  }
})

const open = (data: any, detail: any) => {
  functionDetail.value = detail
  if (data) {
    markdownContent.value = cloneDeep(data)
  }
  visibleInternalDesc.value = true
}

const addInternalFunction = (data: any) => {
  emit('addFunction', data)
  visibleInternalDesc.value = false
}

defineExpose({
  open
})
</script>
<style lang="scss"></style>
