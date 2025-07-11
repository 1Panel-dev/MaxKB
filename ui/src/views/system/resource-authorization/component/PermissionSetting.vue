<template>
  <div class="w-full">
    <div class="flex-between mb-16">
      <div
        class="flex align-center"
        v-if="hasPermission([EditionConst.IS_EE, EditionConst.IS_PE], 'OR')"
      >
        <!-- 企业版: 选优先级-->
        <span class="lighter mr-16">{{
          $t('views.system.resourceAuthorization.priority.label')
        }}</span>
        <el-radio-group v-model="radioRole">
          <el-radio :value="true" size="large"
            >{{ $t('views.system.resourceAuthorization.priority.role') }}
          </el-radio>
          <el-radio :value="false" size="large">{{ $t('common.custom') }}</el-radio>
        </el-radio-group>
      </div>
      <el-input
        v-model="filterText"
        :placeholder="$t('common.search')"
        prefix-icon="Search"
        class="mt-4"
        :class="hasPermission([EditionConst.IS_EE, EditionConst.IS_PE], 'OR') ? 'w-240' : ''"
        clearable
      />
    </div>

    <el-table
      row-key="id"
      :data="filterData"
      :max-height="tableHeight"
      :expand-row-keys="defaultExpandKeys"
      style="width: 100%"
    >
      <el-table-column class-name="folder-flex" prop="name" :label="$t('common.name')">
        <template #default="{ row }">
          <div class="flex align-center">
            <!-- 文件夹 icon -->
            <el-avatar
              v-if="row.isFolder"
              class="mr-12"
              shape="square"
              :size="20"
              style="background: none"
            >
              <img
                src="@/assets/knowledge/icon_file-folder_colorful.svg"
                style="width: 100%"
                alt=""
              />
            </el-avatar>
            <!--  知识库 icon -->
            <KnowledgeIcon class="mr-12" :size="20" v-else-if="isKnowledge" :type="row.icon" />
            <!--  应用/工具 自定义 icon -->
            <el-avatar
              v-else-if="isAppIcon(row?.icon) && !isModel"
              style="background: none"
              class="mr-12"
              shape="square"
              :size="20"
            >
              <img :src="resetUrl(row?.icon)" alt="" />
            </el-avatar>
            <!--  应用 icon -->
            <LogoIcon v-else-if="isApplication" height="20px" class="mr-12" />
            <!-- 工具 icon -->
            <el-avatar v-else-if="isTool" class="avatar-green mr-12" shape="square" :size="20">
              <img src="@/assets/workflow/icon_tool.svg" style="width: 58%" alt="" />
            </el-avatar>
            <!-- 模型 icon -->
            <span
              v-else-if="isModel"
              style="width: 24px; height: 24px; display: inline-block"
              class="mr-12"
              :innerHTML="getProviderIcon(row)"
            ></span>
            <span :title="row?.name">
              {{ row?.name }}
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column
        v-if="isRole"
        :label="$t('views.system.resourceAuthorization.setting.authorization')"
        align="center"
        width="100"
      >
        <!-- <template #header>
          <el-checkbox
            :disabled="props.manage"
            v-model="allChecked[AuthorizationEnum.MANAGE]"
            :indeterminate="allIndeterminate[AuthorizationEnum.MANAGE]"
            :label="$t('views.system.resourceAuthorization.setting.management')"
          />
        </template> -->
        <template #default="{ row }">
          <el-checkbox
            v-if="row.isFolder"
            :disabled="props.manage"
            v-model="row.permission[AuthorizationEnum.ROLE]"
            :indeterminate="row.permissionHalf[AuthorizationEnum.ROLE]"
            @change="(e: boolean) => checkedOperateChange(AuthorizationEnum.ROLE, row, e)"
          />
          <el-checkbox
            v-else
            :disabled="props.manage"
            v-model="row.permission[AuthorizationEnum.ROLE]"
            @change="(e: boolean) => checkedOperateChange(AuthorizationEnum.ROLE, row, e)"
          />
        </template>
      </el-table-column>
      <el-table-column
        v-if="!isRole"
        :label="$t('views.system.resourceAuthorization.setting.management')"
        align="center"
        width="100"
      >
        <!-- <template #header>
          <el-checkbox
            :disabled="props.manage"
            v-model="allChecked[AuthorizationEnum.MANAGE]"
            :indeterminate="allIndeterminate[AuthorizationEnum.MANAGE]"
            :label="$t('views.system.resourceAuthorization.setting.management')"
          />
        </template> -->
        <template #default="{ row }">
          <el-checkbox
            v-if="row.isFolder"
            :disabled="props.manage"
            v-model="row.permission[AuthorizationEnum.MANAGE]"
            :indeterminate="row.permissionHalf[AuthorizationEnum.MANAGE]"
            @change="(e: boolean) => checkedOperateChange(AuthorizationEnum.MANAGE, row, e)"
          />
          <el-checkbox
            v-else
            :disabled="props.manage"
            v-model="row.permission[AuthorizationEnum.MANAGE]"
            @change="(e: boolean) => checkedOperateChange(AuthorizationEnum.MANAGE, row, e)"
          />
        </template>
      </el-table-column>
      <el-table-column
        v-if="!isRole"
        :label="$t('views.system.resourceAuthorization.setting.check')"
        align="center"
        width="100"
      >
        <!-- <template #header>
          <el-checkbox
            :disabled="props.manage"
            v-model="allChecked[AuthorizationEnum.VIEW]"
            :indeterminate="allIndeterminate[AuthorizationEnum.VIEW]"
            :label="$t('views.system.resourceAuthorization.setting.check')"
          />
        </template> -->
        <template #default="{ row }">
          <el-checkbox
            v-if="row.isFolder"
            :disabled="props.manage"
            v-model="row.permission[AuthorizationEnum.VIEW]"
            :indeterminate="row.permissionHalf[AuthorizationEnum.VIEW]"
            @change="(e: boolean) => checkedOperateChange(AuthorizationEnum.VIEW, row, e)"
          />
          <el-checkbox
            v-else
            :disabled="props.manage"
            v-model="row.permission[AuthorizationEnum.VIEW]"
            @change="(e: boolean) => checkedOperateChange(AuthorizationEnum.VIEW, row, e)"
          />
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import type { Provider } from '@/api/type/model'
import { AuthorizationEnum } from '@/enums/system'
import { isAppIcon, resetUrl } from '@/utils/common'
import { EditionConst } from '@/utils/permission/data'
import { hasPermission } from '@/utils/permission/index'
import useStore from '@/stores'

const { model } = useStore()
const props = defineProps({
  data: {
    type: Array<any>,
    default: () => [],
  },
  id: String,
  type: String,
  tableHeight: Number,
  manage: Boolean,
  isRole: Boolean,
})
const emit = defineEmits(['update:data', 'refreshData', 'update:isRole'])
const radioRole = computed({
  get: () => props.isRole,
  set: (v: boolean) => {
    emit('update:isRole', v)
  },
})
const isKnowledge = computed(() => props.type === AuthorizationEnum.KNOWLEDGE)
const isApplication = computed(() => props.type === AuthorizationEnum.APPLICATION)
const isTool = computed(() => props.type === AuthorizationEnum.TOOL)
const isModel = computed(() => props.type === AuthorizationEnum.MODEL)
const defaultExpandKeys = computed(() => (props.data?.length > 0 ? [props.data[0]?.id] : []))
const dfsPermission = (arr: any = [], Name: string | number, e: boolean, idArr: any[]) => {
  arr.map((item: any) => {
    if (idArr.includes(item.id)) {
      item.permission[Name] = e
      if (Name === AuthorizationEnum.MANAGE && e) {
        item.permission[AuthorizationEnum.VIEW] = true
      } else if (Name === AuthorizationEnum.VIEW && !e) {
        item.permission[AuthorizationEnum.MANAGE] = false
      }
    }

    if (item.children?.length) {
      dfsPermission(
        item.children,
        Name,
        e,
        idArr.includes(item.id) ? item.children.map((ele: any) => ele.id) : idArr,
      )
    }
  })
}

const filterText = ref('')

const filterData = computed(() => {
  function filterTree(data: any[]): any[] {
    return data
      .map((item) => {
        // 递归过滤 children
        const children = item.children ? filterTree(item.children) : []
        // 判断当前节点或其子节点是否匹配
        const isMatch = item.name.toLowerCase().includes(filterText.value.toLowerCase())
        if (isMatch || children.length) {
          return {
            ...item,
            children: children.length ? children : undefined,
          }
        }
        return null
      })
      .filter(Boolean)
  }

  return filterTree(props.data)
})

function checkedOperateChange(Name: string | number, row: any, e: boolean) {
  dfsPermission(props.data, Name, e, [row.id])
  emit('refreshData')
}

const provider_list = ref<Array<Provider>>([])

function getProvider() {
  model.asyncGetProvider().then((res: any) => {
    provider_list.value = res?.data
  })
}

const getProviderIcon = computed(() => {
  return (row: any) => {
    return provider_list.value.find((p) => p.provider === row.icon)?.icon
  }
})
onMounted(() => {
  if (isModel.value) {
    getProvider()
  }
})
</script>
<style lang="scss" scoped>
:deep(.folder-flex) {
  .cell {
    display: flex;
    align-items: center;
  }
}
</style>
