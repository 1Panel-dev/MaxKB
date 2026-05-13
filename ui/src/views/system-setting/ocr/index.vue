<template>
  <div class="ocr-setting p-16-24">
    <el-breadcrumb separator-icon="ArrowRight" class="mb-16">
      <el-breadcrumb-item>{{ t('views.system.subTitle') }}</el-breadcrumb-item>
      <el-breadcrumb-item>
        <h5 class="ml-4 color-text-primary">OCR 设置</h5>
      </el-breadcrumb-item>
    </el-breadcrumb>
    <el-card style="--el-card-padding: 16px" v-loading="loading">
      <el-scrollbar>
        <div class="ocr-setting__main p-16">
          <el-alert
            class="mb-16"
            :closable="false"
            type="info"
            show-icon
            title="OCR 用于把图片 / 扫描版 PDF 入库时自动识别成文本"
            description="启用后，知识库上传 .png/.jpg/.bmp/.tiff/.webp 等图片文件以及扫描版 PDF 时，会自动 OCR 识别后再向量化入库。支持两种模式：视觉大模型（精度高，需消耗模型额度）或本地 OCR（离线运行，需在容器内手动安装 rapidocr-onnxruntime）。"
          />

          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-position="top"
            require-asterisk-position="right"
          >
            <el-form-item label="OCR 模式" prop="mode">
              <el-radio-group v-model="form.mode">
                <el-radio value="vision_model">视觉大模型（推荐）</el-radio>
                <el-radio value="local">本地 OCR（rapidocr）</el-radio>
              </el-radio-group>
            </el-form-item>

            <!-- 视觉模型模式 -->
            <template v-if="form.mode === 'vision_model'">
              <el-form-item label="视觉模型" prop="model_id">
                <el-select
                  v-model="form.model_id"
                  filterable
                  clearable
                  placeholder="选择一个 IMAGE 类型的模型"
                  :loading="modelLoading"
                  @change="onModelChange"
                  style="width: 100%"
                >
                  <el-option
                    v-for="m in modelList"
                    :key="m.id"
                    :label="m.name"
                    :value="m.id"
                  >
                    <span>{{ m.name }}</span>
                    <span class="ml-8 color-secondary">{{ m.model_name }}</span>
                  </el-option>
                </el-select>
                <el-text type="info" size="small">
                  仅显示「图像识别 / 多模态」类型的已就绪模型（model_type=IMAGE）。如果列表为空，请先在「模型」中添加一个支持视觉的模型，例如 gpt-4o、claude-3-5-sonnet、gemini-1.5-pro、qwen-vl-max。
                </el-text>
              </el-form-item>

              <el-form-item label="OCR 提示词（可选）" prop="prompt">
                <el-input
                  v-model="form.prompt"
                  type="textarea"
                  :rows="3"
                  :placeholder="defaultPrompt"
                  maxlength="2048"
                  show-word-limit
                />
                <el-text type="info" size="small">留空则使用内置默认提示词，引导模型「忠实输出」而非「总结」。</el-text>
              </el-form-item>
            </template>

            <!-- 本地 OCR 模式 -->
            <template v-if="form.mode === 'local'">
              <el-alert
                class="mb-16"
                type="warning"
                :closable="false"
                show-icon
                title="本地 OCR 需要先在 MaxKB 容器内安装依赖"
              >
                <template #default>
                  <div style="font-family: monospace; white-space: pre-wrap; font-size: 12px; line-height: 1.6;">docker exec -it &lt;maxkb-container&gt; pip install rapidocr-onnxruntime onnxruntime</div>
                  <div class="mt-4">安装大约 150 MB，需要联网。安装完成后请点击下方「测试」按钮验证。</div>
                </template>
              </el-alert>
              <el-form-item label="主要语言" prop="language">
                <el-select v-model="form.language" style="width: 200px">
                  <el-option label="中文（含英文）" value="ch" />
                  <el-option label="English" value="en" />
                  <el-option label="日本語" value="japan" />
                  <el-option label="한국어" value="korean" />
                </el-select>
                <el-text type="info" size="small" class="ml-12">
                  影响 RapidOCR 加载哪一组识别模型。一般「中文」即可同时识别中英文。
                </el-text>
              </el-form-item>
            </template>

            <div class="mt-16">
              <el-button type="primary" @click="onSave" :disabled="loading">保存</el-button>
              <el-button @click="onTest" :disabled="loading">测试</el-button>
            </div>
          </el-form>
        </div>
      </el-scrollbar>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

import OcrApi from '@/api/system-settings/ocr-setting'
import ModelApi from '@/api/model/model'
import { MsgSuccess, MsgError } from '@/utils/message'
import { t } from '@/locales'
import useStore from '@/stores'

const { user } = useStore()

const defaultPrompt =
  '请把图片中的所有可见文字完整、忠实地识别并输出，保持原始的段落结构、列表项、表格行列关系；不要做总结、解释、翻译或添加任何额外说明；不能识别的部分用 [unclear] 占位。'

const form = ref<any>({
  mode: 'vision_model',
  model_id: '',
  workspace_id: '',
  language: 'ch',
  prompt: '',
})

const formRef = ref<FormInstance>()
const loading = ref(false)
const modelLoading = ref(false)
const modelList = ref<any[]>([])

const rules = reactive<FormRules<any>>({
  mode: [{ required: true, message: '请选择 OCR 模式', trigger: 'change' }],
  model_id: [
    {
      validator: (_rule: any, value: string, cb: any) => {
        if (form.value.mode === 'vision_model' && !value) {
          cb(new Error('请选择一个视觉模型'))
        } else {
          cb()
        }
      },
      trigger: 'change',
    },
  ],
})

function onModelChange(modelId: string) {
  // 把选中模型所在 workspace 记下来，后端 OCR 调用时需要
  form.value.workspace_id = user.getWorkspaceId() || 'default'
  // 实际上模型在哪个 workspace 是看模型本身的归属字段，此处假设当前用户的 workspace 与所选模型一致
  const m = modelList.value.find((x) => x.id === modelId)
  if (m && m.workspace_id) form.value.workspace_id = m.workspace_id
}

async function loadModels() {
  modelLoading.value = true
  try {
    // 拉所有当前 workspace 可见的 IMAGE 模型
    const res: any = await ModelApi.getSelectModelList({ model_type: 'IMAGE' } as any)
    // getSelectModelList 已经把 shared_model + model 合并为扁平数组
    modelList.value = (res?.data || []).filter((m: any) => m.status === 'SUCCESS' || !m.status)
  } catch (e) {
    modelList.value = []
  } finally {
    modelLoading.value = false
  }
}

async function loadSetting() {
  try {
    const res: any = await OcrApi.getOcrSetting(loading)
    if (res?.data) {
      form.value = {
        mode: res.data.mode || 'vision_model',
        model_id: res.data.model_id || '',
        workspace_id: res.data.workspace_id || '',
        language: res.data.language || 'ch',
        prompt: res.data.prompt || '',
      }
    }
  } catch (e) {
    // 接口缺失或权限不足时回退默认
  }
}

async function onSave() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      await OcrApi.putOcrSetting(buildPayload(), loading)
      MsgSuccess(t('common.saveSuccess'))
    } catch (e: any) {
      MsgError(e?.response?.data?.message || '保存失败')
    }
  })
}

async function onTest() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      await OcrApi.postTestOcrSetting(buildPayload(), loading)
      MsgSuccess('OCR 配置可用')
    } catch (e: any) {
      MsgError(e?.response?.data?.message || 'OCR 测试失败')
    }
  })
}

function buildPayload() {
  // 没选模型时把 workspace 默认填上，避免 vision_model 模式漏 workspace
  if (form.value.mode === 'vision_model' && !form.value.workspace_id) {
    form.value.workspace_id = user.getWorkspaceId() || 'default'
  }
  return { ...form.value }
}

onMounted(async () => {
  await Promise.all([loadModels(), loadSetting()])
})
</script>

<style lang="scss" scoped>
.ocr-setting {
  &__main {
    width: 70%;
    margin: 0 auto;
    height: calc(100vh - 200px);
  }
}
</style>
