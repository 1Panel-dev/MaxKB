# MaxKB API Development Rules

## API Design Principles

### URL Structure
- Use workspace-based routing: `/workspace/{workspace_id}/resource`
- Follow RESTful conventions for resource operations
- Use kebab-case for URL segments
- Include version information when needed
- Example: `/workspace/123/knowledge/456/document`

### HTTP Methods
- GET: Retrieve resources (list or detail)
- POST: Create new resources
- PUT: Update existing resources (full update)
- PATCH: Partial updates
- DELETE: Remove resources

### Response Format
Always use the standardized response format from `common.result`:
```python
# Success response
return result.success(data)

# Error response  
return result.error(message, code)

# Paginated response
return result.page(data, total, page, size)
```

### Authentication & Authorization
- Use `TokenAuth` for API authentication
- Implement `@has_permissions` decorator for authorization
- Check workspace permissions for workspace-scoped resources
- Use role-based access control (RBAC)
- Example:
```python
@has_permissions(ViewPermission([RoleConstants.ADMIN, RoleConstants.USER]))
def get(self, request, workspace_id):
    pass
```

## Serializer Patterns

### Input Validation
- Create dedicated serializers for request validation
- Use Django REST Framework field validators
- Implement custom validation methods when needed
- Handle file uploads with `UploadedFileField`

### Output Serialization
- Create model serializers for consistent output
- Use `SerializerMethodField` for computed fields
- Implement nested serialization for related objects
- Handle sensitive data appropriately

### Example Serializer Structure
```python
class KnowledgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Knowledge
        fields = ['id', 'name', 'desc', 'created_time']
    
    def validate_name(self, value):
        # Custom validation logic
        return value
```

## Error Handling

### Custom Exceptions
- Use `AppApiException` for application-specific errors
- Provide meaningful error messages
- Include appropriate HTTP status codes
- Support internationalization for error messages

### Exception Handling Pattern
```python
try:
    # Business logic
    pass
except Exception as e:
    raise AppApiException(500, _('Operation failed'))
```

## Database Operations

### Query Optimization
- Use `select_related()` for foreign key relationships
- Use `prefetch_related()` for many-to-many relationships
- Implement proper filtering and pagination
- Use database indexes for frequently queried fields

### Transaction Management
- Use `@transaction.atomic` for data consistency
- Handle database rollbacks properly
- Implement proper error handling in transactions

## Pagination

### Standard Pagination
- Use consistent pagination parameters: `current_page`, `page_size`
- Implement pagination in URL path: `/{current_page}/{page_size}`
- Return total count and page information
- Support filtering and sorting with pagination

### Pagination Implementation
```python
def get(self, request, workspace_id, current_page, page_size):
    return result.success(
        native_page_search(
            queryset, 
            select_string, 
            with_search_params, 
            current_page, 
            page_size
        )
    )
```

## File Upload Handling

### File Processing
- Support multiple file formats (PDF, DOCX, TXT, etc.)
- Implement file size and type validation
- Use secure file storage mechanisms
- Handle file processing asynchronously when needed

### Upload API Pattern
```python
class DocumentUploadView(APIView):
    def post(self, request, workspace_id, knowledge_id):
        files = request.FILES.getlist('file')
        # Process files
        return result.success(processed_data)
```

## Frontend TypeScript Interface Patterns

### API Response Types
- Define interfaces for all API responses
- Use generic types for paginated responses
- Include optional fields with proper typing
- Example:
```typescript
interface ChatProfile {
  id: string
  name: string
  avatar?: string
  status: 'online' | 'offline' | 'busy'
  created_time: string
}

interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

interface PageResponse<T> extends ApiResponse<T[]> {
  total: number
  current_page: number
  page_size: number
}
```

### Request/Response Mapping
- Create TypeScript interfaces that match Django serializers
- Use consistent naming conventions between frontend and backend
- Handle optional and nullable fields properly
- Implement proper error type definitions

## Testing APIs

### Test Structure
- Create test cases for all API endpoints
- Test both success and error scenarios
- Use Django's test client for API testing
- Mock external dependencies

### Test Example
```python
class KnowledgeAPITest(TestCase):
    def test_create_knowledge(self):
        response = self.client.post('/api/knowledge', data)
        self.assertEqual(response.status_code, 200)
```

## Performance Considerations

### Caching
- Use Redis for caching frequently accessed data
- Implement cache invalidation strategies
- Cache expensive database queries
- Use cache decorators where appropriate

### Query Optimization
- Monitor database query performance
- Use database query analysis tools
- Implement proper indexing strategies
- Avoid N+1 query problems

## Security Best Practices

### Input Validation
- Validate all user inputs
- Sanitize file uploads
- Implement rate limiting
- Use CSRF protection

### Data Protection
- Hash sensitive data
- Use secure random tokens
- Implement proper session management
- Follow OWASP security guidelines
