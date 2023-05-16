from flask import Flask, render_template, redirect, request, session, flash
from flask_app import app
from flask_bcrypt import Bcrypt
from flask_app.models import user
from flask_app.models import sighting

bcrypt = Bcrypt(app)

#login 

@app.route('/')
@app.route('/login')
def login_index():

    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    if not user.User.validate_user(request.form):
        return redirect('/')
    
    pw_hash = bcrypt.generate_password_hash(request.form['password'])

    data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': pw_hash
    }

    user_id = user.User.add_user(data)
    if 'user_id' not in session:
        session['user_id'] = user_id
    session['user_id'] = user_id

    return redirect('/dashboard')

@app.route('/login', methods=['POST'])
def login():
    data = {
        'email': request.form['email']
    }
    u = user.User.get_one_by_email(data)

    if not u:
        flash('invalid email/password', 'login_error')
        return redirect('/')
    if not bcrypt.check_password_hash(u.password, request.form['password']):
        flash('invalid email/password', 'login_error')
        return redirect('/')
    session['user_id'] = u.id

    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.clear()

    return redirect('/')

# dashboard

@app.route('/dashboard')
def dashboard_index():
    if 'user_id' not in session:
        flash('Need to login first!', 'login_error')
        return redirect('/')
    
    data = {
        'id': session['user_id']
    }
    sightings_list = []
    all_sightings = sighting.Sighting.get_all()
    for sight in all_sightings:
        sight_data = {
            'id': sight.id
        }
        s = sighting.Sighting.get_users_with_sightings(sight_data)
        for x in s.skeptics:
            if x.first_name == None:
                s.skeptics.pop()
                sightings_list.append(s)
            else:
                sightings_list.append(s)

    return render_template('dashboard.html', user=user.User.get_one(data), sightings_list=sightings_list)

# create sighting

@app.route('/dashboard/report')
def create_report_index():
    if 'user_id' not in session:
        flash('Need to login first!', 'login_error')
        return redirect('/')
    
    data = {
        'id': session['user_id']
    }
    
    return render_template('create_sighting.html', user=user.User.get_one(data))

@app.route('/dashboard/report/create', methods=['POST'])
def create_report():
    if not sighting.Sighting.validate_sighting(request.form):
        return redirect('/dashboard/report')
    
    data = {
        'location': request.form['location'],
        'what_happened': request.form['what_happened'],
        'date_of_siting': request.form['date_of_siting'],
        'num_of_sasquatches': request.form['num_of_sasquatches'],
        'user_id': session['user_id']
    }

    sighting.Sighting.add_sighting(data)

    return redirect('/dashboard')

# view sighting

@app.route('/show/<int:id>')
def view_sighting(id):
    if 'user_id' not in session:
        flash('Need to login first!', 'login_error')
        return redirect('/')
    
    data = {
        'id': id
    }
    sighting_with_skeptics = sighting.Sighting.get_users_with_sightings(data)
    return render_template('show.html', user=user.User.get_one({'id':session['user_id']}), s=sighting.Sighting.get_one(data), skeptics=sighting_with_skeptics.skeptics)

@app.route('/show/<int:id>/add_skeptic', methods=['POST'])
def add_skeptic(id):
    data = {
        'user_id':session['user_id'],
        'sighting_id': id
    }
    sighting.Sighting.add_skeptic(data)

    return redirect(f'/show/{id}')

@app.route('/show/<int:id>/delete_skeptic', methods=['POST'])
def delete_skeptic(id):
    data = {
        'user_id': session['user_id'],
        'sighting_id': id
    }
    sighting.Sighting.delete_skeptic(data)

    return redirect(f'/show/{id}')
# edit and deleting sighting

@app.route('/edit/<int:id>')
def edit_index(id):
    if 'user_id' not in session:
        flash('Need to login first!', 'login_error')
        return redirect('/')
    
    data = {
        'id': id
    }

    s = sighting.Sighting.get_one(data)

    return render_template('edit_sighting.html', user=user.User.get_one({'id':session['user_id']}), s=s)

@app.route('/edit/<int:id>/process', methods=['POST'])
def edit_sighting(id):
    if not sighting.Sighting.validate_sighting(request.form):
        return redirect(f'/dashboard/edit/{id}')
    
    data = {
        'location': request.form['location'],
        'what_happened': request.form['what_happened'],
        'date_of_siting': request.form['date_of_siting'],
        'num_of_sasquatches': request.form['num_of_sasquatches'],
        'id': id
    }

    sighting.Sighting.edit(data)

    return redirect('/dashboard')

@app.route('/delete/<int:id>')
def delete_sighting(id):
    data = {
        'id':id
    }

    sighting.Sighting.delete(data)
    return redirect('/dashboard')