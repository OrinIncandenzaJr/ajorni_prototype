from flask import render_template, flash, redirect, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ItineraryForm, ActivityForm, EditActivityForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Itinerary, Activity
from flask import request
from werkzeug.urls import url_parse
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    itineraries = current_user.followed_itineraries().paginate(page,
            app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=itineraries.next_num) if itineraries.has_next else None
    prev_url = url_for('index', page=itineraries.prev_num) if itineraries.has_prev else None
    return render_template('index.html', title='Home',
                           itineraries=itineraries.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    itineraries = user.itineraries.order_by(Itinerary.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('user', username=user.username, page=itineraries.next_num) \
        if itineraries.has_next else None
    prev_url = url_for('user', username=user.username, page=itineraries.prev_num) \
        if itineraries.has_prev else None
    return render_template('user.html', user=user, itineraries=itineraries.items,
        next_url=next_url, prev_url=prev_url)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are following {username}')
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {username}')
    return redirect(url_for('user', username=username))

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    itineraries = Itinerary.query.order_by(Itinerary.timestamp.desc()).paginate(page,
        app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=itineraries.next_num) \
        if itineraries.has_next else None
    prev_url = url_for('explore', page=itineraries.prev_num) \
        if itineraries.has_prev else None
    return render_template('index.html', title='Explore', itineraries=itineraries.items,
                           next_url=next_url, prev_url=prev_url)

@app.route('/itinerary/<itinerary_id>')
@login_required
def itinerary(itinerary_id):
    itinerary = Itinerary.query.filter_by(id=itinerary_id).first()
    name = itinerary.name
    activities = itinerary.get_activities()
    return render_template('itinerary.html', title=name, activities=activities, itinerary=itinerary)

@app.route('/add_activity/<itinerary_id>', methods=['GET', 'POST'])
@login_required
def add_activity(itinerary_id):
    form = ActivityForm()
    if form.validate_on_submit():
        activity = Activity(itinerary_id=itinerary_id, name=form.name.data,
            description=form.description.data)
        db.session.add(activity)
        db.session.commit()
        return redirect(url_for('itinerary', itinerary_id=itinerary_id))
    return render_template('add_activity.html', form=form)

@app.route('/activity/<activity_id>')
@login_required
def activity(activity_id):
    activity = Activity.query.filter_by(id=activity_id).first()
    return render_template('activity.html', title=activity.name, activity=activity, itinerary_id=activity.itinerary_id)


@app.route('/edit_activity/<activity_id>', methods=['GET', 'POST'])
@login_required
def edit_activity(activity_id):
    activity = Activity.query.filter_by(id=activity_id).first()
    form = EditActivityForm()
    if form.validate_on_submit():
        activity.name = form.name.data
        activity.description = form.description.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('activity', activity_id=activity_id))
    elif request.method == 'GET':
        form.name.data = activity.name
        form.description.data = activity.description
    return render_template('edit_activity.html', form=form)

@app.route('/edit_itinerary/<itinerary_id>')
@login_required
def edit_itinerary(itinerary_id):
    itinerary = Itinerary.query.filter_by(id=itinerary_id).first()
    activities = itinerary.get_activities()
    return render_template('edit_itinerary.html', activities=activities, itinerary=itinerary)


@app.route('/add_itinerary', methods=['GET', 'POST'])
@login_required
def add_itinerary():
    form = ItineraryForm()
    if form.validate_on_submit():
        itinerary = Itinerary(name=form.name.data, city=form.city.data)
        db.session.add(itinerary)
        db.session.commit()
        flash('Your itinerary is now live!')
        return redirect(url_for('add_activity', itinerary_id=itinerary.id)) #create route for this one
    return render_template('add_itinerary.html', form=form)
