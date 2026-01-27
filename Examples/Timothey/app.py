from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import json
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'travel_tracks_secret_key_2024'

# Путь к файлам базы данных
DB_USERS = 'data/users.json'
DB_TRACKS = 'data/tracks.json'
DB_PURCHASES = 'data/purchases.json'

ADMIN_EMAIL = 'admin@travel.com'

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        if session.get('user_email') != ADMIN_EMAIL:
            flash('Доступ запрещён. Требуются права администратора.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    tracks = load_json(DB_TRACKS)
    featured_tracks = tracks[:6]
    return render_template('index.html', tracks=featured_tracks)

@app.route('/catalog')
def catalog():
    tracks = load_json(DB_TRACKS)
    category = request.args.get('category', 'all')
    if category != 'all':
        tracks = [t for t in tracks if t.get('category') == category]
    return render_template('catalog.html', tracks=tracks, category=category)

@app.route('/track/<int:track_id>')
def track_detail(track_id):
    tracks = load_json(DB_TRACKS)
    track = next((t for t in tracks if t['id'] == track_id), None)
    if not track:
        return render_template('404.html'), 404
    return render_template('track_detail.html', track=track)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        users = load_json(DB_USERS)
        user = next((u for u in users if u['email'] == email and u['password'] == password), None)
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash('Добро пожаловать!', 'success')
            return redirect(url_for('index'))
        flash('Неверный email или пароль', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        users = load_json(DB_USERS)
        if any(u['email'] == email for u in users):
            flash('Email уже зарегистрирован', 'error')
            return render_template('register.html')
        new_user = {
            'id': len(users) + 1,
            'name': name,
            'email': email,
            'password': password
        }
        users.append(new_user)
        save_json(DB_USERS, users)
        flash('Регистрация успешна! Войдите в систему', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    users = load_json(DB_USERS)
    user = next((u for u in users if u['id'] == session['user_id']), None)
    purchases = load_json(DB_PURCHASES)
    user_purchases = [p for p in purchases if p['user_id'] == session['user_id']]
    tracks = load_json(DB_TRACKS)
    
    # Добавляем информацию о треках к покупкам
    for purchase in user_purchases:
        track = next((t for t in tracks if t['id'] == purchase['track_id']), None)
        if track:
            purchase['track_image'] = track.get('image', '')
            purchase['track_country'] = track.get('country', '')
    
    return render_template('profile.html', user=user, purchases=user_purchases)

@app.route('/profile/edit', methods=['POST'])
@login_required
def profile_edit():
    name = request.form.get('name')
    email = request.form.get('email')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    
    users = load_json(DB_USERS)
    user = next((u for u in users if u['id'] == session['user_id']), None)
    
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('profile'))
    
    # Проверяем текущий пароль если меняем пароль
    if new_password:
        if user['password'] != current_password:
            flash('Неверный текущий пароль', 'error')
            return redirect(url_for('profile'))
        user['password'] = new_password
    
    # Проверяем уникальность email
    if email != user['email']:
        if any(u['email'] == email for u in users if u['id'] != user['id']):
            flash('Этот email уже используется', 'error')
            return redirect(url_for('profile'))
    
    user['name'] = name
    user['email'] = email
    session['user_name'] = name
    session['user_email'] = email
    
    save_json(DB_USERS, users)
    flash('Профиль успешно обновлён!', 'success')
    return redirect(url_for('profile'))

@app.route('/admin')
@admin_required
def admin():
    users = load_json(DB_USERS)
    tracks = load_json(DB_TRACKS)
    purchases = load_json(DB_PURCHASES)
    
    stats = {
        'total_users': len(users),
        'total_tracks': len(tracks),
        'total_purchases': len(purchases),
        'total_revenue': sum(p['price'] for p in purchases),
        'users': users,
        'tracks': tracks,
        'purchases': purchases
    }
    return render_template('admin.html', stats=stats)

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    users = load_json(DB_USERS)
    users = [u for u in users if u['id'] != user_id]
    save_json(DB_USERS, users)
    flash('Пользователь удалён', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/track/add', methods=['POST'])
@admin_required
def admin_add_track():
    tracks = load_json(DB_TRACKS)
    new_track = {
        'id': max([t['id'] for t in tracks], default=0) + 1,
        'name': request.form.get('name'),
        'description': request.form.get('description'),
        'category': request.form.get('category'),
        'price': int(request.form.get('price', 0)),
        'duration': request.form.get('duration'),
        'distance': request.form.get('distance'),
        'difficulty': request.form.get('difficulty'),
        'country': request.form.get('country'),
        'image': request.form.get('image'),
        'rating': float(request.form.get('rating', 4.5)),
        'reviews': 0
    }
    tracks.append(new_track)
    save_json(DB_TRACKS, tracks)
    flash('Трек успешно добавлен!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/track/<int:track_id>/delete', methods=['POST'])
@admin_required
def admin_delete_track(track_id):
    tracks = load_json(DB_TRACKS)
    tracks = [t for t in tracks if t['id'] != track_id]
    save_json(DB_TRACKS, tracks)
    flash('Трек удалён', 'success')
    return redirect(url_for('admin'))

@app.route('/purchase/<int:track_id>', methods=['POST'])
@login_required
def purchase(track_id):
    tracks = load_json(DB_TRACKS)
    track = next((t for t in tracks if t['id'] == track_id), None)
    if track:
        purchases = load_json(DB_PURCHASES)
        purchase_data = {
            'id': len(purchases) + 1,
            'user_id': session['user_id'],
            'track_id': track_id,
            'track_name': track['name'],
            'price': track['price']
        }
        purchases.append(purchase_data)
        save_json(DB_PURCHASES, purchases)
        flash(f'Трек "{track["name"]}" успешно куплен!', 'success')
    return redirect(url_for('track_detail', track_id=track_id))

@app.route('/statistics')
@login_required
def statistics():
    tracks = load_json(DB_TRACKS)
    purchases = load_json(DB_PURCHASES)
    users = load_json(DB_USERS)
    
    stats = {
        'total_tracks': len(tracks),
        'total_users': len(users),
        'total_purchases': len(purchases),
        'total_revenue': sum(p['price'] for p in purchases),
        'purchases': purchases,
        'tracks': tracks
    }
    return render_template('statistics.html', stats=stats)

@app.route('/api/stats')
def api_stats():
    tracks = load_json(DB_TRACKS)
    purchases = load_json(DB_PURCHASES)
    
    # Статистика по категориям
    categories = {}
    for track in tracks:
        cat = track.get('category', 'Другое')
        categories[cat] = categories.get(cat, 0) + 1
    
    # Статистика по покупкам
    purchase_stats = {}
    for p in purchases:
        name = p['track_name'][:20]
        purchase_stats[name] = purchase_stats.get(name, 0) + 1
    
    return jsonify({
        'categories': categories,
        'purchases': purchase_stats,
        'monthly': [12, 19, 3, 5, 2, 3, 15, 22, 18, 25, 30, 28]
    })

@app.context_processor
def inject_admin_check():
    def is_admin():
        return session.get('user_email') == ADMIN_EMAIL
    return dict(is_admin=is_admin)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    # Создаем начальные данные если их нет
    if not os.path.exists(DB_TRACKS):
        initial_tracks = [
            {"id": 1, "name": "Альпийский маршрут", "description": "Захватывающий трек через швейцарские Альпы. Проходит через живописные долины, горные перевалы и традиционные деревни. Идеально подходит для опытных путешественников.", "category": "Горы", "price": 2500, "duration": "7 дней", "distance": "120 км", "difficulty": "Сложный", "country": "Швейцария", "image": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800", "rating": 4.9, "reviews": 124},
            {"id": 2, "name": "Тропа викингов", "description": "Исторический маршрут по следам древних викингов в Норвегии. Фьорды, водопады и древние поселения ждут вас.", "category": "История", "price": 3200, "duration": "10 дней", "distance": "180 км", "difficulty": "Средний", "country": "Норвегия", "image": "https://images.unsplash.com/photo-1520769669658-f07657f5a307?w=800", "rating": 4.8, "reviews": 89},
            {"id": 3, "name": "Джунгли Амазонки", "description": "Экстремальное приключение в сердце амазонских джунглей. Уникальная флора и фауна, встречи с местными племенами.", "category": "Джунгли", "price": 4500, "duration": "14 дней", "distance": "95 км", "difficulty": "Экстремальный", "country": "Бразилия", "image": "https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800", "rating": 4.7, "reviews": 56},
            {"id": 4, "name": "Великий шёлковый путь", "description": "Путешествие по легендарному торговому маршруту. Древние города, пустыни и караван-сараи.", "category": "История", "price": 5800, "duration": "21 день", "distance": "450 км", "difficulty": "Средний", "country": "Узбекистан", "image": "https://images.unsplash.com/photo-1596484552834-6a58f850e0a1?w=800", "rating": 4.9, "reviews": 203},
            {"id": 5, "name": "Патагония дикая", "description": "Нетронутая природа Патагонии. Ледники, горы и бескрайние степи на краю света.", "category": "Горы", "price": 6200, "duration": "12 дней", "distance": "200 км", "difficulty": "Сложный", "country": "Аргентина", "image": "https://images.unsplash.com/photo-1478827536114-da961b7f86d2?w=800", "rating": 5.0, "reviews": 178},
            {"id": 6, "name": "Сафари Серенгети", "description": "Незабываемое сафари в национальном парке Серенгети. Большая пятёрка и великая миграция.", "category": "Сафари", "price": 7500, "duration": "8 дней", "distance": "350 км", "difficulty": "Лёгкий", "country": "Танзания", "image": "https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800", "rating": 4.8, "reviews": 312},
            {"id": 7, "name": "Камино де Сантьяго", "description": "Знаменитый паломнический путь через север Испании. Духовное путешествие и культурное наследие.", "category": "Пешие", "price": 1800, "duration": "30 дней", "distance": "800 км", "difficulty": "Средний", "country": "Испания", "image": "https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=800", "rating": 4.6, "reviews": 445},
            {"id": 8, "name": "Гималайский трек", "description": "Базовый лагерь Эвереста. Путь к подножию высочайшей вершины мира через непальские деревни.", "category": "Горы", "price": 4800, "duration": "16 дней", "distance": "130 км", "difficulty": "Сложный", "country": "Непал", "image": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800", "rating": 4.9, "reviews": 267}
        ]
        save_json(DB_TRACKS, initial_tracks)
    
    if not os.path.exists(DB_USERS):
        save_json(DB_USERS, [{"id": 1, "name": "Админ", "email": "admin@travel.com", "password": "admin123"}])
    
    if not os.path.exists(DB_PURCHASES):
        save_json(DB_PURCHASES, [])
    
    app.run(debug=True)
