<template>
  <el-dialog title="设置 Logo" v-model="dialogVisible">
    <el-radio-group v-model="radioType" class="radio-block mb-16">
      <div>
        <el-radio value="default">
          <p>默认 Logo</p>
          <AppAvatar
            v-if="detail?.name"
            :name="detail?.name"
            pinyinColor
            class="mt-8 mb-8"
            shape="square"
            :size="32"
          />
        </el-radio>
      </div>
      <div class="mt-8">
        <el-radio value="custom">
          <p>自定义上传</p>
          <div class="flex mt-8">
            <AppAvatar
              v-if="fileURL"
              shape="square"
              :size="32"
              style="background: none"
              class="mr-16"
            >
              <img :src="fileURL" alt="" />
            </AppAvatar>
            <el-upload
              ref="uploadRef"
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              accept="image/*"
              :on-change="onChange"
            >
              <el-button icon="Upload" :disabled="radioType !== 'custom'">上传</el-button>
            </el-upload>
          </div>
          <div class="el-upload__tip info mt-16">
            建议尺寸 32*32，支持 ico、png , 大小不超过200KB
          </div>
        </el-radio>
      </div>
    </el-radio-group>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submit" :loading="loading"> 保存 </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import overviewApi from '@/api/application-overview'
import { cloneDeep } from 'lodash'
import { MsgSuccess, MsgError } from '@/utils/message'
import { defaultIcon, isAppIcon } from '@/utils/application'
import useStore from '@/stores'

const { application } = useStore()

const route = useRoute()
const {
  params: { id } //应用id
} = route

const emit = defineEmits(['refresh'])

const iconFile = ref<any>(null)
const fileURL = ref<any>(null)

const dialogVisible = ref<boolean>(false)
const loading = ref(false)
const detail = ref<any>(null)
const radioType = ref('default')

watch(dialogVisible, (bool) => {
  if (!bool) {
    iconFile.value = null
    fileURL.value = null
  }
})

const open = (data: any) => {
  radioType.value = isAppIcon(data.icon) ? 'custom' : 'default'
  fileURL.value = isAppIcon(data.icon) ? data.icon : null
  detail.value = cloneDeep(data)
  dialogVisible.value = true
}

const onChange = (file: any) => {
  //1、判断文件大小是否合法，文件限制不能大于 200KB
  const isLimit = file?.size / 1024 < 200
  if (!isLimit) {
    MsgError('文件大小超过 200KB')
    return false
  }
  iconFile.value = file
  fileURL.value = URL.createObjectURL(file.raw)
}

function submit() {
  if (radioType.value === 'default') {
    application.asyncPutApplication(id as string, { icon: defaultIcon }, loading).then((res) => {
      emit('refresh')
      MsgSuccess('设置成功')
      dialogVisible.value = false
    })
  } else if (radioType.value === 'custom' && iconFile.value) {
    let fd = new FormData()
    fd.append('file', iconFile.value.raw)
    overviewApi.putAppIcon(id as string, fd, loading).then((res: any) => {
      emit('refresh')
      MsgSuccess('设置成功')
      dialogVisible.value = false
    })
  } else {
    MsgError('请上传一张图片')
  }
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
