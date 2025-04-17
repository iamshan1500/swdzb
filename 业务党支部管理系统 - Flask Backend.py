from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# 初始化数据
activities = []
applications = []
members = [
    {"id": 1, "username": "admin", "password": "adminpass", "role": "manager"},
    {"id": 2, "username": "member1", "password": "member1pass", "role": "employee"},
    {"id": 3, "username": "member2", "password": "member2pass", "role": "employee"}
]

current_user = None
is_manager = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    global current_user, is_manager
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = next((u for u in members if u['username'] == username and u['password'] == password), None)
    if user:
        current_user = user
        is_manager = user['role'] == 'manager'
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "用户名或密码错误"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    global current_user, is_manager
    current_user = None
    is_manager = False
    return jsonify({"success": True}), 200

@app.route('/add_activity', methods=['POST'])
def add_activity():
    global activities
    if not is_manager:
        return jsonify({"success": False, "message": "权限不足"}), 403
    
    data = request.json
    activity = {
        "id": len(activities) + 1,
        "title": data.get("title"),
        "description": data.get("description"),
        "startDate": data.get("startDate"),
        "endDate": data.get("endDate"),
        "maxParticipants": int(data.get("maxParticipants")),
        "participants": [],
        "assignedTo": []
    }
    activities.append(activity)
    return jsonify({"success": True}), 200

@app.route('/apply_for_activity', methods=['POST'])
def apply_for_activity():
    global applications
    if not current_user:
        return jsonify({"success": False, "message": "请先登录"}), 401
    
    data = request.json
    activity_id = data.get("activityId")
    activity = next((a for a in activities if a["id"] == activity_id), None)
    if not activity or len(activity["participants"]) >= activity["maxParticipants"]:
        return jsonify({"success": False, "message": "无法申请此活动：已达到最大参与人数限制"}), 400
    
    application = next((app for app in applications if app["activityId"] == activity_id), None)
    if application:
        application["participants"].append(current_user["username"])
    else:
        applications.append({"activityId": activity_id, "participants": [current_user["username"]]})
    
    return jsonify({"success": True}), 200

@app.route('/approve_applications', methods=['POST'])
def approve_applications():
    global activities
    if not is_manager:
        return jsonify({"success": False, "message": "权限不足"}), 403
    
    data = request.json
    activity_id = data.get("activityId")
    selected_participants = data.get("selectedParticipants")
    activity = next((a for a in activities if a["id"] == activity_id), None)
    if activity:
        activity["assignedTo"] = selected_participants
    return jsonify({"success": True}), 200

@app.route('/add_member', methods=['POST'])
def add_member():
    global members
    if not is_manager:
        return jsonify({"success": False, "message": "权限不足"}), 403
    
    data = request.json
    member = {
        "id": len(members) + 1,
        "username": data.get("username"),
        "password": data.get("password"),
        "role": data.get("role")
    }
    members.append(member)
    return jsonify({"success": True}), 200

@app.route('/edit_member', methods=['POST'])
def edit_member():
    global members
    if not is_manager:
        return jsonify({"success": False, "message": "权限不足"}), 403
    
    data = request.json
    member_id = data.get("memberId")
    member = next((m for m in members if m["id"] == member_id), None)
    if member:
        member["username"] = data.get("username")
        member["password"] = data.get("password")
        member["role"] = data.get("role")
    return jsonify({"success": True}), 200

@app.route('/delete_member', methods=['POST'])
def delete_member():
    global members
    if not is_manager:
        return jsonify({"success": False, "message": "权限不足"}), 403
    
    data = request.json
    member_id = data.get("memberId")
    global members
    members = [m for m in members if m["id"] != member_id]
    return jsonify({"success": True}), 200

if __name__ == '__main__':
    app.run(debug=True)



