<template>
  <div class="upload-document p-12-24">
    <div class="flex align-center mb-16">
      <back-button @click="back" style="margin-left: -4px"></back-button>
      <h3 style="display: inline-block">{{ $t('views.document.importDocument') }}</h3>
    </div>
    <el-card style="--el-card-padding: 0">
      <div class="upload-document__main flex" v-loading="loading">
        <div class="upload-document__component main-calc-height">
          <el-scrollbar>
            <div class="upload-component p-24" style="min-width: 850px">
              <keep-alive :key="key" :include="['data_source', 'knowledge_base']">
                <component
                  ref="ActionRef"
                  :is="ak[active]"
                  v-model:loading="loading"
                  :workflow="_workflow"
                  :knowledge_id="id"
                  :id="action_id"
                ></component>
              </keep-alive>
            </div>
          </el-scrollbar>
        </div>
      </div>
    </el-card>
    <div class="upload-document__footer text-right border-t">
      <el-button v-if="active == 'result'" @click="continueImporting">
        {{ $t('views.document.buttons.continueImporting') }}
      </el-button>
      <el-button
        v-if="base_form_list.length > 0 && active == 'knowledge_base'"
        :loading="loading"
        @click="up"
      >
        {{ $t('common.steps.prev') }}</el-button
      >
      <el-button
        v-if="base_form_list.length > 0 && active == 'data_source'"
        :disabled="loading"
        @click="next"
      >
        {{ $t('common.steps.next') }}
      </el-button>
      <el-button
        v-if="base_form_list.length > 0 ? active == 'knowledge_base' : active == 'data_source'"
        @click="upload"
        type="primary"
        :disabled="loading"
      >
        {{ $t('views.document.buttons.import') }}
      </el-button>
      <el-button v-if="active == 'result'" type="primary" @click="goDocument">{{
        $t('views.knowledge.ResultSuccess.buttons.toDocument')
      }}</el-button>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, ref, provide, type Ref, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import DataSource from '@/views/knowledge-workflow/component/action/DataSource.vue'
import Result from '@/views/knowledge-workflow/component/action/Result.vue'
import applicationApi from '@/api/application/application'
import KnowledgeBase from '@/views/knowledge-workflow/component/action/KnowledgeBase.vue'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { WorkflowType } from '@/enums/application'
import { ComplexPermission, Permission } from '@/utils/permission/type'
import { hasPermission } from '@/utils/permission'
import { EditionConst, PermissionConst, RoleConst } from '@/utils/permission/data'
provide('upload', (file: any, loading?: Ref<boolean>) => {
  return applicationApi.postUploadFile(file, id as string, 'KNOWLEDGE', loading)
})
const router = useRouter()
const route = useRoute()
const key = ref<number>(0)
const {
  params: { folderId },
  query: { id },
  /*
  id为knowledgeID
  folderId 可以区分 resource-management shared还是 workspace
  */
} = route
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const ak = {
  data_source: DataSource,
  knowledge_base: KnowledgeBase,
  result: Result,
}

const loading = ref(false)
const ActionRef = ref()
const action_id = ref<string>()
const form_data = ref<any>({})
const active = ref<'data_source' | 'knowledge_base' | 'result'>('data_source')
const _workflow = ref<any>(null)

const base_form_list = computed(() => {
  const kBase = _workflow.value?.nodes?.find((n: any) => n.type === WorkflowType.KnowledgeBase)
  if (kBase) {
    return kBase.properties.user_input_field_list
  }
  return []
})
const next = () => {
  ActionRef.value.validate().then(() => {
    form_data.value[active.value] = ActionRef.value.get_data()
    active.value = 'knowledge_base'
  })
}
const up = () => {
  ActionRef.value.validate().then(() => {
    active.value = 'data_source'
  })
}
const upload = () => {
  ActionRef.value.validate().then(() => {
    form_data.value[active.value] = ActionRef.value.get_data()
    loadSharedApi({ type: 'knowledge', systemType: apiType.value })
      .workflowUpload(id, form_data.value, loading)
      .then((ok: any) => {
        action_id.value = ok.data.id
        active.value = 'result'
      })
  })
}
function getDetail() {
  loadSharedApi({ type: 'knowledge', systemType: apiType.value })
    .getKnowledgeDetail(id, loading)
    .then((res: any) => {
      _workflow.value = res.data.work_flow
    })
}
const continueImporting = () => {
  active.value = 'data_source'
  key.value++
  action_id.value = undefined
  const c_workflow = _workflow.value
  _workflow.value = null
  form_data.value = {}
  nextTick(() => {
    _workflow.value = c_workflow
  })
}
const goDocument = () => {
  router.push({ path: `/knowledge/${id}/${folderId}/4/document` })
}

const back = () => {
  if (route.path.includes('resource-management')) {
    return router.push({ path: get_resource_management_route() })
  } else if (route.path.includes('shared')) {
    return router.push({ path: get_shared_route() })
  } else {
    return router.push({ path: get_route() })
  }
}

const get_shared_route = () => {
  if (hasPermission([RoleConst.ADMIN, PermissionConst.SHARED_KNOWLEDGE_DOCUMENT_READ], 'OR')) {
    return `/knowledge/${id}/shared/4/document`
  } else if (
    hasPermission([RoleConst.ADMIN, PermissionConst.SHARED_KNOWLEDGE_PROBLEM_READ], 'OR')
  ) {
    return `/knowledge/${id}/shared/4/problem`
  } else if (
    hasPermission([RoleConst.ADMIN, PermissionConst.SHARED_KNOWLEDGE_HIT_TEST_READ], 'OR')
  ) {
    return `/knowledge/${id}/shared/4/hit-test`
  } else if (
    hasPermission([RoleConst.ADMIN, PermissionConst.SHARED_KNOWLEDGE_CHAT_USER_READ], 'OR')
  ) {
    return `/knowledge/${id}/shared/4/chat-user`
  } else if (hasPermission([RoleConst.ADMIN, PermissionConst.SHARED_KNOWLEDGE_EDIT], 'OR')) {
    return `/knowledge/${id}/shared/4/setting`
  } else {
    return `/system/shared/knowledge`
  }
}

const get_resource_management_route = () => {
  if (hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_KNOWLEDGE_DOCUMENT_READ], 'OR')) {
    return `/knowledge/${id}/resource-management/4/document`
  } else if (
    hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_KNOWLEDGE_PROBLEM_READ], 'OR')
  ) {
    return `/knowledge/${id}/resource-management/4/problem`
  } else if (hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_KNOWLEDGE_HIT_TEST], 'OR')) {
    return `/knowledge/${id}/resource-management/4/hit-test`
  } else if (
    hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_KNOWLEDGE_CHAT_USER_READ], 'OR')
  ) {
    return `/knowledge/${id}/resource-management/4/chat-user`
  } else if (hasPermission([RoleConst.ADMIN, PermissionConst.RESOURCE_KNOWLEDGE_EDIT], 'OR')) {
    return `/knowledge/${id}/resource-management/4/setting`
  } else {
    return `/system/resource-management/knowledge`
  }
}

const get_route = () => {
  const checkPermission = (permissionConst: Permission) => {
    return hasPermission(
      [
        new ComplexPermission(
          [RoleConst.USER],
          [PermissionConst.KNOWLEDGE.getKnowledgeWorkspaceResourcePermission(id as string)],
          [],
          'AND',
        ),
        RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
        permissionConst.getWorkspacePermissionWorkspaceManageRole,
        permissionConst.getKnowledgeWorkspaceResourcePermission(id as string),
      ],
      'OR',
    )
  }
  if (checkPermission(PermissionConst.KNOWLEDGE_DOCUMENT_READ)) {
    return `/knowledge/${id}/${folderId}/4/document`
  } else if (checkPermission(PermissionConst.KNOWLEDGE_PROBLEM_READ)) {
    return `/knowledge/${id}/${folderId}/4/problem`
  } else if (checkPermission(PermissionConst.KNOWLEDGE_HIT_TEST_READ)) {
    return `/knowledge/${id}/${folderId}/4/hit-test`
  } else if (checkPermission(PermissionConst.KNOWLEDGE_CHAT_USER_READ)) {
    return `/knowledge/${id}/${folderId}/4/chat-user`
  } else if (checkPermission(PermissionConst.KNOWLEDGE_EDIT)) {
    return `/knowledge/${id}/${folderId}/4/setting`
  } else {
    return `/knowledge`
  }
}

onMounted(() => {
  getDetail()
})
</script>
<style lang="scss">
@use './index.scss';
</style>
