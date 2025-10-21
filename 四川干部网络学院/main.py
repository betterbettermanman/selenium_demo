# app.py

from flask import Flask, request, jsonify

from models import db, User  # 导入 db 实例和模型

# 创建 Flask 应用
app = Flask(__name__)

# 配置数据库连接
# 格式: mysql+pymysql://用户名:密码@主机:端口/数据库名
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@172.201.1.31:3306/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 禁用事件系统以节省开销

# 配置连接池 (可选但推荐)
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True  # 每次使用前检查连接有效性
}

# 初始化 SQLAlchemy
db.init_app(app)  # 使用 init_app 而不是直接 db = SQLAlchemy(app)，更灵活


# --- CRUD 路由示例 ---
@app.route('/users', methods=['POST'])
def create_user():
    """创建用户"""
    data = request.get_json()
    if not data or 'username' not in data or 'email' not in data:
        return jsonify({'error': '缺少必要字段'}), 400

    # 检查用户名或邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在'}), 400

    # 创建新用户
    new_user = User(username=data['username'], email=data['email'])
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': '用户创建成功', 'user': new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()  # 出错时回滚
        return jsonify({'error': str(e)}), 500


@app.route('/users', methods=['GET'])
def get_users():
    """获取所有用户"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if 'username' in data:
        # 检查新用户名是否已存在（排除自己）
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': '用户名已存在'}), 400
        user.username = data['username']

    if 'email' in data:
        # 检查新邮箱是否已存在（排除自己）
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': '邮箱已存在'}), 400
        user.email = data['email']

    try:
        db.session.commit()
        return jsonify({'message': '用户更新成功', 'user': user.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': '用户删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# 运行应用
if __name__ == '__main__':
    app.run()
