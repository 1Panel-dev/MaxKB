/** 后端资源授权的资源类型。 */
export const RESOURCE_TYPE = { APPLICATION: 'APPLICATION', KNOWLEDGE: 'KNOWLEDGE', MODEL: 'MODEL', TOOL: 'TOOL' } as const

/** 后端资源授权的权限值。 */
export const RESOURCE_PERMISSION = { MANAGE: 'MANAGE', NOT_AUTH: 'NOT_AUTH', ROLE: 'ROLE', VIEW: 'VIEW' } as const
