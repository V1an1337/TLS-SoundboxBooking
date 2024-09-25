from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)

# 秘钥（请确保安全存储并不公开）
app.config['SECRET_KEY'] = 'your_secret_key'

# 用户示例（在真实应用中，应该从数据库中获取用户信息）
users = {
    'user1': 'password1',
    'user2': 'password2'
}

@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    username = auth.get('username')
    password = auth.get('password')

    # 验证用户名和密码
    if username in users and users[username] == password:
        # 生成不会过期的JWT
        token = jwt.encode({
            'username': username
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'Token is missing!'}), 401

    try:
        # 解码JWT
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({'message': 'Welcome, ' + decoded['username']})

    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token!'}), 401

if __name__ == '__main__':
    app.run(debug=True)
