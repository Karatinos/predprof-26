from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
import random
import string
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Измените на свой секретный ключ

# ============================================
# НАСТРОЙКИ ПОЧТЫ - УКАЖИТЕ СВОИ ДАННЫЕ
# ============================================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # SMTP сервер
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'YOUR_EMAIL@gmail.com'  # <-- ВАША ПОЧТА
app.config['MAIL_PASSWORD'] = 'YOUR_APP_PASSWORD'     # <-- ПАРОЛЬ ПРИЛОЖЕНИЯ
app.config['MAIL_DEFAULT_SENDER'] = 'YOUR_EMAIL@gmail.com'  # <-- ВАША ПОЧТА
# ============================================

mail = Mail(app)

# База данных (в реальном проекте используйте настоящую БД)
users = {
    'demo@example.com': {'password': 'demo123', 'verified': True, 'name': 'Демо Пользователь'}
}
verification_codes = {}

def generate_code(length=6):
    """Генерация случайного кода"""
    return ''.join(random.choices(string.digits, k=length))

def send_email(to_email, subject, code, template_type='verify'):
    """
    Универсальная функция отправки email
    template_type: 'verify' - верификация, 'login' - вход, 'register' - регистрация
    """
    templates = {
        'register': {
            'title': 'Подтверждение регистрации',
            'message': 'Для завершения регистрации введите код:'
        },
        'login': {
            'title': 'Код для входа',
            'message': 'Для входа в аккаунт введите код:'
        },
        'verify': {
            'title': 'Код подтверждения',
            'message': 'Ваш код подтверждения:'
        }
    }
    
    t = templates.get(template_type, templates['verify'])
    
    html_content = f'''
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px 15px 0 0;">
            <h1 style="color: white; margin: 0; text-align: center;">🚀 LearnHub</h1>
        </div>
        <div style="background: #ffffff; padding: 30px; border: 1px solid #e5e7eb; border-top: none;">
            <h2 style="color: #1f2937; margin-top: 0;">{t['title']}</h2>
            <p style="color: #6b7280;">{t['message']}</p>
            <div style="background: #f3f4f6; padding: 25px; text-align: center; border-radius: 12px; margin: 20px 0;">
                <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #667eea;">{code}</span>
            </div>
            <p style="color: #9ca3af; font-size: 14px;">Код действителен 10 минут.</p>
            <p style="color: #9ca3af; font-size: 14px;">Если вы не запрашивали этот код, проигнорируйте письмо.</p>
        </div>
        <div style="background: #f9fafb; padding: 20px; border-radius: 0 0 15px 15px; text-align: center; border: 1px solid #e5e7eb; border-top: none;">
            <p style="color: #9ca3af; margin: 0; font-size: 12px;">© 2024 LearnHub. Все права защищены.</p>
        </div>
    </div>
    '''
    
    try:
        msg = Message(subject=subject, recipients=[to_email], html=html_content)
        mail.send(msg)
        return True, None
    except Exception as e:
        return False, str(e)

def login_required(f):
    """Декоратор для защиты страниц"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            flash('Войдите в аккаунт', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== МАРШРУТЫ ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = users.get(session['user_email'], {})
    return render_template('dashboard.html', user=user, email=session['user_email'])

# ==================== РЕГИСТРАЦИЯ ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        if not email or not password or not name:
            flash('Заполните все поля', 'error')
            return redirect(url_for('register'))
        
        if email in users and users[email].get('verified'):
            flash('Пользователь уже существует', 'error')
            return redirect(url_for('register'))
        
        # Сохраняем и отправляем код
        code = generate_code()
        users[email] = {'password': password, 'verified': False, 'name': name}
        verification_codes[email] = {
            'code': code,
            'expiry': datetime.now() + timedelta(minutes=10),
            'type': 'register'
        }
        
        success, error = send_email(email, 'Подтверждение регистрации - LearnHub', code, 'register')
        
        if success:
            session['pending_email'] = email
            session['verify_type'] = 'register'
            flash('Код отправлен на почту', 'success')
            return redirect(url_for('verify'))
        else:
            flash(f'Ошибка отправки: {error}', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

# ==================== ВХОД ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Заполните все поля', 'error')
            return redirect(url_for('login'))
        
        user = users.get(email)
        
        if not user or user['password'] != password:
            flash('Неверный email или пароль', 'error')
            return redirect(url_for('login'))
        
        if not user.get('verified'):
            flash('Аккаунт не подтверждён', 'error')
            return redirect(url_for('login'))
        
        # Отправляем код для двухфакторной аутентификации
        code = generate_code()
        verification_codes[email] = {
            'code': code,
            'expiry': datetime.now() + timedelta(minutes=10),
            'type': 'login'
        }
        
        success, error = send_email(email, 'Код для входа - LearnHub', code, 'login')
        
        if success:
            session['pending_email'] = email
            session['verify_type'] = 'login'
            flash('Код отправлен на почту', 'success')
            return redirect(url_for('verify'))
        else:
            flash(f'Ошибка отправки: {error}', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# ==================== ВЕРИФИКАЦИЯ ====================

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'pending_email' not in session:
        return redirect(url_for('index'))
    
    email = session['pending_email']
    verify_type = session.get('verify_type', 'register')
    
    if request.method == 'POST':
        code = request.form.get('code')
        stored = verification_codes.get(email)
        
        if not stored:
            flash('Код не найден. Попробуйте снова.', 'error')
            return redirect(url_for('login') if verify_type == 'login' else url_for('register'))
        
        if datetime.now() > stored['expiry']:
            flash('Код истёк. Запросите новый.', 'error')
            return redirect(url_for('verify'))
        
        if code != stored['code']:
            flash('Неверный код', 'error')
            return redirect(url_for('verify'))
        
        # Успешная верификация
        del verification_codes[email]
        
        if verify_type == 'login':
            session['user_email'] = email
            del session['pending_email']
            del session['verify_type']
            flash(f'Добро пожаловать, {users[email]["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            users[email]['verified'] = True
            del session['pending_email']
            del session['verify_type']
            flash('Регистрация завершена! Теперь войдите.', 'success')
            return redirect(url_for('login'))
    
    return render_template('verify.html', email=email, verify_type=verify_type)

@app.route('/resend')
def resend():
    email = session.get('pending_email')
    verify_type = session.get('verify_type', 'register')
    
    if not email:
        return redirect(url_for('index'))
    
    code = generate_code()
    verification_codes[email] = {
        'code': code,
        'expiry': datetime.now() + timedelta(minutes=10),
        'type': verify_type
    }
    
    subject = 'Код для входа - LearnHub' if verify_type == 'login' else 'Код подтверждения - LearnHub'
    success, error = send_email(email, subject, code, verify_type)
    
    if success:
        flash('Новый код отправлен', 'success')
    else:
        flash(f'Ошибка: {error}', 'error')
    
    return redirect(url_for('verify'))

# ==================== ВЫХОД ====================

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из аккаунта', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
