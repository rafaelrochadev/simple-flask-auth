from flask import Flask, jsonify, request
from models.user import User
from database import db 
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username and password: 
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Logado com sucesso!"})
    return jsonify({"message": "Login inválido!"}), 404

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso!"})

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username and password:
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Usuario adicionado com sucesso"})
    return jsonify({"message": "Dados inválidos!"}), 401

@app.route('/user/<int:user_id>', methods=['GET'])
def read_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({"message": f"Usuario: {user.username}"})
    return jsonify({"message": "Usuario nao encontrado"}), 404

@app.route('/user/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if user and data.get('password'):
        user.password = data.get('password')
        db.session.commit()
        return jsonify({"message": f"Usuario: {user.username} atualizado!"})
    return jsonify({"message": "Usuario nao encontrado"}), 404

@app.route('/user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user_id == current_user.id:
        return jsonify({"message": "Ação não permitida"}), 403
    elif user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"Usuario: {user.username} deletado!"})
    else:
        return jsonify({"message": "Usuario nao encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True)
