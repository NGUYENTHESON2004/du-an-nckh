import sqlite3
import datetime
import os
import sys
import math
import json
import io
import csv
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, make_response
from functools import wraps
from PIL import Image

# --- CẤU HÌNH V70 - FINAL PERFECT ---
app = Flask(__name__)
app.secret_key = 'LMS_V70_FINAL'
DB_NAME = "data_training.db"
DICTIONARY_FILE = "dictionary.json"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_PHOTO_FOLDER = os.path.join(BASE_DIR, "static", "user_photos")
if not os.path.exists(ROOT_PHOTO_FOLDER): os.makedirs(ROOT_PHOTO_FOLDER)

LIVE_STATUS = {}
ITEMS_PER_PAGE = 8

def get_vn_time(): return datetime.datetime.utcnow() + datetime.timedelta(hours=7)
def get_vn_str(): return get_vn_time().strftime('%Y-%m-%d %H:%M:%S')

# --- HÀM DỊCH TỰ ĐỘNG ---
def get_translation_map():
    if os.path.exists(DICTIONARY_FILE):
        try:
            with open(DICTIONARY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def translate_log_detail(raw_text):
    vn_map = get_translation_map()
    if ": " in raw_text:
        parts = raw_text.split(": ", 1)
        prefix = parts[0]; code = parts[1].strip()
        if code in vn_map: return f"{prefix}: {vn_map[code]}"
    if raw_text in vn_map: return vn_map[raw_text]
    return raw_text

# --- DATABASE & SETTINGS ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, fullname TEXT, status TEXT DEFAULT 'active', notes TEXT DEFAULT '', last_login TIMESTAMP, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    try: c.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP") 
    except: pass
    c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender_id INTEGER, content TEXT, reply TEXT, is_read INTEGER DEFAULT 0, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, action_type TEXT, details TEXT, result TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_photos (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, filename TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    try: c.execute("INSERT INTO users (username, password, fullname, status) VALUES (?, ?, ?, ?)", ('admin', 'admin123', 'Administrator', 'active'))
    except: pass
    defaults = {'system_name': 'LMS PRO V70', 'pass_mark': '5', 'photo_interval': '10', 'max_duration': '60', 'maintenance_mode': '0', 'announcement': ''}
    for k, v in defaults.items():
        try: c.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (k, v))
        except: pass
    conn.commit(); conn.close()

def get_setting(key):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,)); row = c.fetchone(); conn.close()
    return row[0] if row else ""

def get_all_settings():
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("SELECT key, value FROM settings"); data = dict(c.fetchall()); conn.close()
    return data

# --- LOGIN PAGE ---
LOGIN_LAYOUT = """
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đăng Nhập V70</title>
    <link href="{{ url_for('static', filename='css/bootstrap.min.css') }}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/all.min.css') }}" rel="stylesheet">
    <style>
        body { height: 100vh; overflow: hidden; font-family: 'Segoe UI', sans-serif; background: #fff; }
        .split-screen { display: flex; height: 100%; }
        .left-pane { flex: 1; background: #4f46e5; display: flex; align-items: center; justify-content: center; color: white; position: relative; overflow: hidden; }
        .left-pane::before { content: ''; position: absolute; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%); top: -50%; left: -50%; animation: spin 30s linear infinite; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
        .right-pane { width: 500px; display: flex; align-items: center; justify-content: center; padding: 40px; background: #f8fafc; }
        .login-box { width: 100%; max-width: 380px; }
        .form-control { padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; background: #fff; margin-bottom: 15px; }
        .btn-login { width: 100%; padding: 12px; background: #4f46e5; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s; }
        .btn-login:hover { background: #4338ca; transform: translateY(-1px); }
        .brand-text { font-size: 40px; font-weight: 800; letter-spacing: -1px; z-index: 2; text-shadow: 0 10px 20px rgba(0,0,0,0.2); }
        @media (max-width: 768px) { .left-pane { display: none; } .right-pane { width: 100%; } }
    </style>
</head>
<body>
    <div class="split-screen">
        <div class="left-pane"><div class="text-center"><div class="brand-text"><i class="fas fa-layer-group"></i> LMS V70</div><div class="mt-2 opacity-75">Hệ thống Đào tạo & Giám sát</div></div></div>
        <div class="right-pane">
            <div class="login-box">
                <h3 class="fw-bold text-dark mb-1">Đăng Nhập</h3>
                <p class="text-muted small mb-4">Vui lòng nhập thông tin tài khoản.</p>
                {% if maintenance == '1' %}<div class="alert alert-warning small fw-bold"><i class="fas fa-tools"></i> HỆ THỐNG BẢO TRÌ</div>{% endif %}
                <form action="/do_login" method="post">
                    <label class="small fw-bold text-secondary mb-1">Tài khoản</label><input type="text" name="u" class="form-control" required>
                    <label class="small fw-bold text-secondary mb-1">Mật khẩu</label><input type="password" name="p" class="form-control" required>
                    <button class="btn-login mt-2">TRUY CẬP</button>
                </form>
                <div class="mt-4 text-center border-top pt-3"><a href="/register" class="text-decoration-none small fw-bold text-primary">Đăng ký tài khoản mới</a></div>
            </div>
        </div>
    </div>
</body>
</html>
"""

REGISTER_LAYOUT = """
<!doctype html>
<html lang="vi"><head><meta charset="UTF-8"><title>Đăng Ký</title><link href="{{ url_for('static', filename='css/bootstrap.min.css') }}" rel="stylesheet"><style>body{height:100vh;display:flex;align-items:center;justify-content:center;background:#f8fafc;font-family:sans-serif}.card{border:none;box-shadow:0 10px 30px rgba(0,0,0,0.05);border-radius:12px;width:100%;max-width:400px;padding:30px}</style></head><body><div class="card"><h4 class="fw-bold text-center mb-4" style="color:#4f46e5">TẠO TÀI KHOẢN</h4><form action="/do_register" method="post"><input name="u" class="form-control mb-2" placeholder="Tên đăng nhập" required><input type="password" name="p" class="form-control mb-2" placeholder="Mật khẩu" required><input name="n" class="form-control mb-4" placeholder="Họ và tên đầy đủ" required><button class="btn btn-primary w-100 fw-bold" style="background:#4f46e5; border:none; padding:10px">GỬI YÊU CẦU</button></form><a href="/login" class="d-block text-center mt-3 small text-muted text-decoration-none">Quay lại đăng nhập</a></div></body></html>
"""

# --- ADMIN LAYOUT (ĐÃ SỬA LẠI NÚT DUYỆT) ---
ADMIN_LAYOUT = """
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard V70</title>
    <link href="{{ url_for('static', filename='css/bootstrap.min.css') }}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/all.min.css') }}" rel="stylesheet">
    <script src="{{ url_for('static', filename='js/bootstrap.bundle.min.js') }}"></script>
    <script src="{{ url_for('static', filename='js/chart.js') }}"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f1f5f9; height: 100vh; overflow: hidden; display: flex; }
        .sidebar { width: 250px; background: #0f172a; color: #94a3b8; display: flex; flex-direction: column; flex-shrink: 0; }
        .brand { height: 60px; display: flex; align-items: center; padding: 0 20px; font-weight: 800; color: white; font-size: 18px; border-bottom: 1px solid #1e293b; }
        .menu-label { padding: 15px 20px 5px; font-size: 10px; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; color: #475569; }
        .user-item { padding: 8px 20px; cursor: pointer; display: flex; align-items: center; justify-content: space-between; transition: 0.2s; border-left: 3px solid transparent; font-size: 13px; }
        .user-item:hover { background: #1e293b; color: white; }
        .user-item.active { background: #1e293b; color: white; border-left-color: #4f46e5; }
        .live-dot { width: 7px; height: 7px; border-radius: 50%; background: #475569; }
        .live-dot.online { background: #10b981; box-shadow: 0 0 8px #10b981; }
        .main { flex: 1; display: flex; flex-direction: column; min-width: 0; background: #f8fafc; }
        .top-bar { height: 60px; background: white; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: space-between; padding: 0 25px; }
        .content-area { flex: 1; overflow-y: auto; padding: 20px; }
        .dashboard-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 15px; height: calc(100% - 80px); }
        .stat-card { background: white; border-radius: 10px; padding: 12px; border: 1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.02); display: flex; align-items: center; gap: 12px; }
        .stat-icon { width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
        .log-card { background: white; border: 1px solid #e2e8f0; border-radius: 6px; margin-bottom: 6px; overflow: hidden; box-shadow: 0 1px 2px rgba(0,0,0,0.01); }
        .log-header { padding: 8px 12px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; background: white; user-select: none; }
        .log-header:hover { background: #f8fafc; }
        .log-body { background: #f9fafb; border-top: 1px solid #e2e8f0; padding: 5px 12px; }
        .step-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #e2e8f0; font-size: 12px; }
        .res-ok { background: #d1fae5; color: #047857; border: 1px solid #a7f3d0; padding: 2px 6px; border-radius: 20px; font-size: 10px; font-weight: 700;}
        .res-fail { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; padding: 2px 6px; border-radius: 20px; font-size: 10px; font-weight: 700;}
        .photo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; }
        .photo-item { aspect-ratio: 4/3; background: #000; border-radius: 4px; overflow: hidden; position: relative; cursor: zoom-in; }
        .photo-item img { width: 100%; height: 100%; object-fit: cover; opacity: 0.9; transition: 0.3s; }
        .photo-item:hover img { opacity: 1; transform: scale(1.1); }
        .photo-tag { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.6); color: white; font-size: 9px; text-align: center; padding: 1px; }
        .lightbox { display: none; position: fixed; z-index: 9999; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); align-items:center; justify-content:center; }
        .lightbox img { max-width:90%; max-height:90%; border-radius:5px; }
        .collapse:not(.show) { display: none; } .collapse.show { display: block; }
        @media (max-width: 768px) { .dashboard-grid { grid-template-columns: 1fr; } .sidebar { display:none; } }
    </style>
</head>
<body>
<div id="lightbox" class="lightbox" onclick="this.style.display='none'"><img id="lightbox-img" src=""></div>
<div class="sidebar">
    <div class="brand"><i class="fas fa-cube me-2 text-primary"></i> LMS V70</div>
    <div class="menu-label">QUẢN LÝ</div>
    <div class="user-item {{ 'active' if not active_user and request.path == '/admin' else '' }}" onclick="window.location='/admin'"><span><i class="fas fa-th-large me-2"></i> Tổng quan</span></div>
    <div class="user-item {{ 'active' if 'pending' in request.path else '' }}" onclick="window.location='/admin/pending'"><span><i class="fas fa-clock me-2"></i> Chờ duyệt</span>{% if pending_count > 0 %}<span class="badge bg-danger rounded-pill">{{ pending_count }}</span>{% endif %}</div>
    <div class="menu-label">HỌC VIÊN</div>
    <div style="flex:1; overflow-y:auto; padding-right: 2px;">{% for u in users %}<div class="user-item {{ 'active' if active_user and active_user[0] == u[0] else '' }}" onclick="window.location='/admin/{{ 'pending/' if mode == 'pending' else '' }}{{u[0]}}'"><div class="d-flex align-items-center gap-2"><div class="live-dot" id="dot-{{u[0]}}"></div><div class="text-truncate" style="max-width:130px">{{ u[3] }}</div></div></div>{% endfor %}</div>
    <div class="p-2 border-top border-secondary bg-dark"><button class="btn btn-success btn-sm w-100 mb-2 fw-bold" style="font-size: 12px;" data-bs-toggle="modal" data-bs-target="#addUserModal"><i class="fas fa-user-plus me-1"></i> THÊM</button><div class="d-flex gap-2"><button class="btn btn-primary btn-sm flex-grow-1" data-bs-toggle="modal" data-bs-target="#settingsModal"><i class="fas fa-cog"></i></button><a href="/logout" class="btn btn-outline-danger btn-sm"><i class="fas fa-power-off"></i></a></div></div>
</div>
<div class="main">
    {% if active_user %}
        <div class="top-bar">
            <div><h5 class="m-0 fw-bold text-dark" style="font-size: 16px;">{{ active_user[3] }}</h5><div class="small text-muted" style="font-size: 11px;">ID: {{ active_user[0] }}</div></div>
            <div class="d-flex gap-2">
                {% if mode == 'pending' %}
                    <a href="/admin/approve/{{ active_user[0] }}" class="btn btn-success btn-sm fw-bold py-1" style="font-size: 12px;"><i class="fas fa-check me-1"></i> DUYỆT NGAY</a>
                    <a href="/user/delete/{{ active_user[0] }}" class="btn btn-outline-danger btn-sm fw-bold py-1" style="font-size: 12px;" onclick="return confirm('Từ chối?')"><i class="fas fa-times"></i> TỪ CHỐI</a>
                {% else %}
                    <button class="btn btn-white border btn-sm py-1" style="font-size: 12px;" onclick="openEditUser({{active_user[0]}}, '{{active_user[1]}}', '{{active_user[2]}}', '{{active_user[3]}}', '{{active_user[5]}}')"><i class="fas fa-pen"></i> Sửa</button>
                    <div class="dropdown"><button class="btn btn-primary btn-sm fw-bold dropdown-toggle py-1" style="font-size: 12px;" data-bs-toggle="dropdown">Tác vụ</button><ul class="dropdown-menu dropdown-menu-end shadow border-0 small"><li><a class="dropdown-item" href="/user/export/{{ active_user[0] }}"><i class="fas fa-file-excel me-2 text-success"></i> Xuất Excel</a></li><li><hr class="dropdown-divider"></li><li><a class="dropdown-item text-danger" href="/user/reset_data/{{ active_user[0] }}" onclick="return confirm('Xóa sạch?')"><i class="fas fa-trash me-2"></i> Reset</a></li><li><a class="dropdown-item text-danger" href="/user/ban/{{ active_user[0] }}" onclick="return confirm('Khóa?')"><i class="fas fa-ban me-2"></i> Khóa</a></li></ul></div>
                {% endif %}
            </div>
        </div>
        <div class="content-area">
            <div class="row g-2 mb-3">
                <div class="col-md-3"><div class="stat-card"><div class="stat-icon bg-primary bg-opacity-10 text-primary"><i class="fas fa-check-circle"></i></div><div><div class="h4 fw-bold mb-0">{{ summary.total_sessions }}</div><div class="small text-muted fw-bold">BÀI TẬP</div></div></div></div>
                <div class="col-md-3"><div class="stat-card"><div class="stat-icon bg-danger bg-opacity-10 text-danger"><i class="fas fa-exclamation-triangle"></i></div><div><div class="h4 fw-bold mb-0">{{ summary.total_errors }}</div><div class="small text-muted fw-bold">LỖI</div></div></div></div>
                <div class="col-md-3"><div class="stat-card"><div class="stat-icon bg-info bg-opacity-10 text-info"><i class="fas fa-clock"></i></div><div><div class="h4 fw-bold mb-0" style="font-size:16px">{{ summary.total_time_str }}</div><div class="small text-muted fw-bold">ONLINE</div></div></div></div>
                <div class="col-md-3"><div class="stat-card"><div class="stat-icon bg-success bg-opacity-10 text-success"><i class="fas fa-star"></i></div><div><div class="h4 fw-bold mb-0" style="color:{{summary.grade_color}}">{{ summary.grade }}</div><div class="small text-muted fw-bold">XẾP LOẠI</div></div></div></div>
            </div>
            <div class="dashboard-grid">
                <div style="overflow-y: auto; padding-right: 5px;">
                    <div class="card border-0 shadow-sm mb-3"><div class="card-header bg-white py-2"><i class="fas fa-chart-line me-2 text-primary"></i> TIẾN ĐỘ</div><div class="card-body p-2" style="height: 160px;"><canvas id="progressChart"></canvas></div></div>
                    <h6 class="fw-bold text-muted mb-2 small"><i class="fas fa-stream me-2"></i> NHẬT KÝ CHI TIẾT</h6>
                    {% if sessions %}{% for sess in sessions %}
                        <div class="log-card">
                            <div class="log-header" onclick="toggleLog('c{{ loop.index }}')">
                                <div class="d-flex align-items-center gap-2"><div class="bg-light rounded p-1 text-center border font-monospace fw-bold" style="width:35px; font-size: 14px;">{{ sess.grade }}</div><div><div class="fw-bold text-dark" style="font-size: 13px;">{{ sess.lesson_name }}</div><div class="text-muted" style="font-size: 10px;"><i class="far fa-clock"></i> {{ sess.start_time }}</div></div></div>
                                <div class="d-flex align-items-center gap-2">{% if sess.is_completed %}<span class="badge bg-success rounded-pill" style="font-size: 9px;">XONG</span>{% else %}<span class="badge bg-warning text-dark rounded-pill" style="font-size: 9px;">CHƯA</span>{% endif %}<span class="badge {{ 'bg-success' if sess.error_count==0 else 'bg-danger' }} rounded-pill" style="font-size: 9px;">{{ sess.error_count }} Lỗi</span></div>
                            </div>
                            <div id="c{{ loop.index }}" class="collapse"><div class="log-body">{% for step in sess.steps %}<div class="step-row"><div class="d-flex align-items-start"><span class="step-time">{{ step.time_only }}</span><span class="step-desc">{{ step.details }}</span></div><span class="step-res {{ 'res-ok' if step.result=='ĐÚNG' else 'res-fail' }}">{{ step.result }}</span></div>{% endfor %}</div></div>
                        </div>
                    {% endfor %}{% else %}<div class="text-center text-muted p-4 bg-white border rounded small">Chưa có dữ liệu.</div>{% endif %}
                </div>
                <div style="display: flex; flex-direction: column; height: 100%; overflow: hidden;">
                    <div class="card border-0 shadow-sm mb-2" style="flex-shrink: 0;"><div class="card-header bg-white py-2"><i class="fas fa-envelope me-2 text-primary"></i> TIN NHẮN</div><div class="card-body p-0">{% if messages %}<div class="list-group list-group-flush" style="max-height:150px; overflow-y:auto">{% for m in messages %}<div class="list-group-item list-group-item-action p-2" onclick="openReply({{m[0]}}, '{{m[2]}}')"><div class="d-flex w-100 justify-content-between" style="font-size: 10px;"><small class="text-muted">{{ m[5] }}</small>{% if not m[3] %}<i class="fas fa-circle text-danger" style="font-size:6px"></i>{% endif %}</div><p class="mb-0 small text-truncate-2" style="font-size: 12px;">{{ m[2] }}</p></div>{% endfor %}</div>{% else %}<div class="p-2 text-center text-muted small">Trống.</div>{% endif %}</div></div>
                    <div class="card border-0 shadow-sm" style="flex: 1; display: flex; flex-direction: column; overflow: hidden;"><div class="card-header bg-white py-2 d-flex justify-content-between align-items-center"><span><i class="fas fa-camera me-2 text-primary"></i> ẢNH GIÁM SÁT</span><span class="badge bg-secondary rounded-pill font-monospace" style="font-size: 10px;">Tổng: {{ photos|length }}</span></div><div class="card-body p-1" style="flex: 1; overflow-y: auto;"><div class="photo-grid">{% for p in photos %}<div class="photo-item" onclick="openLightbox('/static/user_photos/{{ active_user[0] }}/{{ p[2] }}')"><img src="/static/user_photos/{{ active_user[0] }}/{{ p[2] }}"><div class="photo-tag">{{ p[3].split(' ')[1] }}</div></div>{% endfor %}</div></div></div>
                </div>
            </div>
        </div>
    {% else %}
        <div class="d-flex flex-column h-100 align-items-center justify-content-center text-center p-5"><h4 class="fw-bold text-dark">DASHBOARD</h4><p class="text-muted small">Chọn học viên để xem chi tiết.</p></div>
    {% endif %}
</div>
<div class="modal fade" id="addUserModal" tabindex="-1"><div class="modal-dialog modal-sm"><form class="modal-content" action="/user/add" method="post"><div class="modal-header fw-bold py-2 small">THÊM HỌC VIÊN MỚI</div><div class="modal-body small"><div class="mb-2"><label class="fw-bold">Tên đăng nhập</label><input name="username" class="form-control form-control-sm" required></div><div class="mb-2"><label class="fw-bold">Mật khẩu</label><input name="password" class="form-control form-control-sm" required></div><div class="mb-2"><label class="fw-bold">Họ và tên</label><input name="fullname" class="form-control form-control-sm" required></div></div><div class="modal-footer py-1"><button class="btn btn-primary btn-sm w-100 fw-bold">LƯU TÀI KHOẢN</button></div></form></div></div>
<div class="modal fade" id="replyModal" tabindex="-1"><div class="modal-dialog"><form class="modal-content" action="/admin/reply_msg" method="post"><div class="modal-header fw-bold py-2 small">TRẢ LỜI TIN NHẮN</div><div class="modal-body small"><input type="hidden" name="msg_id" id="reply_msg_id"><div class="p-2 bg-light border rounded mb-2 fst-italic text-muted" id="reply_msg_content" style="font-size: 11px;"></div><textarea name="reply_content" class="form-control form-control-sm" rows="3" placeholder="Nhập câu trả lời..." required></textarea></div><div class="modal-footer py-1"><button class="btn btn-primary btn-sm w-100">Gửi phản hồi</button></div></form></div></div>
<div class="modal fade" id="editUserModal" tabindex="-1"><div class="modal-dialog modal-sm"><form class="modal-content" action="/user/edit" method="post"><div class="modal-header fw-bold py-2 small">SỬA THÔNG TIN</div><div class="modal-body small"><input type="hidden" name="uid" id="edit_uid"><div class="mb-2"><label class="fw-bold">Username</label><input name="username" id="edit_username" class="form-control form-control-sm" required></div><div class="mb-2"><label class="fw-bold">Password</label><input name="password" id="edit_password" class="form-control form-control-sm" required></div><div class="mb-2"><label class="fw-bold">Fullname</label><input name="fullname" id="edit_fullname" class="form-control form-control-sm" required></div><div class="mb-2"><label class="fw-bold text-warning">Ghi chú (Admin)</label><textarea name="notes" id="edit_notes" class="form-control form-control-sm"></textarea></div></div><div class="modal-footer py-1"><button class="btn btn-primary btn-sm w-100">Lưu thay đổi</button></div></form></div></div>
<div class="modal fade" id="settingsModal" tabindex="-1"><div class="modal-dialog modal-sm"><div class="modal-content"><div class="modal-header fw-bold py-2 small">CÀI ĐẶT HỆ THỐNG</div><div class="modal-body small"><form action="/admin/save_settings" method="post"><div class="mb-2"><label class="fw-bold">Tên hệ thống</label><input name="system_name" class="form-control form-control-sm" value="{{ settings.system_name }}"></div><div class="row g-2"><div class="col-6 mb-2"><label class="fw-bold">Điểm đạt</label><input type="number" name="pass_mark" class="form-control form-control-sm" value="{{ settings.pass_mark }}"></div><div class="col-6 mb-2"><label class="fw-bold">Thời gian (p)</label><input type="number" name="max_duration" class="form-control form-control-sm" value="{{ settings.max_duration }}"></div></div><div class="mb-2"><label class="fw-bold">Chụp ảnh (s)</label><input type="number" name="photo_interval" class="form-control form-control-sm" value="{{ settings.photo_interval }}"></div><div class="mb-2"><label class="fw-bold">Thông báo</label><input name="announcement" class="form-control form-control-sm" value="{{ settings.announcement }}"></div><div class="form-check form-switch bg-light p-2 rounded"><input class="form-check-input ms-0 me-2" type="checkbox" name="maintenance_mode" value="1" {{ 'checked' if settings.maintenance_mode == '1' else '' }}><label class="form-check-label text-danger fw-bold small">CHẾ ĐỘ BẢO TRÌ</label></div><button class="btn btn-primary btn-sm w-100 mt-3">LƯU CÀI ĐẶT</button></form></div></div></div></div>
<script>
    function toggleLog(id) { var el = document.getElementById(id); if(el.classList.contains('show')) el.classList.remove('show'); else el.classList.add('show'); }
    function openEditUser(id, u, p, n, note) { document.getElementById('edit_uid').value=id; document.getElementById('edit_username').value=u; document.getElementById('edit_password').value=p; document.getElementById('edit_fullname').value=n; document.getElementById('edit_notes').value=note?note:''; new bootstrap.Modal(document.getElementById('editUserModal')).show(); }
    function openReply(id, content) { document.getElementById('reply_msg_id').value=id; document.getElementById('reply_msg_content').innerText=content; new bootstrap.Modal(document.getElementById('replyModal')).show(); }
    function openLightbox(src) { document.getElementById('lightbox-img').src=src; document.getElementById('lightbox').style.display='flex'; }
    setInterval(() => { fetch('/api/monitor').then(r=>r.json()).then(data => { data.forEach(u => { const el = document.getElementById('dot-' + u.uid); if(el) el.className = u.status === 'online' ? 'live-dot online' : 'live-dot'; }); }); }, 3000);
    {% if chart_labels %}
    const ctx = document.getElementById('progressChart');
    if (ctx) { new Chart(ctx, { type: 'line', data: { labels: {{ chart_labels | tojson }}, datasets: [{ label: 'Số lỗi', data: {{ chart_data | tojson }}, borderColor: '#4f46e5', backgroundColor: 'rgba(79, 70, 229, 0.1)', borderWidth: 2, pointRadius: 3, tension: 0.3, fill: true }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { display: false }, ticks: { font: { size: 10 } } }, x: { ticks: { font: { size: 10 }, maxRotation: 0, autoSkip: true, maxTicksLimit: 5 } } } } }); }
    {% endif %}
</script>
</body>
</html>
"""

# --- STUDENT LAYOUT (ĐÃ TỐI ƯU UX) ---
STUDENT_LAYOUT = """
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Góc Học Tập</title>
    <link href="{{ url_for('static', filename='css/bootstrap.min.css') }}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/all.min.css') }}" rel="stylesheet">
    <script src="{{ url_for('static', filename='js/bootstrap.bundle.min.js') }}"></script>
    <style>
        body { background: #f8fafc; font-family: sans-serif; font-size: 14px; padding-bottom: 50px; }
        .stat-card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px; text-align: center; height: 100%; transition: 0.2s; }
        .stat-val { font-size: 24px; font-weight: 800; color: #1e293b; line-height: 1; margin-top: 5px; }
        .stat-label { font-size: 10px; text-transform: uppercase; color: #64748b; font-weight: 600; letter-spacing: 0.5px; }
        .sess-card { background: white; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 12px; overflow: hidden; transition: 0.2s; }
        .sess-card:hover { transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .sess-header { padding: 15px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; background: white; }
        .sess-header:hover { background: #f8fafc; }
        .step-list { background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 10px 15px; }
        .step-item { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #eee; font-size: 13px; }
        .step-item:last-child { border-bottom: none; }
        .res-badge { font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 20px; min-width: 50px; text-align: center; }
        .res-ok { background: #d1fae5; color: #047857; }
        .res-fail { background: #fee2e2; color: #b91c1c; }
        .status-tag { font-size: 10px; font-weight: bold; padding: 4px 8px; border-radius: 6px; text-transform: uppercase; }
        .status-done { background: #ecfccb; color: #3f6212; }
        .status-pending { background: #fef9c3; color: #854d0e; }
        .collapse:not(.show) { display: none; } .collapse.show { display: block; }
    </style>
</head>
<body>
    {% if settings.announcement %}<div class="bg-primary text-white text-center p-2 fw-bold small"><i class="fas fa-bullhorn me-2"></i> {{ settings.announcement }}</div>{% endif %}
    <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom py-2 shadow-sm sticky-top">
        <div class="container">
            <a class="navbar-brand fw-bold text-primary fs-6" href="#"><i class="fas fa-cube me-2"></i>{{ settings.system_name }}</a>
            <div class="d-flex align-items-center gap-3">
                <div class="text-end lh-1 d-none d-sm-block"><div class="fw-bold text-dark">{{ user[3] }}</div><div class="small text-muted" style="font-size:11px">Học viên</div></div>
                <div class="bg-light rounded-circle d-flex align-items-center justify-content-center fw-bold text-primary border" style="width:35px; height:35px">{{ user[3][0] }}</div>
                <button class="btn btn-outline-primary btn-sm rounded-pill px-3" data-bs-toggle="modal" data-bs-target="#msgModal"><i class="fas fa-comment-dots"></i></button>
                <a href="/logout" class="btn btn-danger btn-sm rounded-pill px-3 fw-bold">Thoát</a>
            </div>
        </div>
    </nav>
    <div class="container py-4">
        <div class="row g-3 mb-4">
            <div class="col-6 col-md-3"><div class="stat-card border-bottom-4 border-primary"><div class="stat-label">BÀI TẬP</div><div class="stat-val text-primary">{{ summary.total_sessions }}</div></div></div>
            <div class="col-6 col-md-3"><div class="stat-card border-bottom-4 border-danger"><div class="stat-label">LỖI</div><div class="stat-val text-danger">{{ summary.total_errors }}</div></div></div>
            <div class="col-6 col-md-3"><div class="stat-card border-bottom-4 border-info"><div class="stat-label">THỜI GIAN</div><div class="stat-val text-info" style="font-size:18px">{{ summary.total_time_str }}</div></div></div>
            <div class="col-6 col-md-3"><div class="stat-card border-bottom-4 border-success"><div class="stat-label">XẾP LOẠI</div><div class="stat-val" style="color:{{summary.grade_color}}">{{ summary.grade }}</div></div></div>
        </div>
        <h6 class="fw-bold text-muted mb-3"><i class="fas fa-history me-2"></i> LỊCH SỬ THỰC HÀNH</h6>
        {% if sessions %}{% for sess in sessions %}
            <div class="sess-card">
                <div class="sess-header" onclick="toggleStudentLog('s{{ loop.index }}')">
                    <div class="d-flex align-items-center gap-3">
                        <div class="bg-light rounded p-2 text-center border fw-bold fs-5 text-secondary" style="width:50px">{{ sess.grade }}</div>
                        <div><div class="fw-bold text-dark fs-6">{{ sess.lesson_name }}</div><div class="small text-muted"><i class="far fa-clock me-1"></i> {{ sess.start_time }} &bull; {{ sess.duration_str }}</div></div>
                    </div>
                    <div class="text-end">
                        {% if sess.is_completed %}<span class="status-tag status-done me-2"><i class="fas fa-check"></i> ĐÃ XONG</span>{% else %}<span class="status-tag status-pending me-2"><i class="fas fa-spinner fa-spin"></i> CHƯA XONG</span>{% endif %}
                        <span class="badge {{ 'bg-success' if sess.error_count==0 else 'bg-danger' }} rounded-pill">{{ sess.error_count }} Lỗi</span>
                        <i class="fas fa-chevron-down text-muted ms-2 transition-icon" id="icon-s{{ loop.index }}"></i>
                    </div>
                </div>
                <div id="s{{ loop.index }}" class="collapse step-list">
                    {% for step in sess.steps %}
                    <div class="step-item"><div><span class="text-muted font-monospace me-2 bg-white border px-1 rounded">{{ step.time_only }}</span><span class="fw-500 text-dark">{{ step.details }}</span></div><span class="res-badge {{ 'res-ok' if step.result=='ĐÚNG' else 'res-fail' }}">{{ step.result }}</span></div>
                    {% endfor %}
                </div>
            </div>
        {% endfor %}{% else %}<div class="p-5 text-center text-muted bg-white border rounded">Chưa có dữ liệu bài tập nào.</div>{% endif %}
    </div>
    <div class="modal fade" id="msgModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content"><div class="modal-header fw-bold">HỘP THƯ TRAO ĐỔI</div><div class="modal-body bg-light" style="max-height:400px; overflow-y:auto">{% if messages %}{% for m in messages %}<div class="bg-white p-3 mb-2 rounded border shadow-sm"><div class="small fw-bold text-dark">Bạn:</div><div class="text-muted mb-2">{{ m[2] }}</div>{% if m[3] %}<div class="bg-info bg-opacity-10 p-2 rounded text-primary small"><strong>GV trả lời:</strong> {{ m[3] }}</div>{% else %}<div class="small text-secondary fst-italic text-end">--- Đang đợi ---</div>{% endif %}</div>{% endfor %}{% else %}<div class="text-center text-muted p-3">Chưa có tin nhắn nào.</div>{% endif %}</div><form action="/student/send_msg" method="post" class="modal-footer bg-white"><input name="content" class="form-control" placeholder="Nhập câu hỏi..." required><button class="btn btn-primary rounded-pill px-4 fw-bold">GỬI</button></form></div></div></div>
    <script>
        function toggleStudentLog(id) {
            var el = document.getElementById(id); var icon = document.getElementById('icon-' + id);
            if (el.classList.contains('show')) { el.classList.remove('show'); if(icon) icon.style.transform = 'rotate(0deg)'; }
            else { el.classList.add('show'); if(icon) icon.style.transform = 'rotate(180deg)'; }
        }
    </script>
</body>
</html>
"""

# --- LOGIC & API ---
# ... (Phần logic Login, Admin, API giữ nguyên như cũ, không thay đổi để đảm bảo tính ổn định) ...
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session: return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') != 'admin': return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'user_role' in session: return redirect('/admin') if session['user_role'] == 'admin' else redirect('/student')
    return redirect('/login')

@app.route('/login')
def login_page(): return render_template_string(LOGIN_LAYOUT, maintenance=get_setting('maintenance_mode'))

@app.route('/register')
def register_page(): return render_template_string(REGISTER_LAYOUT)

@app.route('/do_register', methods=['POST'])
def do_register():
    u=request.form['u']; p=request.form['p']; n=request.form['n']
    conn=sqlite3.connect(DB_NAME); c=conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, fullname, status) VALUES (?,?,?,?)", (u, p, n, 'pending'))
        conn.commit(); conn.close()
        return "<script>alert('Đăng ký thành công! Vui lòng chờ Admin phê duyệt.');window.location='/login';</script>"
    except: return "<script>alert('Tên đăng nhập đã tồn tại!');window.history.back();</script>"

@app.route('/do_login', methods=['POST'])
def do_login():
    u=request.form.get('u','').strip(); p=request.form.get('p','').strip()
    if u=='admin' and p=='admin123': session['user_role']='admin'; return redirect('/admin')
    if get_setting('maintenance_mode')=='1': return "<script>alert('Bảo trì!');window.location='/login';</script>"
    conn=sqlite3.connect(DB_NAME); c=conn.cursor()
    c.execute("SELECT id, fullname, password, status FROM users WHERE username=?", (u,)); user=c.fetchone(); conn.close()
    if user and user[2]==p:
        if user[3]=='pending': return "<script>alert('Tài khoản đang chờ duyệt!');window.location='/login';</script>"
        if user[3]=='banned': return "<script>alert('Tài khoản đã bị KHÓA!');window.location='/login';</script>"
        session['user_role']='student'; session['user_id']=user[0]; session['fullname']=user[1]; LIVE_STATUS[user[0]]=datetime.datetime.now(); return redirect('/student')
    return "<script>alert('Sai thông tin!');window.location='/login';</script>"

@app.route('/logout')
def logout(): session.clear(); return redirect('/login')

# --- ADMIN ---
@app.route('/admin')
@app.route('/admin/<int:active_id>')
@app.route('/admin/pending')
@app.route('/admin/pending/<int:pending_id>')
@admin_required
def admin_dashboard(active_id=None, pending_id=None):
    mode = 'pending' if 'pending' in request.path else 'active'
    target_id = pending_id if mode == 'pending' else active_id
    query = request.args.get('q', '').strip()
    
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE status='pending'"); pending_count = c.fetchone()[0]
    
    sql = "SELECT id, username, password, fullname, status, created_at FROM users WHERE status=? AND username!='admin'"
    params = [mode]
    if query:
        sql += " AND (username LIKE ? OR fullname LIKE ?)"
        params.extend(['%'+query+'%', '%'+query+'%'])
    sql += " ORDER BY id DESC"
    c.execute(sql, params)
    users = c.fetchall()
    
    settings = get_all_settings()
    active_user = None; sessions = []; photos = []; messages = []
    summary = {'total_sessions': 0, 'total_errors': 0, 'total_time_str': "00:00:00", 'grade': "-"}
    chart_labels = []; chart_data = [] # Data for Line Chart
    
    if target_id:
        c.execute("SELECT * FROM users WHERE id=?", (target_id,))
        active_user = c.fetchone()
        if active_user:
            c.execute("SELECT * FROM user_photos WHERE user_id=? ORDER BY timestamp DESC", (target_id,))
            photos = c.fetchall()
            c.execute("SELECT * FROM logs WHERE user_id=? ORDER BY timestamp ASC", (target_id,))
            raw_logs = c.fetchall()
            c.execute("SELECT m.*, u.fullname FROM messages m JOIN users u ON m.sender_id=u.id WHERE sender_id=? ORDER BY timestamp DESC", (target_id,))
            messages = c.fetchall()
            sessions, summary = process_logs(raw_logs, settings)
            
            for s in sessions:
                chart_labels.append(s['lesson_name'])
                chart_data.append(s['error_count'])
            chart_labels.reverse(); chart_data.reverse()

    conn.close()
    return render_template_string(ADMIN_LAYOUT, users=users, active_user=active_user, sessions=sessions, summary=summary, photos=photos, settings=settings, pending_count=pending_count, messages=messages, mode=mode, chart_labels=chart_labels, chart_data=chart_data)

@app.route('/admin/approve/<int:uid>')
@admin_required
def approve_user(uid):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("UPDATE users SET status='active' WHERE id=?", (uid,)); conn.commit(); conn.close()
    return redirect('/admin/pending')

@app.route('/user/ban/<int:uid>')
@admin_required
def ban_user(uid):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("UPDATE users SET status='banned' WHERE id=?", (uid,)); conn.commit(); conn.close()
    return redirect('/admin')

@app.route('/admin/save_settings', methods=['POST'])
@admin_required
def save_settings():
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    keys = ['system_name', 'pass_mark', 'photo_interval', 'max_duration', 'announcement']
    for k in keys: c.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (k, request.form.get(k, '')))
    c.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", ('maintenance_mode', '1' if 'maintenance_mode' in request.form else '0'))
    conn.commit(); conn.close()
    return redirect('/admin')

@app.route('/user/add', methods=['POST'])
@admin_required
def add_user():
    try:
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("INSERT INTO users (username, password, fullname, status) VALUES (?,?,?,?)",(request.form['username'],request.form['password'],request.form['fullname'], 'active')); conn.commit();conn.close()
    except: pass
    return redirect('/admin')

@app.route('/user/edit', methods=['POST'])
@admin_required
def edit_user():
    try:
        uid = request.form['uid']; user = request.form['username']
        pw = request.form['password']; name = request.form['fullname']
        conn=sqlite3.connect(DB_NAME); c=conn.cursor()
        c.execute("UPDATE users SET username=?, password=?, fullname=? WHERE id=?", (user, pw, name, uid))
        conn.commit(); conn.close()
    except: pass
    return redirect('/admin/' + uid)

@app.route('/user/delete/<int:id>')
@admin_required
def delete_user(id):
    conn=sqlite3.connect(DB_NAME); c=conn.cursor()
    c.execute("DELETE FROM users WHERE id=?",(id,)); conn.commit(); conn.close()
    return redirect(request.referrer)

@app.route('/user/reset_data/<int:user_id>')
@admin_required
def reset_user_data(user_id):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("DELETE FROM logs WHERE user_id=?", (user_id,))
    c.execute("SELECT filename FROM user_photos WHERE user_id=?", (user_id,)); photos = c.fetchall()
    for p in photos:
        try: os.remove(os.path.join(ROOT_PHOTO_FOLDER, str(user_id), p[0]))
        except: pass
    c.execute("DELETE FROM user_photos WHERE user_id=?", (user_id,)); conn.commit(); conn.close()
    return redirect(request.referrer)

@app.route('/user/export/<int:user_id>')
@admin_required
def export_excel(user_id):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("SELECT fullname FROM users WHERE id=?", (user_id,)); u = c.fetchone()
    c.execute("SELECT * FROM logs WHERE user_id=? ORDER BY timestamp ASC", (user_id,)); logs = c.fetchall(); conn.close()
    si = io.StringIO(); cw = csv.writer(si)
    cw.writerow(["BÁO CÁO", u[0]]); cw.writerow(["Thời gian", "Hành động", "Chi tiết", "Kết quả"])
    for l in logs: 
        translated = translate_log_detail(l[3])
        cw.writerow([l[5], l[2], translated, l[4]])
    out = make_response(si.getvalue().encode('utf-8-sig'))
    out.headers["Content-Disposition"] = "attachment; filename=report.csv"; out.headers["Content-type"] = "text/csv"
    return out

@app.route('/admin/reply_msg', methods=['POST'])
@admin_required
def reply_msg():
    msg_id = request.form.get('msg_id'); reply = request.form.get('reply_content')
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("UPDATE messages SET reply=?, is_read=1 WHERE id=?", (reply, msg_id)); conn.commit(); conn.close()
    return redirect(request.referrer)

@app.route('/student/send_msg', methods=['POST'])
@login_required
def send_msg():
    uid = session['user_id']; content = request.form.get('content')
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT INTO messages (sender_id, content) VALUES (?, ?)", (uid, content)); conn.commit(); conn.close()
    return redirect('/student')

# --- STUDENT ---
@app.route('/student')
@login_required
def student_dashboard():
    if session.get('user_role') == 'admin': return redirect('/admin')
    uid = session['user_id']
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (uid,)); user = c.fetchone()
    c.execute("SELECT * FROM logs WHERE user_id=? ORDER BY timestamp ASC", (uid,)); raw_logs = c.fetchall()
    c.execute("SELECT * FROM messages WHERE sender_id=? ORDER BY timestamp DESC", (uid,)); messages = c.fetchall()
    settings = get_all_settings()
    all_sessions, summary = process_logs(raw_logs, settings)
    conn.close()
    return render_template_string(STUDENT_LAYOUT, user=user, sessions=all_sessions, summary=summary, settings=settings, messages=messages)

# --- UTILS (ĐÃ CẬP NHẬT LOGIC HOÀN THÀNH & TỔNG THỜI GIAN) ---
def process_logs(raw_logs, settings):
    sessions = []; summary = {'total_sessions': 0, 'total_errors': 0, 'total_time_str': "00:00:00", 'grade': "-"}
    pass_mark = int(settings.get('pass_mark', 5))
    
    # --- TÍNH TỔNG THỜI GIAN ONLINE (LOGIC MỚI) ---
    grand_total_seconds = 0
    if raw_logs:
        sorted_logs = sorted(raw_logs, key=lambda x: x[5]) # x[5] là timestamp
        current_session_start = datetime.datetime.strptime(sorted_logs[0][5], '%Y-%m-%d %H:%M:%S')
        last_time = current_session_start
        SESSION_TIMEOUT = 1800 # 30 phút * 60 giây

        for i in range(1, len(sorted_logs)):
            curr_time_str = sorted_logs[i][5]
            curr_time = datetime.datetime.strptime(curr_time_str, '%Y-%m-%d %H:%M:%S')
            delta = (curr_time - last_time).total_seconds()
            if delta < SESSION_TIMEOUT: grand_total_seconds += delta
            last_time = curr_time

    m, s = divmod(grand_total_seconds, 60); h, m = divmod(m, 60)
    summary['total_time_str'] = "{:02d}h {:02d}m".format(int(h), int(m))

    # --- LOGIC CŨ: TẠO DANH SÁCH BÀI TẬP ---
    current_sess = None
    for log in raw_logs:
        translated = translate_log_detail(log[3])
        step = {'time_only': log[5].split(' ')[1] if ' ' in log[5] else log[5], 'action_type': log[2], 'details': translated, 'result': log[4]}
        
        is_new = (log[4] == 'START') or ("Bắt đầu bài tập" in log[3])
        if is_new or (current_sess is None):
            if current_sess:
                finalize_sess(current_sess, pass_mark); sessions.insert(0, current_sess)
            
            lname = log[3].replace("Bắt đầu bài tập:", "").strip() if "Bắt đầu" in log[3] else "Thực hành"
            if lname in get_translation_map(): lname = get_translation_map()[lname]
            
            current_sess = {'lesson_name': lname, 'start_time': log[5], 'end_time': log[5], 'steps': [], 'error_count': 0, 'is_completed': False}
            current_sess['steps'].append(step)
        else:
            if current_sess: 
                current_sess['steps'].append(step); current_sess['end_time'] = log[5]
                if log[4] == 'SAI': current_sess['error_count'] += 1
                if log[4] == 'FINISH': current_sess['is_completed'] = True 

    if current_sess: finalize_sess(current_sess, pass_mark); sessions.insert(0, current_sess)
    
    summary['total_sessions'] = len(sessions)
    summary['total_errors'] = sum(s['error_count'] for s in sessions)
    
    e = summary['total_errors']
    if summary['total_sessions'] == 0: summary['grade']="-"; summary['grade_color']="#999"
    elif e == 0: summary['grade']="XUẤT SẮC"; summary['grade_color']="#16a34a"
    elif e <= pass_mark: summary['grade']="KHÁ"; summary['grade_color']="#2563eb"
    else: summary['grade']="CẦN CỐ GẮNG"; summary['grade_color']="#dc2626"
    return sessions, summary

def finalize_sess(sess, pass_mark):
    try:
        t1 = datetime.datetime.strptime(sess['start_time'], '%Y-%m-%d %H:%M:%S')
        t2 = datetime.datetime.strptime(sess['end_time'], '%Y-%m-%d %H:%M:%S')
        sess['seconds'] = (t2 - t1).total_seconds()
        m, s = divmod(sess['seconds'], 60); sess['duration_str'] = f"{int(m)}p{int(s)}s"
    except: sess['seconds']=0; sess['duration_str']="0s"
    e = sess['error_count']
    if e == 0: sess['grade'] = "S"
    elif e <= pass_mark: sess['grade'] = "A"
    else: sess['grade'] = "D"

# --- API ---
@app.route('/api/upload_photo', methods=['POST'])
def api_upload_photo():
    try:
        uid = request.args.get('uid')
        if not uid or uid == "-1": return "no_user"
        LIVE_STATUS[int(uid)] = datetime.datetime.now()
        width = int(request.args.get('w', 320)); height = int(request.args.get('h', 240))
        raw_data = request.data
        image = Image.frombytes('RGBA', (width, height), raw_data)
        if image.mode == 'RGBA': r, g, b, a = image.split(); image = Image.merge("RGB", (g, b, a)) 
        else: image = image.convert('RGB')
        folder_name = str(uid); user_folder = os.path.join(ROOT_PHOTO_FOLDER, folder_name)
        if not os.path.exists(user_folder): os.makedirs(user_folder)
        filename = f"cam_{get_vn_str().replace(' ','_').replace(':','')}.jpg"
        image.save(os.path.join(user_folder, filename))
        conn = sqlite3.connect(DB_NAME); c = conn.cursor()
        c.execute("INSERT INTO user_photos (user_id, filename, timestamp) VALUES (?, ?, ?)", (uid, filename, get_vn_str()))
        conn.commit(); conn.close()
        return "saved"
    except: return "error"

@app.route('/api/monitor')
def api_monitor():
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username != 'admin'"); users = c.fetchall(); conn.close()
    res = []
    now = datetime.datetime.now()
    for u in users:
        st = 'offline'
        if u[0] in LIVE_STATUS:
            if (now - LIVE_STATUS[u[0]]).total_seconds() < 30: st = 'online'
        res.append({'uid':u[0], 'status':st})
    return jsonify(res)

@app.route('/api/login', methods=['POST'])
def api_login_flash():
    u=request.form.get('u','').strip(); p=request.form.get('p','').strip()
    all_settings = get_all_settings()
    if all_settings.get('maintenance_mode') == '1': 
        return jsonify({"status":"fail", "msg":"MAINTENANCE", "announcement": all_settings.get('announcement', '')})
    conn=sqlite3.connect(DB_NAME); c=conn.cursor()
    c.execute("SELECT id, fullname, password, status FROM users WHERE username=?",(u,))
    user=c.fetchone(); conn.close()
    if user and user[2]==p: 
        LIVE_STATUS[user[0]] = datetime.datetime.now()
        return jsonify({
            "status": "ok", "uid": user[0], "name": user[1],
            "settings": {
                "photo_interval": int(all_settings.get('photo_interval', 10)),
                "pass_mark": int(all_settings.get('pass_mark', 5)),
                "max_duration": int(all_settings.get('max_duration', 60)),
                "announcement": all_settings.get('announcement', '')
            }
        })
    return jsonify({"status":"fail"})

@app.route('/api/log', methods=['POST'])
def api_log():
    try:
        uid = int(request.form['uid'])
        LIVE_STATUS[uid] = datetime.datetime.now()
        conn=sqlite3.connect(DB_NAME);c=conn.cursor()
        c.execute("INSERT INTO logs (user_id, action_type, details, result, timestamp) VALUES (?,?,?,?,?)",(uid,request.form['act'],request.form['det'],request.form['res'], get_vn_str())); conn.commit();conn.close();return "logged"
    except: return "err"

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)