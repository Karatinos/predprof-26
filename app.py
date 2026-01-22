from flask import Flask, render_template

# Initialize Flask with template_folder set to current directory '.'
# This fixes the "TemplateNotFound" error if files are in the root folder
app = Flask(__name__)

# Homepage
@app.route('/index.html')
def home():
    return render_template('index.html')

# Login Page
@app.route('/login.html')
def login():
    return render_template('login.html')

# Registration Page
@app.route('/register.html')
def register():
    return render_template('register.html')

# User Profile
@app.route('/profile.html')
def profile():
    return render_template('profile.html')

# Product Catalog
@app.route('/catalog.html')
def catalog():
    return render_template('catalog.html')

# Item Detail Page
@app.route('/item.html')
def item():
    # In a real app, you would fetch item details using the ID
    # For now, we return the static item template
    return render_template('item.html')

# Custom 404 Error Handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=8001)
