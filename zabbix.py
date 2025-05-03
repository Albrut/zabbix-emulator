from flask import Flask, request, jsonify
from flasgger import Swagger
import uuid

app = Flask(__name__)
swagger = Swagger(app)

# Hardcoded users with roles, IDs and personal data
users = [
    {
        
        "login": "admin",
        "password": "adminpass",
        "role": "incident_admin",
        "name": "Иван",
        "surname": "Петров",
        "is_working": True
    },
    {
        
        "login": "user",
        "password": "userpass",
        "role": "user",
        "name": "Ольга",
        "surname": "Сидорова",
        "is_working": False
    }
]

# Hardcoded incidents
incidents = [
    {
        "number": 1,
        "resources": "Сервисы Тундук",
        "datetime": "10/03/2025 09:30",
        "description": "Проблемы с доступом к серверу",
        "priority": "Высокий",
        "responsible": "admin",
        "status": "В процессе",
        "closure_datetime": None,
        "solution": None,
        "notes": ""
    },
    {
        "number": 2,
        "resources": "АБС",
        "datetime": "11/03/2025 10:00",
        "description": "Ошибка при обработке транзакции",
        "priority": "Средний",
        "responsible": "user",
        "status": "Закрыт",
        "closure_datetime": "11/03/2025 13:00",
        "solution": "Перезагружен сервис",
        "notes": "Проблема решена"
    }
]

# Dictionary to store active authentication tokens
active_tokens = {}

def generate_token():
    return str(uuid.uuid4())

@app.route('/api', methods=['POST'])
def api():
    """
    JSON-RPC API endpoint
    ---
    tags:
      - JSON-RPC
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            jsonrpc:
              type: string
              example: "2.0"
            method:
              type: string
              example: "user.login"
            params:
              type: object
              example: {"user": "admin", "password": "adminpass"}
            auth:
              type: string
              example: null
            id:
              type: integer
              example: 1
    responses:
      200:
        description: JSON-RPC standard response
        schema:
          type: object
          properties:
            jsonrpc:
              type: string
              example: "2.0"
            result:
              type: object
              description: Depends on the method
            id:
              type: integer
              example: 1
    """
    data = request.json
    if not data or 'method' not in data:
        return jsonify({"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None})

    method = data['method']
    params = data.get('params', {})
    auth = data.get('auth')
    id_ = data.get('id')

    # ---- user.login ----
    if method == 'user.login':
        user_login = params.get('user')
        password = params.get('password')
        for u in users:
            if u['login'] == user_login and u['password'] == password:
                token = generate_token()
                active_tokens[token] = u
                return jsonify({"jsonrpc": "2.0", "result": token, "id": id_})
        return jsonify({"jsonrpc": "2.0", "error": {"code": -32001, "message": "Invalid credentials"}, "id": id_})

    # ---- problem.get ----
    elif method == 'problem.get':
        if auth not in active_tokens:
            return jsonify({"jsonrpc": "2.0", "error": {"code": -32002, "message": "Unauthorized"}, "id": id_})
        active_incidents = [inc for inc in incidents if inc['status'] == "В процессе"]
        return jsonify({"jsonrpc": "2.0", "result": active_incidents, "id": id_})

    # ---- user.get ----
    elif method == 'user.get':
        if auth not in active_tokens:
            return jsonify({"jsonrpc": "2.0", "error": {"code": -32002, "message": "Unauthorized"}, "id": id_})
        u = active_tokens[auth]
        user_info = {
            
            "alias": u['login'],
            "role": u['role'],
            "name": u['name'],
            "surname": u['surname'],
            "is_working": u['is_working']
        }
        return jsonify({"jsonrpc": "2.0", "result": [user_info], "id": id_})

    # ---- unknown method ----
    else:
        return jsonify({"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": id_})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
