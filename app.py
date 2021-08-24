from flask import Flask, render_template, redirect, url_for, request, g
from flask_login import login_required, current_user, login_user, logout_user
from models import User,Store,Neighbourhood,Journey,db,login
import sqlite3
import os

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


@app.route('/search', methods = ['POST', 'GET'])
@login_required
def search():
    stores = Store.query.all()
    neighbourhoods = Neighbourhood.query.all()

    if request.method == 'POST':
        neighbourhood_id = request.form['neighbourhood_id']
        store_id = request.form['store_id']
        n_name = Neighbourhood.query.get(neighbourhood_id).name
        s_name = Store.query.get(store_id).name
        journeys = Journey.query.filter_by(n_id=neighbourhood_id,s_id=store_id)
        results = []

        for journey in journeys:
            current_journey=[]
            current_journey.append(journey.id)
            current_journey.append(n_name)
            current_journey.append(s_name)
            current_journey.append(journey.note)
            current_journey.append(journey.cost)
            passenger_ids = journey.passenger_list.split(",")
            nr_of_passengers=len(passenger_ids)+1
            current_journey.append(nr_of_passengers)
            results.append(current_journey)
        return render_template('search.html', stores=stores, neighbourhoods=neighbourhoods,results=results, s_name=s_name, n_name=n_name)

    else:
        return render_template('search.html', stores=stores, neighbourhoods=neighbourhoods)
 
 
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/search')
     
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email = email).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/search')
     
    return render_template('login.html')
 
@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/search')
     
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']
 
        if User.query.filter_by(email=email).first():
            return ('Email already Present')
             
        user = User(email=email, name=name, surname=surname)
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
    created_journey_ids = []
    joined_journeys = []
    created_journeys = []

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
            current_journey.append(Neighbourhood.query.get(temp.n_id).name)
            current_journey.append(Store.query.get(temp.s_id).name)
            current_journey.append(temp.note)
            current_journey.append(temp.cost)
            passenger_ids = temp.passenger_list.split(",")
            nr_of_passengers=len(passenger_ids)+1
            current_journey.append(nr_of_passengers)
            joined_journeys.append(current_journey)

        for created_journey_id in created_journey_ids:
            temp = Journey.query.get(created_journey_id)
            current_journey=[]
            current_journey.append(created_journey_id)
            current_journey.append(Neighbourhood.query.get(temp.n_id).name)
            current_journey.append(Store.query.get(temp.s_id).name)
            current_journey.append(temp.note)
            current_journey.append(temp.cost)
            passenger_ids = temp.passenger_list.split(",")
            nr_of_passengers=len(passenger_ids)+1
            current_journey.append(nr_of_passengers)
            created_journeys.append(current_journey)

    return render_template('profile.html', user=user, created_journeys=created_journeys, joined_journeys=joined_journeys)


@app.route('/create', methods=['POST', 'GET'])
@login_required
def create():
    
    if request.method == 'POST':
        #Getting info from the from elements
        neighbourhood_id = request.form['neighbourhood_id']
        store_id = request.form['store_id']
        cost = request.form['cost']
        passenger_limit = request.form['passenger_limit']
        note = request.form['note']
        
        driver_id = current_user.get_id()
        n_id = Neighbourhood.query.filter_by(id=neighbourhood_id).first_or_404().id
        s_id = Store.query.filter_by(id=store_id).first_or_404().id
     
        journey = Journey(driver_id=driver_id, n_id=n_id, s_id=s_id, cost=cost, passenger_limit=passenger_limit, note=note)
        db.session.add(journey)
        db.session.commit()
        return redirect('/journey/'+journey.id)  #REDIRECT HERE TO THE CREATED JOURNEY
    else:
        stores = Store.query.all()
        neighbourhoods = Neighbourhood.query.all()
        return render_template('create.html', stores=stores, neighbourhoods=neighbourhoods)

@app.route('/journey/<id>', methods=['POST', 'GET'])
@login_required
def journey(id):
    #Query the journey info first
    journey = Journey.query.filter_by(id=id).first()
    driver = User.query.filter_by(id=journey.driver_id).first()
    neighbourhood = Neighbourhood.query.filter_by(id=journey.n_id).first()
    store = Store.query.filter_by(id=journey.s_id).first()
    is_own=False
    is_passenger=False


    #Check if the user is displaying his own journey
    if journey.driver_id == int(current_user.get_id()):
        is_own=True

    #Check if the user is already joined this journey
    if journey.passenger_list is not None:
        passenger_ids = journey.passenger_list.split(",")

        if current_user.get_id() in passenger_ids:
            is_passenger=True
    

    #If request is to join this journey and the user does not own the journey
    if request.method == 'POST':
        if 'join-journey' in request.form and is_own == False:
            if journey.passenger_list is None:
                journey.passenger_list = current_user.get_id()
            else:
                journey.passenger_list = journey.passenger_list+","+current_user.get_id()
            journey.passenger_limit = int(journey.passenger_limit)-1

        if 'leave-journey' in request.form:
            passenger_ids = journey.passenger_list.split(",")
            passenger_ids.remove(current_user.get_id())
            if(len(passenger_ids)>0):
                journey.passenger_list = ','.join(passenger_ids)
            else:
                journey.passenger_list = None
            journey.passenger_limit = int(journey.passenger_limit)+1
            

        if 'cancel-journey' in request.form:
            journey.is_cancelled=1
        
        db.session.commit()
        return redirect('/journey/'+id)
    else:
        if journey.passenger_list is None:
            return render_template('journey.html', journey=journey, driver=driver, neighbourhood=neighbourhood, store=store, is_own=is_own, is_passenger=is_passenger)
            
        else:
            passenger_ids = journey.passenger_list.split(",")
            nr_of_passengers=len(passenger_ids)+1
            passengers = []

            for i in passenger_ids:
                current_passenger = User.query.filter_by(id=i).first()
                current_passenger_info=[current_passenger.name, current_passenger.surname, current_passenger.email]
                passengers.append(current_passenger_info)

            return render_template('journey.html', journey=journey, driver=driver, neighbourhood=neighbourhood, store=store, passengers=passengers, is_own=is_own, is_passenger=is_passenger, nr_of_passengers=nr_of_passengers)
    