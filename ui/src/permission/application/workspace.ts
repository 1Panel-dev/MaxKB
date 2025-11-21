import { hasPermission } from '@/utils/permission/index'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
import { ComplexPermission } from '@/utils/permission/type'

const workspace = {
    create: () => 
        hasPermission(
            [
              RoleConst.USER.getWorkspaceRole,
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_CREATE.getWorkspacePermission,
              PermissionConst.APPLICATION_CREATE.getWorkspacePermissionWorkspaceManageRole,  
            ],
            'OR'
    ),
    folderCreate: (folder_id: string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(folder_id)],[],'AND'),
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_FOLDER_EDIT.getApplicationWorkspaceResourcePermission(folder_id),
              PermissionConst.APPLICATION_CREATE.getWorkspacePermissionWorkspaceManageRole,  
            ],
            'OR'
    ),
    folderRead: (folder_id: string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(folder_id)],[],'AND'),  
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_FOLDER_READ.getApplicationWorkspaceResourcePermission(folder_id),
              PermissionConst.APPLICATION_READ.getWorkspacePermissionWorkspaceManageRole,  
            ],
            'OR'
    ),
    folderEdit: (folder_id: string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(folder_id)],[],'AND'),
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_FOLDER_EDIT.getApplicationWorkspaceResourcePermission(folder_id),
              PermissionConst.APPLICATION_EDIT.getWorkspacePermissionWorkspaceManageRole,
            ],
            'OR'
    ),
    folderAuth: (folder_id: string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(folder_id)],[],'AND'),  
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_FOLDER_EDIT.getApplicationWorkspaceResourcePermission(folder_id),
              PermissionConst.APPLICATION_RESOURCE_AUTHORIZATION.getWorkspacePermissionWorkspaceManageRole,  
            ],
            'OR'
    ),
    folderDelete: (folder_id: string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(folder_id)],[],'AND'),
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_FOLDER_EDIT.getApplicationWorkspaceResourcePermission(folder_id),
              PermissionConst.APPLICATION_DELETE.getWorkspacePermissionWorkspaceManageRole
            ],
            'OR'
    ),
    folderManage: (folder_id: string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(folder_id)],[],'AND'),  
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_FOLDER_EDIT.getApplicationWorkspaceResourcePermission(folder_id),
              PermissionConst.APPLICATION_EDIT.getWorkspacePermissionWorkspaceManageRole,  
            ],
            'OR'
    ),
    edit: (source_id:string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(source_id)],[],'AND'),
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_EDIT.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_EDIT.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    debug: (source_id:string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(source_id)],[],'AND'),
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_READ.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_READ.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    auth: (source_id:string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(source_id)],[],'AND'),
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_RESOURCE_AUTHORIZATION.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_RESOURCE_AUTHORIZATION.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    export: (source_id:string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(source_id)],[],'AND'),
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_EXPORT.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_EXPORT.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    delete: (source_id:string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(source_id)],[],'AND'),
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_DELETE.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_DELETE.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),

    overview_embed: (source_id:string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(source_id)],[],'AND'),
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_OVERVIEW_EMBEDDED.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_OVERVIEW_EMBEDDED.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    overview_access: (source_id:string) => 
      hasPermission(
            [new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(source_id)],[],'AND'),
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
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(source_id)],[],'AND'),
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_OVERVIEW_DISPLAY.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_OVERVIEW_DISPLAY.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    overview_api_key: (source_id:string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(source_id)],[],'AND'),
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_OVERVIEW_API_KEY.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_OVERVIEW_API_KEY.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    access_edit: (source_id:string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(source_id)],[],'AND'),
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_ACCESS_EDIT.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_ACCESS_EDIT.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    application_chat_user_edit: (source_id:string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(source_id)],[],'AND'),
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_CHAT_USER_EDIT.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_CHAT_USER_EDIT.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    chat_log_clear: (source_id:string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(source_id)],[],'AND'),
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_CHAT_LOG_CLEAR_POLICY.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_CHAT_LOG_CLEAR_POLICY.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    chat_log_export: (source_id:string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(source_id)],[],'AND'),
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_CHAT_LOG_EXPORT.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_CHAT_LOG_EXPORT.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    chat_log_add_knowledge: (source_id:string) => 
        hasPermission(
            [
              new ComplexPermission([RoleConst.USER],[PermissionConst.APPLICATION.getApplicationWorkspaceResourcePermission(source_id)],[],'AND'),
              RoleConst.WORKSPACE_MANAGE.getWorkspaceRole,
              PermissionConst.APPLICATION_CHAT_LOG_ADD_KNOWLEDGE.getWorkspacePermissionWorkspaceManageRole,
              PermissionConst.APPLICATION_CHAT_LOG_ADD_KNOWLEDGE.getApplicationWorkspaceResourcePermission(source_id)  
            ],
            'OR'
    ),
    overview_read: () => false,
    access_read: () => false,
    chat_user_read: () => false,
    chat_log_read: () => false
}


export default workspace