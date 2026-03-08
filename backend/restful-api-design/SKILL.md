# RESTful API Design and Implementation

## Purpose
Master the design and implementation of high-quality RESTful APIs following REST principles and best practices.

## Use Cases
- Building scalable web APIs
- Designing microservices communication
- Creating mobile-friendly backends
- Public API development
- Third-party integration

## Prerequisites
- Understanding of HTTP protocol
- Basic knowledge of API concepts
- Experience with at least one backend framework

## Core Steps

1. **Understand REST Principles**
   - Resources (nouns, not verbs)
   - HTTP methods (GET, POST, PUT, DELETE, PATCH)
   - Stateless communication
   - Standard status codes

2. **Design Resource Models**
   - Identify entities in your domain
   - Map entities to URLs
   - Define relationships between resources

3. **Choose Versioning Strategy**
   - URL path versioning (`/api/v1/`)
   - Header versioning
   - Accept header versioning

4. **Implement CRUD Operations**
   - Create (POST)
   - Read (GET)
   - Update (PUT/PATCH)
   - Delete (DELETE)

5. **Handle Errors Properly**
   - Consistent error response format
   - Appropriate HTTP status codes
   - Descriptive error messages

6. **Implement Pagination & Filtering**
   - Query parameters for filtering
   - Limit/offset or cursor-based pagination
   - Sorting capabilities

## Key Code Examples

### Python Flask Example
```python
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Sample data
users = {}
next_id = 1

def create_response(data=None, error=None, status_code=200):
    return jsonify({
        'success': error is None,
        'data': data,
        'error': error,
        'meta': {
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0'
        }
    }), status_code

@app.route('/api/v1/users', methods=['GET'])
def list_users():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    # Pagination logic
    user_list = list(users.values())
    start = (page - 1) * limit
    end = start + limit

    return create_response({
        'users': user_list[start:end],
        'total': len(user_list),
        'page': page,
        'limit': limit
    })

@app.route('/api/v1/users', methods=['POST'])
def create_user():
    global next_id
    data = request.get_json()

    if not data or 'name' not in data:
        return create_response(
            error='Name is required',
            status_code=400
        )

    user_id = next_id
    next_id += 1

    user = {
        'id': user_id,
        'name': data['name'],
        'email': data.get('email'),
        'created_at': datetime.utcnow().isoformat()
    }

    users[user_id] = user
    return create_response(user, status_code=201)

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = users.get(user_id)
    if not user:
        return create_response(
            error=f'User {user_id} not found',
            status_code=404
        )
    return create_response(user)

@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = users.get(user_id)
    if not user:
        return create_response(
            error=f'User {user_id} not found',
            status_code=404
        )

    data = request.get_json()
    user.update(data)
    return create_response(user)

@app.route('/api/v1/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if user_id not in users:
        return create_response(
            error=f'User {user_id} not found',
            status_code=404
        )

    deleted_user = users.pop(user_id)
    return create_response({'deleted': deleted_user})
```

### FastAPI Example (Python)
```python
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title='User API', version='1.0')

class UserCreate(BaseModel):
    name: str
    email: str

class User(UserCreate):
    id: int
    created_at: datetime

users = {}
next_id = 1

@app.get('/api/v1/users', response_model=List[User])
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    user_list = list(users.values())
    start = (page - 1) * limit
    return user_list[start:start+limit]

@app.post('/api/v1/users', response_model=User, status_code=201)
def create_user(user_data: UserCreate):
    global next_id
    user = User(
        id=next_id,
        name=user_data.name,
        email=user_data.email,
        created_at=datetime.utcnow()
    )
    users[next_id] = user
    next_id += 1
    return user

@app.get('/api/v1/users/{user_id}', response_model=User)
def get_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail='User not found')
    return users[user_id]

@app.put('/api/v1/users/{user_id}', response_model=User)
def update_user(user_id: int, user_data: UserCreate):
    if user_id not in users:
        raise HTTPException(status_code=404, detail='User not found')
    user = users[user_id]
    user.name = user_data.name
    user.email = user_data.email
    return user

@app.delete('/api/v1/users/{user_id}')
def delete_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail='User not found')
    return {'deleted': users.pop(user_id)}
```

## FAQ

**Q: Should I use PUT or PATCH for updates?**
A: Use PUT for complete replacement, PATCH for partial updates. In practice, PATCH is more flexible and commonly used.

**Q: How do I handle API versioning?**
A: URL path versioning (`/api/v1/`) is most explicit and recommended. Avoid forcing version upgrades on clients.

**Q: Should sub-resources be nested in URLs?**
A: Yes, for related resources: `GET /api/v1/users/{userId}/posts`. Limit to 2 levels deep.

**Q: How do I handle filtering and search?**
A: Use query parameters: `GET /api/v1/users?name=john&email=john@example.com`

## Resources
- [REST API Best Practices](https://restfulapi.net/)
- [JSON:API Specification](https://jsonapi.org/)
- [HTTP Status Codes](https://httpwg.org/specs/rfc9110.html#status.codes)
- [OpenAPI/Swagger Documentation](https://swagger.io/)
