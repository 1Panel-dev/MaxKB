import { hasPermission } from '@/utils/permission/index'
import { PermissionConst, RoleConst } from '@/utils/permission/data'

const workspace = {
    create: () => 
        hasPermission(
            [
              RoleConst.ADMIN,
              RoleConst.USER.getWorkspaceRole,
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_CREATE.getWorkspacePermission,
              PermissionConst.APPLICATION_CREATE.getWorkspacePermissionWorkspaceManageRole,  
            ],
            'OR'
    ),
    edit: (source_id:string) => 
        hasPermission(
            [
              RoleConst.ADMIN,
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_EDIT.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_EDIT.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    export: (source_id:string) => 
        hasPermission(
            [
              RoleConst.ADMIN,
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_EXPORT.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_EXPORT.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    delete: (source_id:string) => 
        hasPermission(
            [
              RoleConst.ADMIN,
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_DELETE.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_DELETE.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    overview_embed: (source_id:string) => 
        hasPermission(
            [
              RoleConst.ADMIN,
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_OVERVIEW_EMBEDDED.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_OVERVIEW_EMBEDDED.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    overview_access: (source_id:string) => 
      hasPermission(
            [
              RoleConst.ADMIN,
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_OVERVIEW_ACCESS.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_OVERVIEW_ACCESS.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    )

        ,
    overview_display: (source_id:string) => 
        hasPermission(
            [
              RoleConst.ADMIN,
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_OVERVIEW_DISPLAY.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_OVERVIEW_DISPLAY.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    overview_api_key: (source_id:string) => 
        hasPermission(
            [
              RoleConst.ADMIN,
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_OVERVIEW_API_KEY.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_OVERVIEW_API_KEY.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    access_edit: (source_id:string) => 
        hasPermission(
            [
              RoleConst.ADMIN,
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_ACCESS_EDIT.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_ACCESS_EDIT.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    chat_user_edit: (source_id:string) => 
        hasPermission(
            [
              RoleConst.ADMIN,
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_CHAT_USER_EDIT.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_CHAT_USER_EDIT.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    chat_log_clear: (source_id:string) => 
        hasPermission(
            [
              RoleConst.ADMIN,
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_CHAT_LOG_CLEAR_POLICY.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_CHAT_LOG_CLEAR_POLICY.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    chat_log_export: (source_id:string) => 
        hasPermission(
            [
              RoleConst.ADMIN,
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_CHAT_LOG_EXPORT.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_CHAT_LOG_EXPORT.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    chat_log_add_knowledge: (source_id:string) => 
        hasPermission(
            [
              RoleConst.ADMIN,
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_CHAT_LOG_ADD_KNOWLEDGE.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_CHAT_LOG_ADD_KNOWLEDGE.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
}


export default workspace