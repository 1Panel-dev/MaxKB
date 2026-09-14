<script setup lang="ts">
import { computed, onBeforeUnmount, ref, useTemplateRef, watch } from 'vue'
import { ClickOutside as vClickOutside, ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

defineOptions({ name: 'MkEditAvatar' })

const props = withDefaults(defineProps<{ defaultIcon: string; editable?: boolean; size?: number }>(), {
  editable: true,
  size: 32,
})
const avatar = defineModel<string>({ default: '' })
const emit = defineEmits<{ change: [icon: string, file: File | null] }>()
defineSlots<{ default?(props: { icon: string; size: number }): unknown }>()

// 头像编辑草稿：确认前不修改外部值。
const visible = ref(false)
const logoMode = ref<'default' | 'custom'>('default')
const draftIcon = ref('')
const draftFile = ref<File | null>(null)
const reading = ref(false)
const referenceRef = useTemplateRef<HTMLElement>('referenceRef')
const fileInputRef = useTemplateRef<HTMLInputElement>('fileInputRef')
const currentIcon = computed(() => avatar.value || props.defaultIcon)
let fileReader: FileReader | undefined

function open() {
  if (!props.editable || visible.value) return
  logoMode.value = avatar.value && avatar.value !== props.defaultIcon ? 'custom' : 'default'
  draftIcon.value = logoMode.value === 'custom' ? avatar.value : ''
  draftFile.value = null
  visible.value = true
}

function close() {
  visible.value = false
  fileReader?.abort()
  reading.value = false
}

function clearDraft() {
  if (visible.value) return
  draftIcon.value = ''
  draftFile.value = null
  if (fileInputRef.value) fileInputRef.value.value = ''
}

function closeOutside(event: MouseEvent) {
  if (event.target instanceof Node && referenceRef.value?.contains(event.target)) return
  close()
}

function confirm() {
  if (reading.value || (logoMode.value === 'custom' && !draftIcon.value)) return
  const icon = logoMode.value === 'default' ? '' : draftIcon.value
  const file = logoMode.value === 'custom' ? draftFile.value : null
  avatar.value = icon
  emit('change', icon, file)
  close()
}

// 本地图片校验与预览，文件由调用方上传。
function selectImage(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  if (!['image/jpeg', 'image/png', 'image/gif'].includes(file.type)) {
    ElMessage.warning('仅支持 JPG、PNG、GIF 格式的图片')
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.warning('文件大小不能超过 10MB')
    return
  }
  fileReader?.abort()
  const reader = new FileReader()
  fileReader = reader
  reading.value = true
  reader.onload = () => {
    draftIcon.value = String(reader.result)
    draftFile.value = file
    reading.value = false
  }
  reader.onerror = () => {
    reading.value = false
    ElMessage.error('图片读取失败，请重新选择')
  }
  reader.readAsDataURL(file)
}

watch(
  () => props.editable,
  (editable) => {
    if (!editable) close()
  },
)
onBeforeUnmount(() => fileReader?.abort())
</script>

<template>
  <!-- // TODO: 优化头像预览效果 -->
  <el-popover :visible="visible" :width="414" placement="bottom-start" @after-leave="clearDraft">
    <template #reference>
      <!-- 悬停或点击修改头像 -->
      <button
        ref="referenceRef"
        type="button"
        class="inline-flex shrink-0 overflow-hidden rounded-md border-0 bg-transparent p-0 align-middle"
        :class="editable ? 'cursor-pointer' : 'cursor-default'"
        :disabled="!editable"
        :title="editable ? '修改头像' : '头像'"
        @mouseenter="open"
        @focus="open"
        @click.stop="open"
        @keydown.esc.stop="close"
      >
        <slot :icon="avatar" :size="size">
          <img :src="currentIcon" alt="头像" class="object-contain" :style="{ width: `${size}px`, height: `${size}px` }" />
        </slot>
      </button>
    </template>

    <div v-click-outside="closeOutside" class="text-N900" @keydown.esc.stop="close" @click.stop>
      <div class="mb-1">Logo 设置<span class="ml-0.5 text-danger">*</span></div>
      <el-radio-group v-model="logoMode" :disabled="reading" class="mb-2">
        <el-radio value="default">默认 Logo</el-radio>
        <el-radio value="custom">自定义上传</el-radio>
      </el-radio-group>

      <img v-if="logoMode === 'default'" :src="defaultIcon" alt="默认 Logo" class="h-[106px] w-[106px] rounded-md object-contain" />
      <div v-else>
        <input ref="fileInputRef" type="file" accept="image/jpeg,image/png,image/gif" class="hidden" @change="selectImage" />
        <!-- 选择或更换头像图片 -->
        <button
          type="button"
          class="flex-center h-20 w-20 cursor-pointer overflow-hidden rounded-md border border-dashed bg-N100 p-0 hover:border-primary"
          :disabled="reading"
          :title="draftIcon ? '更换头像图片' : '上传头像图片'"
          @click="fileInputRef?.click()"
        >
          <img v-if="draftIcon" :src="draftIcon" alt="自定义头像预览" class="h-full w-full object-contain" />
          <MkIcon v-else :icon="Plus" :size="28" />
        </button>
        <p class="mt-1 text-N600">支持 JPG、PNG、GIF，文件大小不超过 10MB</p>
      </div>

      <div class="mt-4 flex justify-end gap-3">
        <!-- 取消头像修改 -->
        <el-button class="min-w-20" @click="close">取消</el-button>
        <!-- 确认头像修改 -->
        <el-button class="ml-0! min-w-20" type="primary" :loading="reading" :disabled="logoMode === 'custom' && !draftIcon" @click="confirm">
          确定
        </el-button>
      </div>
    </div>
  </el-popover>
</template>
