<template>
  <el-dialog
    v-model="dialogVisible"
    :close-on-press-escape="false"
    :close-on-click-modal="false"
    :destroy-on-close="true"
    width="600"
  >
    <template #header="{ titleId, titleClass }">
      <h4 :id="titleId" :class="titleClass">添加成员</h4>
      <div class="dialog-sub-title">成员登录后可以访问到您授权的数据。</div>
    </template>

    <el-form
      ref="addMemberFormRef"
      :model="memberForm"
      label-position="top"
      :rules="rules"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item label="用户名/邮箱" prop="users">
        <el-select
          class="custom-select-multiple"
          v-model="memberForm.users"
          multiple
          filterable
          remote
          reserve-keyword
          placeholder="请输入成员的用户名或邮箱"
          :remote-method="remoteMethod"
          :loading="loading"
        >
          <el-option
            v-for="item in options"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submitMember(addMemberFormRef)"> 添加 </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { MsgSuccess } from '@/utils/message'
import TeamApi from '@/api/team'

interface ListItem {
  value: string
  label: string
}

const states = [
  'Alabama',
  'Alaska',
  'Arizona',
  'Arkansas',
  'California',
  'Colorado',
  'Connecticut',
  'Delaware',
  'Florida',
  'Georgia',
  'Hawaii',
  'Idaho',
  'Illinois',
  'Indiana',
  'Iowa',
  'Kansas',
  'Kentucky',
  'Louisiana',
  'Maine',
  'Maryland',
  'Massachusetts',
  'Michigan',
  'Minnesota',
  'Mississippi',
  'Missouri',
  'Montana',
  'Nebraska',
  'Nevada',
  'New Hampshire',
  'New Jersey',
  'New Mexico',
  'New York',
  'North Carolina',
  'North Dakota',
  'Ohio',
  'Oklahoma',
  'Oregon',
  'Pennsylvania',
  'Rhode Island',
  'South Carolina',
  'South Dakota',
  'Tennessee',
  'Texas',
  'Utah',
  'Vermont',
  'Virginia',
  'Washington',
  'West Virginia',
  'Wisconsin',
  'Wyoming'
]

const emit = defineEmits(['refresh'])

const dialogVisible = ref<boolean>(false)

const memberForm = ref({
  users: [],
  user: ''
})

const options = ref<ListItem[]>([])
const list = ref<ListItem[]>([])

const addMemberFormRef = ref<FormInstance>()

const loading = ref<boolean>(false)

const validateUsers = (rule: any, value: any, callback: any) => {
  if (value?.length == 0 && !memberForm.value.user) {
    callback(new Error('请输入用户名/邮箱'))
  } else {
    callback()
  }
}
const rules = ref<FormRules>({
  users: [{ type: 'array', validator: validateUsers }]
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    memberForm.value = {
      users: [],
      user: ''
    }
  }
})

const remoteMethod = (query: string) => {
  if (query) {
    loading.value = true
    setTimeout(() => {
      loading.value = false
      options.value = list.value.filter((item) => {
        return item.label.toLowerCase().includes(query.toLowerCase())
      })
    }, 200)
  } else {
    options.value = []
  }
}

const open = () => {
  dialogVisible.value = true
}
const submitMember = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      loading.value = true
      const submitValue: string = memberForm.value.users?.length
        ? memberForm.value.users.toString()
        : memberForm.value.user
      TeamApi.postCreatTeamMember(submitValue).then(() => {
        MsgSuccess('提交成功')
        emit('refresh')
        dialogVisible.value = false
      })
    } else {
      console.log('error submit!')
    }
  })
}

onMounted(() => {
  list.value = states.map((item) => {
    return { value: `value:${item}`, label: `label:${item}` }
  })
})

defineExpose({ open, close })
</script>
<style lang="scss" scope>
.custom-select-multiple {
  width: 200%;
  .el-input {
    min-height: 100px;
  }
  .el-select__tags {
    top: 0;
    transform: none;
    padding-top: 8px;
  }
  .el-input__wrapper {
    align-items: start;
  }
}
</style>
