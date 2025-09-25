import {hasPermission} from '@/utils/permission/index'
import {PermissionConst, RoleConst} from '@/utils/permission/data'

const systemManage = {
    create: () => false,
    folderCreate: () => false,
    edit: () =>
        hasPermission(
            [
              RoleConst.ADMIN,
              PermissionConst.RESOURCE_APPLICATION_EDIT
            ],
            'OR'
    ),
    folderEdit: () => false,
    export: () =>
        hasPermission(
            [
              RoleConst.ADMIN,
              PermissionConst.RESOURCE_APPLICATION_EXPORT
            ],
            'OR'
    ),
    delete: () =>
        hasPermission(
            [
              RoleConst.ADMIN,
              PermissionConst.RESOURCE_APPLICATION_DELETE
            ],
            'OR'
    ),
    debug: () =>
        hasPermission(
            [
              RoleConst.ADMIN,
              PermissionConst.RESOURCE_APPLICATION_EDIT
            ],
            'OR'
    ),
    folderDelete: () => false,
    auth: () => 
        hasPermission(
            [
              RoleConst.ADMIN,
              PermissionConst.RESOURCE_APPLICATION_AUTH
            ],
            'OR'
    ),
    overview_embed: () =>
        hasPermission(
            [
              RoleConst.ADMIN,
              PermissionConst.RESOURCE_APPLICATION_OVERVIEW_EMBED
            ],
            'OR'
    ),
    overview_access: () =>
      hasPermission(
            [
              RoleConst.ADMIN,
              PermissionConst.RESOURCE_APPLICATION_OVERVIEW_ACCESS
            ],
            'OR'
    ),
    overview_display: () =>
        hasPermission(
            [
              RoleConst.ADMIN,
              PermissionConst.RESOURCE_APPLICATION_OVERVIEW_DISPLAY
            ],
            'OR'
    ),
    overview_api_key: () =>
        hasPermission(
            [
              RoleConst.ADMIN,
              PermissionConst.RESOURCE_APPLICATION_OVERVIEW_API_KEY
            ],
            'OR'
    ),
    access_edit: () =>
        hasPermission(
            [
              RoleConst.ADMIN,
              PermissionConst.RESOURCE_APPLICATION_ACCESS_EDIT
            ],
            'OR'
    ),
    application_chat_user_edit: () =>
        hasPermission(
            [
              RoleConst.ADMIN,
              PermissionConst.RESOURCE_APPLICATION_CHAT_USER_EDIT
            ],
            'OR'
    ),
    chat_log_clear: () =>
        hasPermission(
            [
              RoleConst.ADMIN,
              PermissionConst.RESOURCE_APPLICATION_CHAT_LOG_CLEAR_POLICY
            ],
            'OR'
    ),
    chat_log_export: () =>
        hasPermission(
            [
              RoleConst.ADMIN,
              PermissionConst.RESOURCE_APPLICATION_CHAT_LOG_EXPORT
            ],
            'OR'
    ),
    chat_log_add_knowledge: () =>
        hasPermission(
            [
              RoleConst.ADMIN,
              PermissionConst.RESOURCE_APPLICATION_CHAT_LOG_ADD_KNOWLEDGE
            ],
            'OR'
    ),
    overview_read: () => 
      hasPermission(
        [
          RoleConst.ADMIN,
          PermissionConst.RESOURCE_APPLICATION_OVERVIEW_READ
        ],
        'OR'
    ),
    access_read: () => 
      hasPermission(
        [
          RoleConst.ADMIN,
          PermissionConst.RESOURCE_APPLICATION_ACCESS_READ
        ],'OR'    
    ),
    chat_user_read: () => 
      hasPermission(
        [
          RoleConst.ADMIN,
          PermissionConst.RESOURCE_APPLICATION_CHAT_USER_READ
        ],'OR'
    ),
    chat_user_edit: () =>false,

    chat_log_read: () => 
      hasPermission(
        [
          RoleConst.ADMIN,
          PermissionConst.RESOURCE_APPLICATION_CHAT_LOG_READ
        ],
        'OR')
}
export default systemManage
