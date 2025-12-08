<template>
  <el-dialog v-model="dialogVisible" :title="$t('views.document.tag.addTag')" :before-close="close">
    <el-form
      ref="FormRef"
      :model="{ tagList }"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-scrollbar>
        <el-row :gutter="8" style="margin-right: 10px" class="tag-list-max-list">
          <template v-for="(tag, index) in tagList" :key="tag">
            <el-col :span="12">
              <el-form-item
                :label="index === 0 ? $t('views.document.tag.key') : ''"
                :prop="`tagList.${index}.key`"
                :rules="{
                  required: true,
                  message: $t('views.document.tag.requiredMessage1'),
                  trigger: 'blur',
                }"
              >
                <el-select
                  v-model="tag.key"
                  @change="tagKeyChange(tag)"
                  filterable
                  :placeholder="$t('views.document.tag.requiredMessage1')"
                  :loading="optionLoading"
                >
                  <el-option
                    v-for="op in keyOptions"
                    :key="op"
                    :value="op.key"
                    :label="op.key"
                  ></el-option>
                  <template #footer>
                    <slot name="footer">
                      <div class="w-full text-left cursor">
                        <el-button type="primary" link @click="openCreateTagDialog()">
                          <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
                          {{ $t('views.document.tag.create') }}
                        </el-button>
                      </div>
                    </slot>
                  </template>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="11">
              <el-form-item
                :label="index === 0 ? $t('views.document.tag.value') : ''"
                :prop="`tagList.${index}.value`"
                :rules="{
                  required: true,
                  message: $t('views.document.tag.requiredMessage2'),
                  trigger: 'blur',
                }"
              >
                <el-select
                  v-model="tag.value"
                  filterable
                  :placeholder="$t('views.document.tag.requiredMessage2')"
                >
                  <el-option
                    v-for="op in getValueOptions(tag)"
                    :key="op"
                    :value="op.id"
                    :label="op.value"
                  ></el-option>
                  <template #footer>
                    <slot name="footer">
                      <div class="w-full text-left cursor">
                        <el-button type="primary" link @click="openCreateTagDialog(tag)">
                          <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
                          {{ $t('views.document.tag.createValue') }}
                        </el-button>
                      </div>
                    </slot>
                  </template>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="1">
              <el-button
                :disabled="tagList.length === 1"
                text
                @click="deleteTag(index)"
                :style="{ marginTop: index === 0 ? '35px' : '5px' }"
              >
                <AppIcon iconName="app-delete"></AppIcon>
              </el-button>
            </el-col>
          </template>
        </el-row>
      </el-scrollbar>
    </el-form>

    <el-button link type="primary" @click="add">
      <AppIcon iconName="app-add-outlined" class="mr-4" />
      {{ $t('common.add') }}
    </el-button>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="close">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit">{{ $t('common.confirm') }}</el-button>
      </div>
    </template>
    <CreateTagDialog ref="createTagDialogRef" @refresh="getTags" />
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import CreateTagDialog from './CreateTagDialog.vue'

const emit = defineEmits(['addTags'])
const props = defineProps<{
  apiType: 'systemShare' | 'workspace' | 'systemManage' | 'workspaceShare'
}>()

const route = useRoute()
const {
  params: { id, folderId }, // id为knowledgeID
} = route as any

const isShared = computed(() => {
  return folderId === 'share'
})

const optionLoading = ref<boolean>(false)
const FormRef = ref()
const dialogVisible = ref<boolean>(false)
const tagList = ref<Array<any>>([])
const keyOptions = ref()

const add = () => {
  tagList.value.push({})
}
const deleteTag = (index: number) => {
  tagList.value.splice(index, 1)
}

function tagKeyChange(tag: any) {
  tag.value = null
}

function getValueOptions(tag?: any) {
  let currentKeyOption = null
  if (tag && tag.key) {
    currentKeyOption = keyOptions.value.find((op: any) => op.key === tag.key)
  }
  return currentKeyOption ? currentKeyOption.values : []
}

const submit = () => {
  FormRef.value.validate((valid: boolean) => {
    if (!valid) return
    emit(
      'addTags',
      tagList.value.map((tag) => tag.value),
    )
  })
}

function getTags(Key?: string) {
  loadSharedApi({ type: 'knowledge', systemType: props.apiType, isShared: isShared.value })
    .getTags(id, {}, optionLoading)
    .then((res: any) => {
      keyOptions.value = res.data
    })
}

const createTagDialogRef = ref()

function openCreateTagDialog(row?: any) {
  createTagDialogRef.value?.open(row)
}

const open = () => {
  getTags()
  dialogVisible.value = true
  tagList.value = [{}]
}

const close = () => {
  dialogVisible.value = false
}

defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
