<template>
  <el-drawer v-model="visibleInternalDesc" size="60%" :append-to-body="true">
    <template #header>
      <div class="flex align-center" style="margin-left: -8px">
        <el-button class="cursor mr-4" link @click.prevent="visibleInternalDesc = false">
          <el-icon :size="20">
            <Back />
          </el-icon>
        </el-button>
        <h4>{{ $t('common.detail') }}</h4>
      </div>
    </template>

    <div>
      <div class="border-b">
        <div class="flex-between mb-24">
          <div class="title flex align-center">
            <el-avatar shape="square" :size="64" style="background: none">
              <img src="@/assets/knowledge/icon_basic_template.svg" alt="" />
            </el-avatar>
            <div class="ml-16">
              <h3 class="mb-8">{{ toolDetail.name }}</h3>
              <el-text type="info" v-if="toolDetail?.desc">
                {{ toolDetail.desc }}
              </el-text>
              <span
                class="color-secondary flex align-center mt-8"
                v-if="toolDetail?.downloads != undefined"
              >
                <AppIcon iconName="app-download" class="mr-4" />
                <span> {{ numberFormat(toolDetail.downloads || 0) }} </span>
              </span>
            </div>
          </div>
          <div @click.stop>
            <el-button type="primary" @click="addInternalTool(toolDetail)">
              {{ $t('common.use') }}
            </el-button>
          </div>
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
import { isAppIcon, numberFormat } from '@/utils/common'
const emit = defineEmits(['refresh', 'addTool'])

const visibleInternalDesc = ref(false)
const markdownContent = ref('')
const toolDetail = ref<any>({})

watch(visibleInternalDesc, (bool) => {
  if (!bool) {
    markdownContent.value = ''
  }
})

const open = (data: any, detail: any) => {
  toolDetail.value = detail
  if (data) {
    markdownContent.value = cloneDeep(data)
  }
  visibleInternalDesc.value = true
}

const addInternalTool = (data: any) => {
  emit('addTool', data)
  visibleInternalDesc.value = false
}

defineExpose({
  open,
})
</script>
<style lang="scss"></style>
