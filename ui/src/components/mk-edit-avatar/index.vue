<script setup lang="ts">
import { onBeforeUnmount, ref, useTemplateRef, watch } from 'vue'
import { ClickOutside as vClickOutside, ElMessage } from 'element-plus'
import type { UploadFile, UploadInstance } from 'element-plus'

defineOptions({ name: 'MkEditAvatar' })

const props = withDefaults(defineProps<{ disabled?: boolean; size?: number }>(), {
  disabled: false,
  size: 32,
})
const avatar = defineModel<string>({ default: '' })
const emit = defineEmits<{ change: [file: File | null] }>()
defineSlots<{ default(props: { icon: string | undefined }): unknown }>()

// 头像编辑草稿：确认前不修改外部值。
const visible = ref(false)
const logoMode = ref<'default' | 'custom'>('default')
const previewIcon = ref('')
const draftFile = ref<File | null>(null)
const referenceRef = useTemplateRef<HTMLElement>('referenceRef')
const uploadRef = useTemplateRef<UploadInstance>('uploadRef')

function open() {
  if (visible.value) return
  logoMode.value = avatar.value ? 'custom' : 'default'
  previewIcon.value = logoMode.value === 'custom' ? avatar.value : ''
  draftFile.value = null
  visible.value = true
}

function close() {
  visible.value = false
}

function clearDraft() {
  if (visible.value) return
  previewIcon.value = ''
  draftFile.value = null
  uploadRef.value?.clearFiles()
}

function closeOutside(event: MouseEvent) {
  if (event.target instanceof Node && referenceRef.value?.contains(event.target)) return
  close()
}

function confirm() {
  if (logoMode.value === 'custom' && !previewIcon.value) return
  if (logoMode.value === 'default') {
    avatar.value = ''
    emit('change', null)
  } else if (draftFile.value) {
    avatar.value = previewIcon.value
    emit('change', draftFile.value)
  }
  close()
}

// 本地图片校验与预览，文件由调用方上传。
function selectImage(uploadFile: UploadFile) {
  const file = uploadFile.raw
  uploadRef.value?.clearFiles()
  if (!file) return
  if (!['image/jpeg', 'image/png', 'image/gif'].includes(file.type)) {
    ElMessage.warning('仅支持 JPG、PNG、GIF 格式的图片')
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.warning('文件大小不能超过 10MB')
    return
  }
  previewIcon.value = URL.createObjectURL(file)
  draftFile.value = file
}

// 临时地址由组件统一管理，仍用于头像或弹层预览时不释放。
function releaseUnusedPreview(icon: string) {
  if (icon.startsWith('blob:') && icon !== avatar.value && icon !== previewIcon.value) {
    URL.revokeObjectURL(icon)
  }
}

watch(
  [avatar, previewIcon],
  (_current, [previousAvatar, previousPreview]) => {
    releaseUnusedPreview(previousAvatar)
    if (previousPreview !== previousAvatar) releaseUnusedPreview(previousPreview)
  },
  { flush: 'sync' },
)
onBeforeUnmount(() => {
  if (previewIcon.value.startsWith('blob:') && previewIcon.value !== avatar.value) URL.revokeObjectURL(previewIcon.value)
  if (avatar.value.startsWith('blob:')) URL.revokeObjectURL(avatar.value)
})
</script>

<template>
  <!-- 单向控制显隐，避免选择文件时鼠标移出触发自动关闭。 -->
  <el-popover :visible="visible" :disabled="props.disabled" :width="414" placement="bottom-start" @after-leave="clearDraft">
    <template #reference>
      <!-- 悬停修改头像 -->
      <span
        ref="referenceRef"
        class="inline-flex shrink-0 [&>*]:h-full! [&>*]:w-full!"
        :class="{ 'cursor-pointer': !props.disabled }"
        :style="{ width: `${props.size}px`, height: `${props.size}px` }"
        @mouseenter="open"
      >
        <slot :icon="avatar || undefined" />
      </span>
    </template>

    <div v-click-outside="closeOutside" class="p-4" @keydown.esc.stop="close" @click.stop>
      <div class="mb-1">Logo 设置</div>
      <el-radio-group v-model="logoMode" class="mb-2">
        <el-radio value="default">默认 Logo</el-radio>
        <el-radio value="custom">自定义上传</el-radio>
      </el-radio-group>
      <div v-if="logoMode === 'default'" class="h-20 w-20 [&>*]:h-full! [&>*]:w-full!">
        <slot :icon="undefined" />
      </div>

      <div v-else>
        <!-- 选择或更换头像图片 -->
        <el-upload
          ref="uploadRef"
          action="#"
          accept="image/jpeg,image/png,image/gif"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="selectImage"
        >
          <el-avatar v-if="previewIcon" :size="80" shape="square">
            <img :src="previewIcon" class="object-cover" />
          </el-avatar>

          <div v-else class="flex-center h-20 w-20 rounded-md border border-dashed bg-N200 hover:border-primary">
            <MkIcon name="icon_add_outlined" :size="24" />
          </div>
        </el-upload>
        <p class="text-N600 mt-1">支持 JPG、PNG、GIF，文件大小不超过 10MB</p>
      </div>

      <div class="mt-4 text-right">
        <!-- 取消头像修改 -->
        <el-button plain @click="close">取消</el-button>
        <!-- 确认头像修改 -->
        <el-button type="primary" :disabled="logoMode === 'custom' && !previewIcon" @click="confirm">确定</el-button>
      </div>
    </div>
  </el-popover>
</template>
