<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

defineOptions({ name: 'AdvancedCreateDialog' })

type ApplicationTemplate = 'blank' | 'assistant'

interface AdvancedApplicationDraft {
  desc: string
  name: string
  template: ApplicationTemplate
}

const emit = defineEmits<{ submit: [draft: AdvancedApplicationDraft] }>()

const dialogVisible = ref(false)
const selectedTemplate = ref<ApplicationTemplate>('blank')
const applicationFormRef = ref<FormInstance>()
const applicationForm = reactive<Omit<AdvancedApplicationDraft, 'template'>>({ desc: '', name: '' })
const applicationFormRules: FormRules<typeof applicationForm> = {
  name: [{ required: true, message: '请输入智能体名称', trigger: 'blur' }],
}
const createDisabled = computed(() => !applicationForm.name.trim())

function open() {
  resetData()
  dialogVisible.value = true
}

function submit() {
  applicationFormRef.value?.validate((valid) => {
    if (!valid) return

    emit('submit', {
      desc: applicationForm.desc.trim(),
      name: applicationForm.name.trim(),
      template: selectedTemplate.value,
    })
    dialogVisible.value = false
  })
}

function resetData() {
  Object.assign(applicationForm, { desc: '', name: '' })
  selectedTemplate.value = 'blank'
  applicationFormRef.value?.clearValidate()
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" title="创建高级智能体" align-center @closed="resetData">
    <el-form
      ref="applicationFormRef"
      class="pt-5"
      :model="applicationForm"
      :rules="applicationFormRules"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent="submit"
    >
      <el-form-item label="名称" prop="name">
        <el-input
          v-model="applicationForm.name"
          maxlength="64"
          placeholder="请输入智能体名称"
          show-word-limit
          @blur="applicationForm.name = applicationForm.name.trim()"
        />
      </el-form-item>

      <el-form-item label="描述">
        <el-input
          v-model="applicationForm.desc"
          maxlength="500"
          placeholder="描述该智能体的应用场景及用途，如：XXX 小助手回答用户提出的 XXX 产品使用问题"
          :rows="4"
          show-word-limit
          type="textarea"
          @blur="applicationForm.desc = applicationForm.desc.trim()"
        />
      </el-form-item>

      <el-form-item label="模板" class="mb-0!">
        <div class="grid w-full grid-cols-2 gap-4">
          <button
            type="button"
            class="flex h-38 items-center justify-center rounded-lg border text-lg transition-colors hover:border-primary"
            :class="selectedTemplate === 'blank' ? 'border-primary bg-primary/[0.08]' : 'bg-white'"
            @click="selectedTemplate = 'blank'"
          >
            <MkIcon name="icon_add_outlined" :size="22" />
            <span class="ml-2">空白创建</span>
          </button>

          <button
            type="button"
            class="flex h-38 flex-col rounded-lg border p-4 text-left transition-colors hover:border-primary"
            :class="selectedTemplate === 'assistant' ? 'border-primary bg-primary/[0.08]' : 'bg-white'"
            @click="selectedTemplate = 'assistant'"
          >
            <span class="flex items-center gap-3">
              <el-avatar shape="square" :size="24" class="bg-primary-gradient!">
                <img style="width: 65%" src="@/assets/application/icon_simple_application.svg" alt="" />
              </el-avatar>
              <h6>知识库问答助手</h6>
            </span>
            <span class="mt-4 text-N600">将从知识库中检索到的知识作为已知信息，回答用户提出的问题。</span>
            <span class="mt-auto flex items-center gap-2 text-N600">
              <MkIcon name="icon_download_outlined" />
              <span>204</span>
            </span>
          </button>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button plain @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :disabled="createDisabled" @click="submit">创建</el-button>
    </template>
  </MkDialog>
</template>
