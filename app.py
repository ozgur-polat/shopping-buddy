from flask import Flask, render_template, redirect, url_for, request, g
from flask_login import login_required, current_user, login_user, logout_user
from models import User,Store,JourneyRequest,Journey,db,login
from PostcodeConverter import PostcodeConverter
from dateutil import parser
import sqlite3
import os
import datetime
import numpy as np
import pandas as pd
import minmax_kmeans
from matplotlib import pyplot as plt
import matplotlib.cm as cm

# currentdirectory = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = 'xyz'
 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
 
db.init_app(app)
login.init_app(app)
login.login_view = 'login'

 
@app.before_first_request
def create_all():
    db.create_all()


@app.route('/')
def main():
    return render_template("index.html")


@app.route('/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/stores')
     
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email = email).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/stores')
     
    return render_template('login.html')
 
@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/stores')
     
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']
        city = request.form['city']
        postcode = request.form['postcode']
 
        if User.query.filter_by(email=email).first():
            return ('Email already Present')

        # here the function to get the lat long and pusherem
        post_code_converter = PostcodeConverter()
        lat, lon = post_code_converter.convert_postcode_to_lat_long(postcode, city)

        

        user = User(email=email, name=name, surname=surname, city=city, postcode=postcode, lat=lat, lon=lon)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')
 
 
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/profile/<id>')
@login_required
def profile(id):
    user = User.query.filter_by(id=id).first_or_404()
    all_journeys = Journey.query.all()
    joined_journey_ids = []
    joined_journeys = []

    all_journey_requests = JourneyRequest.query.filter_by(requester_id=id).all()

    journey_requests = []

    if all_journey_requests is not None:
        for journey in all_journey_requests:
            store=Store.query.filter_by(id=journey.store_id).first()
            journey_request = []
            journey_request.append(store.id)
            journey_request.append(store.name)
            journey_request.append(store.city)
            journey_request.append(store.postcode)
            journey_request.append(journey.date)

            journey_requests.append(journey_request)

    if all_journeys is not None:
        for journey in all_journeys:
            if journey.driver_id == int(id):
                created_journey_ids.append(journey.id)
            
            passenger_ids = journey.passenger_list.split(",")

            if id in passenger_ids:
                joined_journey_ids.append(journey.id)
    
        for joined_journey_id in joined_journey_ids:
            temp = Journey.query.get(joined_journey_id)
            current_journey=[]
            current_journey.append(joined_journey_id)
            current_journey.append(Store.query.get(temp.s_id).name)
            current_journey.append(Store.query.get(temp.s_id).address)
            current_journey.append(temp.date)
            joined_journeys.append(current_journey)

    return render_template('profile.html', user=user, joined_journeys=joined_journeys, journey_requests=journey_requests)

 
@app.route('/stores')
@login_required
def stores():
    stores = Store.query.all()
    return render_template('stores.html', stores=stores, user_id = int(current_user.get_id()))

@app.route('/store/<id>', methods=['POST', 'GET'])
@login_required
def store(id):
    store = Store.query.get(id)
    if request.method == 'POST':
        date = request.form['date']
        date = date[0:10]
        date = datetime.datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]))

        user = User.query.get(current_user.get_id())
        
        journey_request = JourneyRequest(requester_id=user.id,requester_lat=float(user.lat), requester_lon=float(user.lon), store_id = store.id, store_name = store.name, store_lat=float(store.lat), store_lon=float(store.lon), date=date)
        db.session.add(journey_request)
        db.session.commit()
        return redirect('/profile/'+current_user.get_id()) ## RETURN HERE TO PROFILE PAGE TO LIST THE REQUESTS AND ASSIGNED JOURNEYS
    else:
        return render_template('store.html', store=store)

@app.route('/create-store', methods=['POST', 'GET'])
@login_required
def create_store():
    if int(current_user.get_id()) == 1:
        if request.method == 'POST':
            name = request.form['name']
            city = request.form['city']
            postcode = request.form['postcode']
            
            post_code_converter = PostcodeConverter()
            lat, lon = post_code_converter.convert_postcode_to_lat_long(postcode, city)

            store = Store(name=name, city=city, postcode=postcode, lat=lat, lon=lon)
            db.session.add(store)
            db.session.commit()
            return redirect('/store/'+ str(store.id))
        else:
            return render_template('create-store.html')
    else:
        return redirect('/stores')


@app.route('/assign')
@login_required
def assign():

    nr_users_to_generate = 200

    try:
        df = pd.read_pickle('test_df.pkl')
    except:
        lat = np.random.uniform(low=52.171713, high=52.301421, size=(nr_users_to_generate,))
        long = np.random.uniform(low=20.937595, high=21.094625, size=(nr_users_to_generate,))
        coordinates = np.array((lat,long)).T
        df = pd.DataFrame(coordinates, columns=['lat','long'])

        df['cluster_id'] = minmax_kmeans.get_clusters(df, k=len(df)//4, min_size=4, max_size=4,num_iter=5)
        df.to_pickle('test_df.pkl')

    BBox = (df.long.min(),df.long.max(),df.lat.min(), df.lat.max())

    warsaw_map = plt.imread('static/warsaw_map.png')

    fig, ax = plt.subplots(figsize = (8,7))
    ax.scatter(df.long, df.lat, zorder=1, alpha= 0.9, c=df.cluster_id, s=20, cmap='tab20')
    ax.set_title('Plotting Members with Clusters on Warsaw Map')
    ax.set_xlim(BBox[0],BBox[1])
    ax.set_ylim(BBox[2],BBox[3])
    ax.imshow(warsaw_map, zorder=0, extent = BBox, aspect= 'equal')
    plt.savefig('static/test.png')

    return render_template('assign.html')
    