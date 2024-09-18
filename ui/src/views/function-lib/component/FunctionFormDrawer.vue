<template>
  <el-drawer v-model="visible" size="60%" :before-close="close">
    <template #header>
      <h4>{{ title }}</h4>
    </template>
    <div>
      <h4 class="title-decoration-1 mb-16">基础信息</h4>
      <el-form
        ref="FormRef"
        :model="form"
        :rules="rules"
        label-position="top"
        require-asterisk-position="right"
        v-loading="loading"
      >
        <el-form-item label="函数名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入函数名称"
            maxlength="64"
            show-word-limit
            @blur="form.name = form.name?.trim()"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="form.desc"
            type="textarea"
            placeholder="请输入函数的描述"
            maxlength="128"
            show-word-limit
            :autosize="{ minRows: 3 }"
            @blur="form.desc = form.desc?.trim()"
          />
        </el-form-item>
        <el-form-item prop="permission_type">
          <template #label>
            <span>权限</span>
          </template>

          <el-radio-group v-model="form.permission_type" class="card__radio">
            <el-row :gutter="16">
              <template v-for="(value, key) of PermissionType" :key="key">
                <el-col :span="12">
                  <el-card
                    shadow="never"
                    class="mb-16"
                    :class="form.permission_type === key ? 'active' : ''"
                  >
                    <el-radio :value="key" size="large">
                      <p class="mb-4">{{ value }}</p>
                      <el-text type="info">
                        {{ PermissionDesc[key] }}
                      </el-text>
                    </el-radio>
                  </el-card>
                </el-col>
              </template>
            </el-row>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <div class="flex-between">
        <h4 class="title-decoration-1 mb-16">
          输入变量 <el-text type="info" class="color-secondary"> 使用函数时显示 </el-text>
        </h4>
        <el-button link type="primary" @click="openAddDialog()">
          <el-icon class="mr-4"><Plus /></el-icon> 添加
        </el-button>
      </div>

      <el-table :data="form.input_field_list" class="mb-16">
        <el-table-column prop="name" label="变量名" />
        <el-table-column label="数据类型">
          <template #default="{ row }">
            <el-tag type="info" class="info-tag">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="必填">
          <template #default="{ row }">
            <div @click.stop>
              <el-switch size="small" v-model="row.is_required" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源">
          <template #default="{ row }">
            {{ row.source === 'custom' ? '自定义' : '引用变量' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" align="left" width="80">
          <template #default="{ row, $index }">
            <span class="mr-4">
              <el-tooltip effect="dark" content="修改" placement="top">
                <el-button type="primary" text @click.stop="openAddDialog(row, $index)">
                  <el-icon><EditPen /></el-icon>
                </el-button>
              </el-tooltip>
            </span>
            <el-tooltip effect="dark" content="删除" placement="top">
              <el-button type="primary" text @click="deleteField($index)">
                <el-icon>
                  <Delete />
                </el-icon>
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
      <h4 class="title-decoration-1 mb-16">
        Python 代码 <el-text type="info" class="color-secondary"> 使用函数时不显示 </el-text>
      </h4>

      <div class="function-CodemirrorEditor mb-8" v-if="showEditor">
        <CodemirrorEditor v-model="form.code" />
        <div class="function-CodemirrorEditor__footer">
          <el-button text type="info" @click="openCodemirrorDialog" class="magnify">
            <AppIcon iconName="app-magnify" style="font-size: 16px"></AppIcon>
          </el-button>
        </div>
      </div>
      <h4 class="title-decoration-1 mb-16 mt-16">
        输出变量 <el-text type="info" class="color-secondary"> 使用函数时显示 </el-text>
      </h4>
      <div class="flex-between border-r-4 p-8-12 mb-8 layout-bg lighter">
        <span>结果 {result}</span>
      </div>
    </div>

    <template #footer>
      <div>
        <el-button :loading="loading" @click="visible = false">取消</el-button>
        <el-button :loading="loading" @click="openDebug">调试</el-button>
        <el-button type="primary" @click="submit(FormRef)" :loading="loading">
          {{ isEdit ? '保存' : '创建' }}</el-button
        >
      </div>
    </template>

    <!-- Codemirror 弹出层 -->
    <el-dialog v-model="dialogVisible" title="Python 代码" append-to-body>
      <CodemirrorEditor
        v-model="cloneContent"
        style="height: 300px !important; border: 1px solid #bbbfc4; border-radius: 4px"
      />
      <template #footer>
        <div class="dialog-footer mt-24">
          <el-button type="primary" @click="submitDialog"> 确认</el-button>
        </div>
      </template>
    </el-dialog>
    <FunctionDebugDrawer ref="FunctionDebugDrawerRef" />
    <FieldFormDialog ref="FieldFormDialogRef" @refresh="refreshFieldList" />
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import FieldFormDialog from './FieldFormDialog.vue'
import FunctionDebugDrawer from './FunctionDebugDrawer.vue'
import type { functionLibData } from '@/api/type/function-lib'
import functionLibApi from '@/api/function-lib'
import type { FormInstance } from 'element-plus'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { cloneDeep } from 'lodash'
import { PermissionType, PermissionDesc } from '@/enums/model'
const props = defineProps({
  title: String
})

const emit = defineEmits(['refresh'])
const FieldFormDialogRef = ref()
const FunctionDebugDrawerRef = ref()

const FormRef = ref()

const isEdit = ref(false)
const loading = ref(false)
const visible = ref(false)
const showEditor = ref(false)
const currentIndex = ref<any>(null)

const form = ref<functionLibData>({
  name: '',
  desc: '',
  code: '',
  input_field_list: [],
  permission_type: 'PRIVATE'
})

const dialogVisible = ref(false)
const cloneContent = ref<any>('')

watch(visible, (bool) => {
  if (!bool) {
    isEdit.value = false
    showEditor.value = false
    currentIndex.value = null
    form.value = {
      name: '',
      desc: '',
      code: '',
      input_field_list: [],
      permission_type: 'PRIVATE'
    }
  }
})

const rules = reactive({
  name: [{ required: true, message: '请输入函数名称', trigger: 'blur' }],
  permission_type: [{ required: true, message: '请选择', trigger: 'change' }]
})

function openCodemirrorDialog() {
  cloneContent.value = form.value.code
  dialogVisible.value = true
}

function submitDialog() {
  form.value.code = cloneContent.value
  dialogVisible.value = false
}

function close() {
  if (isEdit.value || !areAllValuesNonEmpty(form.value)) {
    visible.value = false
  } else {
    MsgConfirm(`提示`, `当前的更改尚未保存，确认退出吗?`, {
      confirmButtonText: '确认',
      type: 'warning'
    })
      .then(() => {
        visible.value = false
      })
      .catch(() => {})
  }
}

function areAllValuesNonEmpty(obj: any) {
  return Object.values(obj).some((value) => {
    return Array.isArray(value)
      ? value.length !== 0
      : value !== null && value !== undefined && value !== ''
  })
}

function openDebug() {
  FunctionDebugDrawerRef.value.open(form.value)
}

function deleteField(index: any) {
  form.value.input_field_list?.splice(index, 1)
}

function openAddDialog(data?: any, index?: any) {
  if (typeof index !== 'undefined') {
    currentIndex.value = index
  }

  FieldFormDialogRef.value.open(data)
}

function refreshFieldList(data: any) {
  if (currentIndex.value !== null) {
    form.value.input_field_list?.splice(currentIndex.value, 1, data)
  } else {
    form.value.input_field_list?.push(data)
  }
  currentIndex.value = null
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid: any) => {
    if (valid) {
      if (isEdit.value) {
        functionLibApi.putFunctionLib(form.value?.id as string, form.value, loading).then((res) => {
          MsgSuccess('编辑成功')
          emit('refresh', res.data)
          visible.value = false
        })
      } else {
        functionLibApi.postFunctionLib(form.value, loading).then((res) => {
          MsgSuccess('创建成功')
          emit('refresh')
          visible.value = false
        })
      }
    }
  })
}

const open = (data: any) => {
  if (data) {
    isEdit.value = data?.id ? true : false
    form.value = cloneDeep(data)
  }
  visible.value = true
  setTimeout(() => {
    showEditor.value = true
  }, 100)
}

defineExpose({
  open
})
</script>
<style lang="scss" scoped></style>
