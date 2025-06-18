<template>
  <el-dialog
    modal-class="authorized-workspace"
    v-model="centerDialogVisible"
    title="授权工作空间"
    width="840"
  >
    <div class="tip">被授权的工作空间，可使用当前资源</div>
    <div class="form-type">类型</div>
    <el-radio-group v-model="listType" @change="handleListTypeChange">
      <el-radio value="WHITE_LIST">白名单</el-radio>
      <el-radio value="BLACK_LIST">黑名单</el-radio>
    </el-radio-group>
    <div class="form-type_work">选择工作空间</div>
    <div class="workspace-list" v-loading="loading">
      <div class="to-be_selected">
        <el-input
          v-model="search"
          :validate-event="false"
          :placeholder="$t('dynamicsForm.searchBar.placeholder')"
          style="width: 364px"
          clearable
        >
          <template #prefix>
            <el-icon>
              <Search></Search>
            </el-icon>
          </template>
        </el-input>
        <el-checkbox
          v-model="checkAll"
          :indeterminate="isIndeterminate"
          @change="handleCheckAllChange"
          v-if="!search"
        >
          全选
        </el-checkbox>
        <el-checkbox-group v-model="checkedWorkspace" @change="handleCheckedWorkspaceChange">
          <el-checkbox
            v-for="space in workspaceWithKeywords"
            :key="space.id"
            :label="space.name"
            :value="space"
          >
            <el-icon size="20">
              <momentsCategories></momentsCategories>
            </el-icon>
            {{ space.name }}
          </el-checkbox>
        </el-checkbox-group>
      </div>
      <div class="selected">
        <div class="count">
          已选: {{ checkedWorkspace.length }} 个
          <el-button @click="clearWorkspaceAll" link type="primary"> 清空 </el-button>
        </div>
        <div class="list-item_primary" v-for="ele in checkedWorkspace">
          <el-icon size="20">
            <momentsCategories></momentsCategories>
          </el-icon>
          <div class="label">{{ ele.name }}</div>
          <el-icon @click="clearWorkspace(ele)" class="close" size="16">
            <closeIcon></closeIcon>
          </el-icon>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="centerDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirm"> 添加 </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'
import type { CheckboxValueType } from 'element-plus'
import iconMap from '@/components/app-icon/icons/common'
import { Search } from '@element-plus/icons-vue'
import authorizationApi from '@/api/shared/authorization'

const checkAll = ref(false)
const isIndeterminate = ref(true)
const checkedWorkspace = ref([])
const workspace = ref([])
const listType = ref('WHITE_LIST')
const search = ref('')
let knowledge_id = ''
let currentType = 'Knowledge'
const loading = ref(false)
const centerDialogVisible = ref(false)
let auth_list: any[] = []
let un_auth_list = []
const closeIcon = iconMap['close-outlined'].iconReader()
const momentsCategories = iconMap['moments-categories'].iconReader()

const workspaceWithKeywords = computed(() => {
  return workspace.value.filter((ele) => (ele.name as string).includes(search.value))
})
const handleCheckAllChange = (val: CheckboxValueType) => {
  checkedWorkspace.value = val ? workspace.value : []
  isIndeterminate.value = false
  if (val) {
    clearWorkspaceAll()
  } else {
    auth_list = [
      ...workspace.value.map((ele) => ({ authentication_type: listType.value, workspace_id: ele })),
      ...auth_list.filter((ele) => ele.authentication_type !== listType.value),
    ]
  }
}
const handleCheckedWorkspaceChange = (value: CheckboxValueType[]) => {
  const checkedCount = value.length
  checkAll.value = checkedCount === workspace.value.length
  isIndeterminate.value = checkedCount > 0 && checkedCount < workspace.value.length
  auth_list = [
    ...value.map((ele) => ({ authentication_type: listType.value, workspace_id: ele.id, name: ele.name })),
    ...auth_list.filter((ele) => ele.authentication_type !== listType.value),
  ]
}

const open = ({ id }: any, type = 'Knowledge') => {
  knowledge_id = id
  auth_list = []
  un_auth_list = []
  listType.value = 'WHITE_LIST'
  loading.value = true
  currentType = type
  authorizationApi[`getSharedAuthorization${type}`](id)
    .then((res: any) => {
      auth_list = (res.data || {}).auth_list || []
      un_auth_list = (res.data || {}).un_auth_list || []
      workspace.value = [
        ...un_auth_list,
        ...auth_list.map((ele) => ({ id: ele.workspace_id, name: ele.name })),
      ] as any
      handleListTypeChange(listType.value)
    })
    .finally(() => {
      loading.value = false
    })
  centerDialogVisible.value = true
}

const handleConfirm = () => {
  authorizationApi[`postSharedAuthorization${currentType}`](knowledge_id, {
    workspace_id_list: checkedWorkspace.value.map(ele => ele.id),
    authentication_type: listType.value,
  }).then(() => {
    centerDialogVisible.value = false
  })
}

const clearWorkspace = (val: any) => {
  checkedWorkspace.value = checkedWorkspace.value.filter((ele) => ele.id !== val.id)
  auth_list = auth_list.filter((ele) => ele.workspace_id !== val.id)
}

const clearWorkspaceAll = () => {
  checkedWorkspace.value = []
  auth_list = auth_list.filter((ele) => ele.authentication_type !== listType.value)
  handleCheckedWorkspaceChange([])
}

const handleListTypeChange = (val: any) => {
  checkedWorkspace.value = auth_list
    .filter((ele) => ele.authentication_type === val)
    .map((ele) => ({ id: ele.workspace_id, name: ele.name })) as any
  handleCheckedWorkspaceChange(checkedWorkspace.value)
}
defineExpose({
  open,
})
</script>
<style lang="scss">
.authorized-workspace {
  font-weight: 400;
  font-size: 14px;
  line-height: 22px;
  .tip {
    color: #646a73;
  }

  .el-dialog__header {
    padding-bottom: 8px;
  }

  .form-type {
    margin-top: 24px;
    margin-bottom: 8px;
  }

  .el-checkbox__label,
  .el-radio__label {
    color: #1f2329 !important;
    font-weight: 400;
  }

  .form-type_work {
    margin-top: 16px;
    margin-bottom: 8px;
  }

  .el-radio {
    height: 22px;
    line-height: 22px;
  }

  .workspace-list {
    width: 100%;
    border: 1px solid #dee0e3;
    border-radius: 4px;
    height: 428px;
  }

  .to-be_selected {
    padding: 16px 0;
    float: left;
    width: 50%;
    height: 100%;
    border-right: 1px solid #dee0e3;
    box-sizing: border-box;

    .el-input {
      margin: 0 0 12px 16px;
    }
    .el-checkbox {
      width: 100%;
      height: 38px;
    }
  }

  .selected {
    padding: 22px 0;
    float: right;
    width: calc(50% - 1px);
    height: 100%;
    box-sizing: border-box;

    .count {
      margin-left: 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 10px;
      .el-button {
        height: 26px;
        width: 44px;
        margin-right: 8px;

        &:hover,
        &:active {
          background-color: #3370ff1a;
          color: var(--el-button-text-color);
        }
      }
    }
  }
  .list-item_primary,
  .el-checkbox {
    height: 38px;
    padding: 8px 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    box-sizing: border-box;

    .el-icon:not(.close) {
      margin-right: 8px;
    }

    .el-checkbox__label {
      display: flex;
      align-items: center;
      width: 80%;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .label {
      width: 88%;
      font-size: 14px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    &:not(.active):hover {
      background: rgba(31, 35, 41, 0.1);
    }
  }
  .dialog-footer {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: flex-end;

    .el-button {
      min-width: 80px;
    }
  }
}
</style>
