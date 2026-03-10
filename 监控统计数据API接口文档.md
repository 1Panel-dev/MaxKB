# 监控统计数据API接口文档

## 1. 概述

本文档详细描述了AI-RAG系统中用于获取监控统计数据的API接口，包括对话统计趋势、Token使用统计和热门问题统计等功能。

## 2. 接口列表

| 接口名称 | URL | 方法 | 功能描述 |
|---------|-----|------|----------|
| 对话统计趋势 | `/api/application/{workspace_id}/{application_id}/stats` | GET | 获取应用的对话相关统计趋势数据 |
| Token使用统计 | `/api/application/{workspace_id}/{application_id}/stats/token-usage` | GET | 获取应用的Token使用统计数据 |
| 热门问题统计 | `/api/application/{workspace_id}/{application_id}/stats/top-questions` | GET | 获取应用的热门问题统计数据 |

## 3. 接口详细说明

### 3.1 对话统计趋势接口

#### 接口信息
- **URL**: `/api/application/{workspace_id}/{application_id}/stats`
- **方法**: GET
- **认证**: Token认证
- **权限**: 需要应用概览读取权限

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
    },
    // 更多日期数据...
  ]
}
```

#### 字段说明
- **chat_record_count**: 对话次数
- **customer_added_count**: 新增用户数
- **customer_num**: 用户总数
- **day**: 日期
- **star_num**: 点赞数
- **tokens_num**: Tokens消耗
- **trample_num**: 踩数

### 3.2 Token使用统计接口

#### 接口信息
- **URL**: `/api/application/{workspace_id}/{application_id}/stats/token-usage`
- **方法**: GET
- **认证**: Token认证
- **权限**: 需要应用概览读取权限

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
    },
    // 更多用户数据...
  ]
}
```

#### 字段说明
- **chat_user_id**: 用户ID
- **nick_name**: 用户昵称
- **tokens_num**: 该用户的Token消耗

### 3.3 热门问题统计接口

#### 接口信息
- **URL**: `/api/application/{workspace_id}/{application_id}/stats/top-questions`
- **方法**: GET
- **认证**: Token认证
- **权限**: 需要应用概览读取权限

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
    },
    // 更多问题数据...
  ]
}
```

#### 字段说明
- **problem_text**: 问题文本
- **count**: 该问题的出现次数

## 4. 权限说明

所有统计接口都需要以下权限之一：
- 应用概览读取权限
- 工作空间管理角色权限
- 具有应用权限的普通用户角色
- 工作空间管理角色

## 5. 时间范围说明

- 开始时间和结束时间均为必填参数
- 时间格式必须为 `YYYY-MM-DD`
- 系统会自动处理时间范围，包括开始日期的 00:00:00 到结束日期的 23:59:59

## 6. 示例请求

### 6.1 对话统计趋势示例

```bash
curl -X GET "http://localhost:8080/api/application/workspace1/application1/stats?start_time=2025-01-01&end_time=2025-01-31" \
  -H "Authorization: Bearer your_token_here"
```

### 6.2 Token使用统计示例

```bash
curl -X GET "http://localhost:8080/api/application/workspace1/application1/stats/token-usage?start_time=2025-01-01&end_time=2025-01-31" \
  -H "Authorization: Bearer your_token_here"
```

### 6.3 热门问题统计示例

```bash
curl -X GET "http://localhost:8080/api/application/workspace1/application1/stats/top-questions?start_time=2025-01-01&end_time=2025-01-31" \
  -H "Authorization: Bearer your_token_here"
```

## 7. 错误响应

| 错误码 | 描述 |
|--------|------|
| 401 | 未授权，Token无效或过期 |
| 403 | 无权限访问该资源 |
| 500 | 应用ID不存在 |
| 500 | 服务器内部错误 |

## 8. 数据来源

- 对话统计数据：来自 `application_chat_record` 表
- 用户统计数据：来自 `ApplicationChatUserStats` 表
- Token使用数据：来自 `application_chat_record` 表中的 `tokens` 字段
- 热门问题数据：来自 `application_chat_record` 表中的 `problem_text` 字段

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

1. 统计数据可能存在一定的延迟，因为数据收集和处理需要时间
2. 对于较大的时间范围，响应时间可能会较长
3. 建议合理设置时间范围，避免请求过大的数据集
4. 所有接口都需要有效的Token认证
5. Token有过期时间，过期后需要重新获取
6. 登录失败次数过多时，需要输入验证码