# AI-RAG API接口参数文档

## 1. 概述

本文档详细描述了MaxKB系统中所有API接口的参数信息，包括用户管理、应用管理、对话管理、知识库管理等模块的接口。

## 2. 用户管理接口

### 2.1 登录接口

- **URL**: `/api/users/login`
- **方法**: POST
- **认证**: 无需认证

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |
| captcha | string | 否 | 验证码（登录失败次数超过阈值时需要） |
| encryptedData | string | 否 | 加密数据 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 2.2 登出接口

- **URL**: `/api/users/logout`
- **方法**: POST
- **认证**: Token认证

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": true
}
```

### 2.3 获取验证码接口

- **URL**: `/api/users/captcha`
- **方法**: GET
- **认证**: 无需认证

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| username | string | 否 | 用户名 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "captcha": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
  }
}
```

### 2.4 用户个人信息接口

- **URL**: `/api/users/profile`
- **方法**: GET
- **认证**: Token认证

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "user123",
    "username": "admin",
    "email": "admin@example.com",
    "is_active": true
  }
}
```

### 2.5 切换语言接口

- **URL**: `/api/users/language`
- **方法**: POST
- **认证**: Token认证

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| language | string | 是 | 语言代码（如：zh-CN, en-US） |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": true
}
```

## 3. 应用管理接口

### 3.1 应用列表接口

- **URL**: `/api/application/workspace/{workspace_id}/application`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "app123",
      "name": "测试应用",
      "description": "这是一个测试应用",
      "workspace_id": "workspace1",
      "create_time": "2025-01-01 10:00:00"
    }
  ]
}
```

### 3.2 应用分页接口

- **URL**: `/api/application/workspace/{workspace_id}/application/{current_page}/{page_size}`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| current_page | path | integer | 是 | 当前页码 |
| page_size | path | integer | 是 | 每页大小 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [
      {
        "id": "app123",
        "name": "测试应用",
        "description": "这是一个测试应用"
      }
    ],
    "total": 10,
    "size": 20,
    "current": 1,
    "pages": 1
  }
}
```

### 3.3 应用详情接口

- **URL**: `/api/application/workspace/{workspace_id}/application/{application_id}`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| application_id | path | string | 是 | 应用ID |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "app123",
    "name": "测试应用",
    "description": "这是一个测试应用",
    "workspace_id": "workspace1",
    "create_time": "2025-01-01 10:00:00",
    "update_time": "2025-01-02 10:00:00"
  }
}
```

### 3.4 创建应用接口

- **URL**: `/api/application/workspace/{workspace_id}/application`
- **方法**: POST
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| name | body | string | 是 | 应用名称 |
| description | body | string | 否 | 应用描述 |
| type | body | string | 是 | 应用类型 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "app123",
    "name": "测试应用"
  }
}
```

### 3.5 更新应用接口

- **URL**: `/api/application/workspace/{workspace_id}/application/{application_id}`
- **方法**: PUT
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| application_id | path | string | 是 | 应用ID |
| name | body | string | 否 | 应用名称 |
| description | body | string | 否 | 应用描述 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": true
}
```

### 3.6 删除应用接口

- **URL**: `/api/application/workspace/{workspace_id}/application/{application_id}`
- **方法**: DELETE
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| application_id | path | string | 是 | 应用ID |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": true
}
```

## 4. 监控统计接口

### 4.1 对话统计趋势接口

- **URL**: `/api/application/{workspace_id}/{application_id}/stats`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| application_id | path | string | 是 | 应用ID |
| start_time | query | string | 是 | 开始时间，格式：YYYY-MM-DD |
| end_time | query | string | 是 | 结束时间，格式：YYYY-MM-DD |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "chat_record_count": 10,
      "customer_added_count": 5,
      "customer_num": 100,
      "day": "2025-01-01",
      "star_num": 8,
      "tokens_num": 1000,
      "trample_num": 2
    }
  ]
}
```

### 4.2 Token使用统计接口

- **URL**: `/api/application/{workspace_id}/{application_id}/stats/token-usage`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| application_id | path | string | 是 | 应用ID |
| start_time | query | string | 是 | 开始时间，格式：YYYY-MM-DD |
| end_time | query | string | 是 | 结束时间，格式：YYYY-MM-DD |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "chat_user_id": "user123",
      "nick_name": "用户1",
      "tokens_num": 5000
    }
  ]
}
```

### 4.3 热门问题统计接口

- **URL**: `/api/application/{workspace_id}/{application_id}/stats/top-questions`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| application_id | path | string | 是 | 应用ID |
| start_time | query | string | 是 | 开始时间，格式：YYYY-MM-DD |
| end_time | query | string | 是 | 结束时间，格式：YYYY-MM-DD |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "problem_text": "如何使用MaxKB",
      "count": 50
    }
  ]
}
```

## 5. 对话管理接口

### 5.1 应用级别对话记录列表接口

- **URL**: `/api/application/{workspace_id}/{application_id}/chat-record/{chat_id}`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| application_id | path | string | 是 | 应用ID |
| chat_id | path | string | 是 | 对话ID |
| search_type | query | string | 否 | 搜索类型 |
| search_text | query | string | 否 | 搜索文本 |
| start_time | query | string | 否 | 开始时间 |
| end_time | query | string | 否 | 结束时间 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "record123",
      "chat_id": "chat123",
      "problem_text": "如何使用MaxKB",
      "answer_text": "MaxKB是一个智能客服平台...",
      "create_time": "2025-01-01 10:00:00",
      "tokens": 100,
      "star": 1,
      "trample": 0
    }
  ]
}
```

### 5.2 用户级别历史对话列表接口

- **URL**: `/api/chat/historical_conversation`
- **方法**: GET
- **认证**: Token认证

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "chat123",
      "abstract": "如何使用MaxKB",
      "create_time": "2025-01-01 10:00:00",
      "update_time": "2025-01-01 10:05:00"
    }
  ]
}
```

### 5.3 发送消息接口

- **URL**: `/api/chat/chat_message/{chat_id}`
- **方法**: POST
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| chat_id | path | string | 是 | 对话ID |
| message_list | body | array | 是 | 消息列表 |
| problem_text | body | string | 是 | 用户问题 |
| stream | body | boolean | 否 | 是否使用流的形式输出 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "record123",
    "chat_id": "chat123",
    "problem_text": "如何使用MaxKB",
    "answer_text": "MaxKB是一个智能客服平台...",
    "create_time": "2025-01-01 10:00:00",
    "tokens": 100
  }
}
```

## 6. 知识库管理接口

### 6.1 知识库列表接口

- **URL**: `/api/knowledge/workspace/{workspace_id}/knowledge`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "knowledge123",
      "name": "测试知识库",
      "description": "这是一个测试知识库",
      "workspace_id": "workspace1",
      "create_time": "2025-01-01 10:00:00"
    }
  ]
}
```

### 6.2 知识库分页接口

- **URL**: `/api/knowledge/workspace/{workspace_id}/knowledge/{current_page}/{page_size}`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| current_page | path | integer | 是 | 当前页码 |
| page_size | path | integer | 是 | 每页大小 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [
      {
        "id": "knowledge123",
        "name": "测试知识库",
        "description": "这是一个测试知识库"
      }
    ],
    "total": 5,
    "size": 20,
    "current": 1,
    "pages": 1
  }
}
```

### 6.3 文档列表接口

- **URL**: `/api/knowledge/workspace/{workspace_id}/knowledge/{knowledge_id}/document`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| knowledge_id | path | string | 是 | 知识库ID |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "doc123",
      "name": "测试文档",
      "knowledge_id": "knowledge123",
      "create_time": "2025-01-01 10:00:00"
    }
  ]
}
```

### 6.4 段落列表接口

- **URL**: `/api/knowledge/workspace/{workspace_id}/knowledge/{knowledge_id}/document/{document_id}/paragraph`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| knowledge_id | path | string | 是 | 知识库ID |
| document_id | path | string | 是 | 文档ID |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "paragraph123",
      "content": "这是一段测试内容",
      "document_id": "doc123",
      "create_time": "2025-01-01 10:00:00"
    }
  ]
}
```

## 7. Token获取方式

### 7.1 用户登录获取Token

- **URL**: `/api/users/login`
- **方法**: POST
- **认证**: 无需认证

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |
| captcha | string | 否 | 验证码（登录失败次数超过阈值时需要） |
| encryptedData | string | 否 | 加密数据 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 7.2 应用访问令牌

系统还支持应用级别的访问令牌，通过`ApplicationAccessToken`模型生成，用于应用间的API调用。

### 7.3 Token使用方式

获取token后，在调用其他API接口时，需要在请求头中添加：

```
Authorization: Bearer your_token_here
```

## 8. 通用参数说明

### 8.1 分页参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| current_page | integer | 当前页码，从1开始 |
| page_size | integer | 每页大小，默认20 |

### 8.2 时间参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| start_time | string | 开始时间，格式：YYYY-MM-DD |
| end_time | string | 结束时间，格式：YYYY-MM-DD |

### 8.3 搜索参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| search_text | string | 搜索文本 |
| search_type | string | 搜索类型 |

## 9. 响应格式

所有API接口的响应格式统一为：

```json
{
  "code": 200,          // 状态码，200表示成功
  "message": "success",  // 消息，success表示成功
  "data": {}            // 数据，根据接口不同返回不同结构
}
```

### 9.1 错误响应

| 错误码 | 描述 |
|--------|------|
| 401 | 未授权，Token无效或过期 |
| 403 | 无权限访问该资源 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 7. 系统管理接口

### 7.1 工作空间用户资源权限接口

- **URL**: `/api/system_manage/workspace/{workspace_id}/user_resource_permission/user/{user_id}/resource/{resource}`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| user_id | path | string | 是 | 用户ID |
| resource | path | string | 是 | 资源类型 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "resource_id": "resource123",
      "resource_name": "测试资源",
      "has_permission": true
    }
  ]
}
```

### 7.2 工作空间用户资源权限分页接口

- **URL**: `/api/system_manage/workspace/{workspace_id}/user_resource_permission/user/{user_id}/resource/{resource}/{current_page}/{page_size}`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| user_id | path | string | 是 | 用户ID |
| resource | path | string | 是 | 资源类型 |
| current_page | path | integer | 是 | 当前页码 |
| page_size | path | integer | 是 | 每页大小 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [
      {
        "resource_id": "resource123",
        "resource_name": "测试资源",
        "has_permission": true
      }
    ],
    "total": 10,
    "size": 20,
    "current": 1,
    "pages": 1
  }
}
```

### 7.3 邮件设置接口

- **URL**: `/api/system_manage/email_setting`
- **方法**: GET, POST
- **认证**: Token认证

#### 请求参数 (POST)

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| smtp_server | string | 是 | SMTP服务器 |
| smtp_port | integer | 是 | SMTP端口 |
| smtp_username | string | 是 | SMTP用户名 |
| smtp_password | string | 是 | SMTP密码 |
| sender_email | string | 是 | 发件人邮箱 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "smtp_server": "smtp.example.com",
    "smtp_port": 587,
    "smtp_username": "admin@example.com",
    "sender_email": "admin@example.com"
  }
}
```

### 7.4 系统配置接口

- **URL**: `/api/system_manage/config`
- **方法**: GET
- **认证**: Token认证

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "system_name": "MaxKB",
    "version": "1.0.0",
    "admin_path": "/admin"
  }
}
```

## 8. 工具管理接口

### 8.1 工具列表接口

- **URL**: `/api/tool/workspace/{workspace_id}/tool`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "tool123",
      "name": "测试工具",
      "description": "这是一个测试工具",
      "workspace_id": "workspace1",
      "create_time": "2025-01-01 10:00:00"
    }
  ]
}
```

### 8.2 工具分页接口

- **URL**: `/api/tool/workspace/{workspace_id}/tool/{current_page}/{page_size}`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| current_page | path | integer | 是 | 当前页码 |
| page_size | path | integer | 是 | 每页大小 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [
      {
        "id": "tool123",
        "name": "测试工具",
        "description": "这是一个测试工具"
      }
    ],
    "total": 5,
    "size": 20,
    "current": 1,
    "pages": 1
  }
}
```

### 8.3 工具详情接口

- **URL**: `/api/tool/workspace/{workspace_id}/tool/{tool_id}`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| tool_id | path | string | 是 | 工具ID |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "tool123",
    "name": "测试工具",
    "description": "这是一个测试工具",
    "workspace_id": "workspace1",
    "create_time": "2025-01-01 10:00:00"
  }
}
```

### 8.4 测试工具连接接口

- **URL**: `/api/tool/workspace/{workspace_id}/tool/test_connection`
- **方法**: POST
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| tool_id | body | string | 是 | 工具ID |
| config | body | object | 是 | 工具配置 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "success": true,
    "message": "连接成功"
  }
}
```

## 9. OSS接口

### 9.1 文件上传接口

- **URL**: `/api/oss/file`
- **方法**: POST
- **认证**: Token认证

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| file | file | 是 | 上传的文件 |
| type | string | 是 | 文件类型 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "file_url": "http://example.com/files/test.png",
    "file_name": "test.png",
    "file_size": 102400
  }
}
```

## 10. 文件夹管理接口

### 10.1 文件夹列表接口

- **URL**: `/api/folder/workspace/{workspace_id}/{source}/folder`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| source | path | string | 是 | 资源类型（如：application, knowledge） |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "folder123",
      "name": "测试文件夹",
      "parent_id": null,
      "workspace_id": "workspace1",
      "source": "application",
      "create_time": "2025-01-01 10:00:00"
    }
  ]
}
```

### 10.2 创建文件夹接口

- **URL**: `/api/folder/workspace/{workspace_id}/{source}/folder`
- **方法**: POST
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| source | path | string | 是 | 资源类型（如：application, knowledge） |
| name | body | string | 是 | 文件夹名称 |
| parent_id | body | string | 否 | 父文件夹ID |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "folder123",
    "name": "测试文件夹",
    "parent_id": null,
    "workspace_id": "workspace1",
    "source": "application"
  }
}
```

### 10.3 更新文件夹接口

- **URL**: `/api/folder/workspace/{workspace_id}/{source}/folder/{folder_id}`
- **方法**: PUT
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| source | path | string | 是 | 资源类型（如：application, knowledge） |
| folder_id | path | string | 是 | 文件夹ID |
| name | body | string | 是 | 文件夹名称 |
| parent_id | body | string | 否 | 父文件夹ID |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": true
}
```

### 10.4 删除文件夹接口

- **URL**: `/api/folder/workspace/{workspace_id}/{source}/folder/{folder_id}`
- **方法**: DELETE
- **认证**: Token认证

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| source | path | string | 是 | 资源类型（如：application, knowledge） |
| folder_id | path | string | 是 | 文件夹ID |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": true
}
```

## 11. 模型提供商接口

### 11.1 模型提供商列表接口

- **URL**: `/api/models_provider/provider`
- **方法**: GET
- **认证**: Token认证

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "provider123",
      "name": "OpenAI",
      "type": "llm",
      "status": "active"
    }
  ]
}
```

### 11.2 模型类型列表接口

- **URL**: `/api/models_provider/provider/model_type_list`
- **方法**: GET
- **认证**: Token认证

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "type": "llm",
      "name": "大语言模型"
    },
    {
      "type": "embedding",
      "name": "嵌入模型"
    }
  ]
}
```

### 11.3 模型列表接口

- **URL**: `/api/models_provider/provider/model_list`
- **方法**: GET
- **认证**: Token认证

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| provider_id | string | 是 | 提供商ID |
| model_type | string | 是 | 模型类型 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "model123",
      "name": "gpt-4",
      "description": "OpenAI GPT-4模型"
    }
  ]
}
```

### 11.4 工作空间模型设置接口

- **URL**: `/api/models_provider/workspace/{workspace_id}/model`
- **方法**: GET, POST
- **认证**: Token认证

#### 请求参数 (POST)

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| provider_id | body | string | 是 | 提供商ID |
| model_id | body | string | 是 | 模型ID |
| api_key | body | string | 是 | API密钥 |
| base_url | body | string | 否 | 基础URL |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "model_setting123",
    "provider_id": "provider123",
    "model_id": "model123",
    "workspace_id": "workspace1"
  }
}
```

## 12. 通用参数说明

### 12.1 分页参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| current_page | integer | 当前页码，从1开始 |
| page_size | integer | 每页大小，默认20 |

### 12.2 时间参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| start_time | string | 开始时间，格式：YYYY-MM-DD |
| end_time | string | 结束时间，格式：YYYY-MM-DD |

### 12.3 搜索参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| search_text | string | 搜索文本 |
| search_type | string | 搜索类型 |

## 13. 响应格式

所有API接口的响应格式统一为：

```json
{
  "code": 200,          // 状态码，200表示成功
  "message": "success",  // 消息，success表示成功
  "data": {}            // 数据，根据接口不同返回不同结构
}
```

### 13.1 错误响应

| 错误码 | 描述 |
|--------|------|
| 401 | 未授权，Token无效或过期 |
| 403 | 无权限访问该资源 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 14. 注意事项

1. 所有接口都需要有效的Token认证
2. Token有过期时间，过期后需要重新获取
3. 登录失败次数过多时，需要输入验证码
4. 对于大量数据的查询，建议使用分页接口
5. 时间格式必须为 `YYYY-MM-DD`
6. 路径参数中的ID通常为UUID格式
7. 部分接口需要特定的权限才能访问
8. 上传文件时，需要使用multipart/form-data格式
9. 对于流式输出的接口，响应会分多次返回
10. 接口调用频率过高可能会被限流
