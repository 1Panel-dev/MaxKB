<template>
  <el-input
    v-model="filterText"
    :placeholder="$t('common.search')"
    prefix-icon="Search"
    class="mb-16 mt-4 1"
    clearable
  />
  <div class="pt-0">
    <el-table default-expand-all row-key="id" :data="filterData" :max-height="tableHeight">
      <el-table-column class-name="folder-flex" prop="name" :label="$t('common.name')">
        <template #default="{ row }">
          <div class="flex align-center">
            <el-avatar
              v-if="isApplication && isAppIcon(row?.icon)"
              style="background: none"
              class="mr-12"
              shape="square"
              :size="20"
            >
              <img :src="row?.icon" alt="" />
            </el-avatar>

            <LogoIcon
              v-else-if="isApplication"
              height="28px"
              style="width: 28px; height: 28px; display: block"
              class="mr-12"
            />
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
            <KnowledgeIcon class="mr-12" :size="20" v-else-if="isKnowledge" :type="row.icon" />

            <auto-tooltip :content="row?.name">
              {{ row?.name }}
            </auto-tooltip>
          </div>
        </template>
      </el-table-column>
      <el-table-column
        :label="$t('views.resourceAuthorization.setting.management')"
        align="center"
        width="100"
        fixed="right"
      >
        <!-- <template #header>
          <el-checkbox
            :disabled="props.manage"
            v-model="allChecked[AuthorizationEnum.MANAGE]"
            :indeterminate="allIndeterminate[AuthorizationEnum.MANAGE]"
            :label="$t('views.resourceAuthorization.setting.management')"
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
        :label="$t('views.resourceAuthorization.setting.check')"
        align="center"
        width="100"
        fixed="right"
      >
        <!-- <template #header>
          <el-checkbox
            :disabled="props.manage"
            v-model="allChecked[AuthorizationEnum.VIEW]"
            :indeterminate="allIndeterminate[AuthorizationEnum.VIEW]"
            :label="$t('views.resourceAuthorization.setting.check')"
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
import { AuthorizationEnum } from '@/enums/system'
import { isAppIcon } from '@/utils/common'

const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
  id: String,
  type: String,
  tableHeight: Number,
  manage: Boolean,
})

const isKnowledge = computed(() => props.type === AuthorizationEnum.KNOWLEDGE)
const isApplication = computed(() => props.type === AuthorizationEnum.APPLICATION)

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

const emit = defineEmits(['update:data', 'refreshData'])

const filterText = ref('')

const filterData = computed(() =>
  props.data.filter((v: any) => v.name.toLowerCase().includes(filterText.value.toLowerCase())),
)

function checkedOperateChange(Name: string | number, row: any, e: boolean) {
  dfsPermission(props.data, Name, e, [row.id])
  emit('refreshData')
}
</script>
<style lang="scss" scoped>
:deep(.folder-flex) {
  .cell {
    display: flex;
    align-items: center;
  }
}
</style>
