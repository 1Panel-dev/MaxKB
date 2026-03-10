# 对话日志API接口文档

## 1. 概述

本文档详细描述了AI-RAG系统中用于获取和管理对话日志的API接口，包括应用级别的对话记录管理和用户级别的对话历史查询等功能。

## 2. 接口分类

### 2.1 应用级别对话日志接口

| 接口名称 | URL | 方法 | 功能描述 |
|---------|-----|------|----------|
| 对话记录列表 | `/api/application/{workspace_id}/{application_id}/chat-record/{chat_id}` | GET | 获取指定对话的记录列表 |
| 对话记录分页 | `/api/application/{workspace_id}/{application_id}/chat-record/{chat_id}/page/{current_page}/{page_size}` | GET | 分页获取对话记录 |
| 对话记录详情 | `/api/application/{workspace_id}/{application_id}/chat-record/{chat_id}/record/{chat_record_id}` | GET | 获取对话记录详情 |
| 添加到知识库 | `/api/application/{workspace_id}/{application_id}/chat-record/add-knowledge` | POST | 将对话内容添加到知识库 |
| 获取标注段落列表 | `/api/application/{workspace_id}/{application_id}/chat-record/{chat_id}/record/{chat_record_id}/improve` | GET | 获取对话记录的标注段落列表 |
| 标注段落 | `/api/application/{workspace_id}/{application_id}/chat-record/{chat_id}/record/{chat_record_id}/improve/{knowledge_id}/{document_id}` | PUT | 标注对话记录中的段落 |
| 删除标注 | `/api/application/{workspace_id}/{application_id}/chat-record/{chat_id}/record/{chat_record_id}/improve/{knowledge_id}/{document_id}/{paragraph_id}` | DELETE | 删除对话记录的标注 |

### 2.2 用户级别对话历史接口

| 接口名称 | URL | 方法 | 功能描述 |
|---------|-----|------|----------|
| 历史对话列表 | `/api/chat/historical_conversation` | GET | 获取用户的历史对话列表 |
| 历史对话分页 | `/api/chat/historical_conversation/{current_page}/{page_size}` | GET | 分页获取历史对话 |
| 历史对话详情 | `/api/chat/historical_conversation/{chat_id}` | GET | 获取指定对话的详细信息 |
| 历史对话记录 | `/api/chat/historical_conversation_record/{chat_id}` | GET | 获取指定对话的记录列表 |
| 历史对话记录分页 | `/api/chat/historical_conversation_record/{chat_id}/{current_page}/{page_size}` | GET | 分页获取对话记录 |
| 对话记录详情 | `/api/chat/historical_conversation/{chat_id}/record/{chat_record_id}` | GET | 获取对话记录的详细信息 |

## 3. 应用级别对话日志接口详细说明

### 3.1 对话记录列表接口

#### 接口信息
- **URL**: `/api/application/{workspace_id}/{application_id}/chat-record/{chat_id}`
- **方法**: GET
- **认证**: Token认证
- **权限**: 需要应用对话日志读取权限

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
    },
    // 更多记录...
  ]
}
```

### 3.2 对话记录分页接口

#### 接口信息
- **URL**: `/api/application/{workspace_id}/{application_id}/chat-record/{chat_id}/page/{current_page}/{page_size}`
- **方法**: GET
- **认证**: Token认证
- **权限**: 需要应用对话日志读取权限

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| application_id | path | string | 是 | 应用ID |
| chat_id | path | string | 是 | 对话ID |
| current_page | path | integer | 是 | 当前页码 |
| page_size | path | integer | 是 | 每页大小 |
| search_type | query | string | 否 | 搜索类型 |
| search_text | query | string | 否 | 搜索文本 |
| start_time | query | string | 否 | 开始时间 |
| end_time | query | string | 否 | 结束时间 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [
      {
        "id": "record123",
        "chat_id": "chat123",
        "problem_text": "如何使用MaxKB",
        "answer_text": "MaxKB是一个智能客服平台...",
        "create_time": "2025-01-01 10:00:00",
        "tokens": 100,
        "star": 1,
        "trample": 0
      },
      // 更多记录...
    ],
    "total": 100,
    "size": 20,
    "current": 1,
    "pages": 5
  }
}
```

### 3.3 对话记录详情接口

#### 接口信息
- **URL**: `/api/application/{workspace_id}/{application_id}/chat-record/{chat_id}/record/{chat_record_id}`
- **方法**: GET
- **认证**: Token认证
- **权限**: 需要应用对话日志读取权限

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| application_id | path | string | 是 | 应用ID |
| chat_id | path | string | 是 | 对话ID |
| chat_record_id | path | string | 是 | 对话记录ID |

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
    "tokens": 100,
    "star": 1,
    "trample": 0,
    "execution_details": [
      // 执行详情...
    ]
  }
}
```

### 3.4 添加到知识库接口

#### 接口信息
- **URL**: `/api/application/{workspace_id}/{application_id}/chat-record/add-knowledge`
- **方法**: POST
- **认证**: Token认证
- **权限**: 需要应用对话日志添加知识权限

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| application_id | path | string | 是 | 应用ID |
| knowledge_id | body | string | 是 | 知识库ID |
| document_id | body | string | 是 | 文档ID |
| content | body | string | 是 | 要添加的内容 |
| title | body | string | 是 | 标题 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "success",
    "message": "添加成功"
  }
}
```

### 3.5 获取标注段落列表接口

#### 接口信息
- **URL**: `/api/application/{workspace_id}/{application_id}/chat-record/{chat_id}/record/{chat_record_id}/improve`
- **方法**: GET
- **认证**: Token认证
- **权限**: 需要应用对话日志标注权限

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| application_id | path | string | 是 | 应用ID |
| chat_id | path | string | 是 | 对话ID |
| chat_record_id | path | string | 是 | 对话记录ID |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "paragraph123",
      "content": "MaxKB是一个智能客服平台...",
      "start_index": 0,
      "end_index": 100
    },
    // 更多段落...
  ]
}
```

### 3.6 标注段落接口

#### 接口信息
- **URL**: `/api/application/{workspace_id}/{application_id}/chat-record/{chat_id}/record/{chat_record_id}/improve/{knowledge_id}/{document_id}`
- **方法**: PUT
- **认证**: Token认证
- **权限**: 需要应用对话日志标注权限

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| application_id | path | string | 是 | 应用ID |
| chat_id | path | string | 是 | 对话ID |
| chat_record_id | path | string | 是 | 对话记录ID |
| knowledge_id | path | string | 是 | 知识库ID |
| document_id | path | string | 是 | 文档ID |
| content | body | string | 是 | 标注内容 |
| start_index | body | integer | 是 | 开始索引 |
| end_index | body | integer | 是 | 结束索引 |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "success",
    "message": "标注成功"
  }
}
```

### 3.7 删除标注接口

#### 接口信息
- **URL**: `/api/application/{workspace_id}/{application_id}/chat-record/{chat_id}/record/{chat_record_id}/improve/{knowledge_id}/{document_id}/{paragraph_id}`
- **方法**: DELETE
- **认证**: Token认证
- **权限**: 需要应用对话日志标注权限

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| workspace_id | path | string | 是 | 工作空间ID |
| application_id | path | string | 是 | 应用ID |
| chat_id | path | string | 是 | 对话ID |
| chat_record_id | path | string | 是 | 对话记录ID |
| knowledge_id | path | string | 是 | 知识库ID |
| document_id | path | string | 是 | 文档ID |
| paragraph_id | path | string | 是 | 段落ID |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "success",
    "message": "删除成功"
  }
}
```

## 4. 用户级别对话历史接口详细说明

### 4.1 历史对话列表接口

#### 接口信息
- **URL**: `/api/chat/historical_conversation`
- **方法**: GET
- **认证**: Token认证
- **权限**: 无需特殊权限（基于Token获取当前用户数据）

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
    },
    // 更多对话...
  ]
}
```

### 4.2 历史对话分页接口

#### 接口信息
- **URL**: `/api/chat/historical_conversation/{current_page}/{page_size}`
- **方法**: GET
- **认证**: Token认证
- **权限**: 无需特殊权限（基于Token获取当前用户数据）

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
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
        "id": "chat123",
        "abstract": "如何使用MaxKB",
        "create_time": "2025-01-01 10:00:00",
        "update_time": "2025-01-01 10:05:00"
      },
      // 更多对话...
    ],
    "total": 50,
    "size": 20,
    "current": 1,
    "pages": 3
  }
}
```

### 4.3 历史对话详情接口

#### 接口信息
- **URL**: `/api/chat/historical_conversation/{chat_id}`
- **方法**: GET
- **认证**: Token认证
- **权限**: 无需特殊权限（基于Token获取当前用户数据）

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| chat_id | path | string | 是 | 对话ID |

#### 响应数据

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "chat123",
    "abstract": "如何使用MaxKB",
    "create_time": "2025-01-01 10:00:00",
    "update_time": "2025-01-01 10:05:00"
  }
}
```

### 4.4 历史对话记录接口

#### 接口信息
- **URL**: `/api/chat/historical_conversation_record/{chat_id}`
- **方法**: GET
- **认证**: Token认证
- **权限**: 无需特殊权限（基于Token获取当前用户数据）

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| chat_id | path | string | 是 | 对话ID |

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
      "tokens": 100
    },
    // 更多记录...
  ]
}
```

### 4.5 历史对话记录分页接口

#### 接口信息
- **URL**: `/api/chat/historical_conversation_record/{chat_id}/{current_page}/{page_size}`
- **方法**: GET
- **认证**: Token认证
- **权限**: 无需特殊权限（基于Token获取当前用户数据）

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| chat_id | path | string | 是 | 对话ID |
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
        "id": "record123",
        "chat_id": "chat123",
        "problem_text": "如何使用MaxKB",
        "answer_text": "MaxKB是一个智能客服平台...",
        "create_time": "2025-01-01 10:00:00",
        "tokens": 100
      },
      // 更多记录...
    ],
    "total": 30,
    "size": 10,
    "current": 1,
    "pages": 3
  }
}
```

### 4.6 对话记录详情接口

#### 接口信息
- **URL**: `/api/chat/historical_conversation/{chat_id}/record/{chat_record_id}`
- **方法**: GET
- **认证**: Token认证
- **权限**: 无需特殊权限（基于Token获取当前用户数据）

#### 请求参数

| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
| chat_id | path | string | 是 | 对话ID |
| chat_record_id | path | string | 是 | 对话记录ID |

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
    "tokens": 100,
    "execution_details": [
      // 执行详情...
    ]
  }
}
```

## 5. 权限说明

### 5.1 应用级别接口权限

| 接口类型 | 所需权限 |
|---------|----------|
| 对话记录查询 | 应用对话日志读取权限 |
| 添加到知识库 | 应用对话日志添加知识权限 |
| 段落标注 | 应用对话日志标注权限 |

### 5.2 用户级别接口权限

用户级别接口基于Token认证，自动获取当前用户的对话数据，无需额外权限。

## 6. 示例请求

### 6.1 应用级别示例

```bash
# 获取对话记录列表
curl -X GET "http://localhost:8080/api/application/workspace1/application1/chat-record/chat123?search_text=MaxKB" \
  -H "Authorization: Bearer your_token_here"

# 分页获取对话记录
curl -X GET "http://localhost:8080/api/application/workspace1/application1/chat-record/chat123/page/1/20" \
  -H "Authorization: Bearer your_token_here"

# 添加到知识库
curl -X POST "http://localhost:8080/api/application/workspace1/application1/chat-record/add-knowledge" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{"knowledge_id": "knowledge123", "document_id": "doc123", "content": "MaxKB使用指南", "title": "如何使用MaxKB"}'
```

### 6.2 用户级别示例

```bash
# 获取历史对话列表
curl -X GET "http://localhost:8080/api/chat/historical_conversation" \
  -H "Authorization: Bearer your_token_here"

# 分页获取历史对话
curl -X GET "http://localhost:8080/api/chat/historical_conversation/1/20" \
  -H "Authorization: Bearer your_token_here"

# 获取对话记录
curl -X GET "http://localhost:8080/api/chat/historical_conversation_record/chat123" \
  -H "Authorization: Bearer your_token_here"
```

## 7. 错误响应

| 错误码 | 描述 |
|--------|------|
| 401 | 未授权，Token无效或过期 |
| 403 | 无权限访问该资源 |
| 404 | 对话或记录不存在 |
| 500 | 服务器内部错误 |

## 8. 数据来源

- 对话记录数据：来自 `application_chat_record` 表
- 对话历史数据：来自 `application_chat` 表
- 用户数据：来自 `application_chat_user` 表

## 9. Token获取方式

### 9.1 用户登录获取Token

#### 接口信息
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

### 9.2 应用访问令牌

系统还支持应用级别的访问令牌，通过`ApplicationAccessToken`模型生成，用于应用间的API调用。

### 9.3 Token使用方式

获取token后，在调用其他API接口时，需要在请求头中添加：

```
Authorization: Bearer your_token_here
```

## 10. 注意事项

1. 应用级别接口需要指定工作空间和应用ID，用户级别接口基于Token自动获取
2. 所有接口都需要有效的Token认证
3. 对于大量数据的查询，建议使用分页接口
4. 标注功能需要先获取标注段落列表，然后进行标注操作
5. 添加到知识库功能需要指定目标知识库和文档
6. Token有过期时间，过期后需要重新获取
7. 登录失败次数过多时，需要输入验证码