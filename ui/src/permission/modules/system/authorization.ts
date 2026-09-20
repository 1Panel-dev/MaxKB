/** 系统「资源授权」按钮权限（按资源类型分组）。$perm.authorization.application.read() ... */

import { canSys } from '../../policy'
import { PermissionConstants as P } from '../../core'

export default {
  /**
   * 系统「资源授权」智能体权限
   * */
  application: {
    /**
     * 系统「资源授权」智能体只读权限
     * */
    read: () => canSys(P.APPLICATION_RESOURCE_PERMISSION_READ), edit: () => canSys(P.APPLICATION_RESOURCE_PERMISSION_EDIT) },
  /**
   * 系统「资源授权」知识库权限
   * */
  knowledge: {
    /**
     * 系统「资源授权」知识库只读权限
     * */
    read: () => canSys(P.KNOWLEDGE_RESOURCE_PERMISSION_READ), edit: () => canSys(P.KNOWLEDGE_RESOURCE_PERMISSION_EDIT) },
  /**
   * 系统「资源授权」工具权限
   * */
  tool: {
    /**
     * 系统「资源授权」工具只读权限
     * */
    read: () => canSys(P.TOOL_RESOURCE_PERMISSION_READ), edit: () => canSys(P.TOOL_RESOURCE_PERMISSION_EDIT) },
  /**
   * 系统「资源授权」模型权限
   * */
  model: {
    /**
     * 系统「资源授权」模型只读权限
     * */
    read: () => canSys(P.MODEL_RESOURCE_PERMISSION_READ), edit: () => canSys(P.MODEL_RESOURCE_PERMISSION_EDIT) },
}
