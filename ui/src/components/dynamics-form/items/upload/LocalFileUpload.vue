<template>
  <div v-loading="loading" class="w-full">
    <el-upload
      :webkitdirectory="false"
      class="w-full"
      drag
      multiple
      v-bind:file-list="modelValue"
      action="#"
      :auto-upload="false"
      :show-file-list="false"
      :accept="accept"
      :limit="attrs.limit"
      :on-exceed="onExceed"
      :on-change="fileHandleChange"
      @click.prevent="handlePreview(false)"
    >
      <img src="@/assets/upload-icon.svg" alt="" />
      <div class="el-upload__text">
        <p>
          {{ $t('views.document.upload.uploadMessage') }}
          <em class="hover" @click.prevent="handlePreview(false)">
            {{ $t('views.document.upload.selectFile') }}
          </em>
          <em class="hover ml-4" @click.prevent="handlePreview(true)">
            {{ $t('views.document.upload.selectFiles') }}
          </em>
        </p>
        <div class="upload__decoration">
          <p>
            {{ $t('views.document.tip.fileLimitCountTip1') }} {{ file_count_limit }}
            {{ $t('views.document.tip.fileLimitCountTip2') }},
            {{ $t('views.document.tip.fileLimitSizeTip1') }} {{ file_size_limit }} MB
          </p>
          <p>{{ $t('views.document.upload.formats') }}{{ formats }}</p>
        </div>
      </div>
    </el-upload>
    <el-row :gutter="8" v-if="modelValue?.length" class="mt-16">
      <template v-for="(item, index) in modelValue" :key="index">
        <el-col :span="12" class="mb-8">
          <el-card
            shadow="never"
            class="file-List-card"
            style="--el-card-padding: 8px 12px; line-height: normal"
          >
            <div class="flex-between">
              <div class="flex">
                <img :src="getImgUrl(item && item?.name)" alt="" width="40" />
                <div class="ml-8">
                  <p>{{ item && item?.name }}</p>
                  <el-text type="info" size="small">{{
                    filesize(item && item?.size) || '0K'
                  }}</el-text>
                </div>
              </div>
              <el-button text @click="deleteFile(index)">
                <AppIcon iconName="app-delete"></AppIcon>
              </el-button>
            </div>
          </el-card>
        </el-col>
      </template>
    </el-row>
  </div>
</template>
<script setup lang="ts">
import { computed, useAttrs, nextTick, inject, ref } from 'vue'
import type { FormField } from '@/components/dynamics-form/type'
import { MsgError } from '@/utils/message'
import type { UploadFiles } from 'element-plus'
import { filesize, getImgUrl } from '@/utils/common'
import { t } from '@/locales'
const upload = inject('upload') as any
const attrs = useAttrs() as any
const props = withDefaults(defineProps<{ modelValue?: any; formField: FormField }>(), {
  modelValue: () => [],
})
const onExceed = () => {
  MsgError(
    t('views.document.tip.fileLimitCountTip1') +
      attrs.limit +
      t('views.document.tip.fileLimitCountTip2'),
  )
}
const emit = defineEmits(['update:modelValue'])
const fileArray = ref<any>([])
const loading = ref<boolean>(false)
// 上传on-change事件
const fileHandleChange = (file: any, fileList: UploadFiles) => {
  //1、判断文件大小是否合法，文件限制不能大于100M
  const isLimit = file?.size / 1024 / 1024 < file_size_limit.value
  if (!isLimit) {
    MsgError(t('views.document.tip.fileLimitSizeTip1') + file_size_limit.value + 'MB')
    fileList.splice(-1, 1) //移除当前超出大小的文件
    return false
  }

  if (file?.size === 0) {
    MsgError(t('views.document.upload.errorMessage3'))
    fileList.splice(-1, 1)
    return false
  }
  upload(file.raw, loading).then((ok: any) => {
    const split_path = ok.data.split('/')
    const file_id = split_path[split_path.length - 1]
    fileArray.value?.push({ name: file.name, file_id, size: file.size })
    emit('update:modelValue', fileArray.value)
  })
}
function deleteFile(index: number) {
  emit(
    'update:modelValue',
    props.modelValue.filter((item: any, i: number) => index != i),
  )
}

const handlePreview = (bool: boolean) => {
  let inputDom: any = null
  nextTick(() => {
    if (document.querySelector('.el-upload__input') != null) {
      inputDom = document.querySelector('.el-upload__input')
      inputDom.webkitdirectory = bool
    }
  })
}
const accept = computed(() => {
  return (attrs.file_type_list || []).map((item: any) => '.' + item.toLowerCase()).join(',')
})

const formats = computed(() => {
  return (attrs.file_type_list || []).map((item: any) => item.toUpperCase()).join('、')
})
const file_size_limit = computed(() => {
  return attrs.file_size_limit || 50
})
const file_count_limit = computed(() => {
  return attrs.file_count_limit || 100
})
</script>
<style lang="scss" scoped>
.upload__decoration {
  font-size: 12px;
  line-height: 20px;
  color: var(--el-text-color-secondary);
}
.el-upload__text {
  .hover:hover {
    color: var(--el-color-primary-light-5);
  }
}
</style>
