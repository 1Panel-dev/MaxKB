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
}


export default workspace