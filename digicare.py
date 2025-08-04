from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import Column, Integer, String, Numeric
import pymysql
from pytz import timezone
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY']='CSE471'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://digicareAdmin:abcd1234@localhost:3306/digicare'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)




#---------------------DB models start----------------------------------------#

#-------------------main table---------------------------#
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False)
    password = db.Column(db.String(100), nullable = False)
    seq_q = db.Column(db.String(100))
    seq_a = db.Column(db.String(100))
    Fname = db.Column(db.String(100))
    Lname = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(100))
    height = db.Column(Numeric(5,2))
    weight = db.Column(Numeric(5,2))
    bloodType = db.Column(db.String(100))
    bloodDonate = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    address = db.Column(db.String(100))
    allergies = db.Column(db.String(100))
    medications = db.Column(db.String(100))
    conditions = db.Column(db.String(100))
    surgeries = db.Column(db.String(100))
    familyHistory = db.Column(db.String(100))
    aType = db.Column(db.String(100))
    flag = db.Column(db.String(100))

    def __repr__(self) -> str:
        return f'{self.id} - {self.email} - {self.username} - {self.password}'
    


class Goal(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(100), nullable = False)
    status = db.Column(db.String(100), nullable = False)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self) -> str:
        return f'{self.id} - {self.name} - {self.description}'
    



class Med(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable = False)
    type = db.Column(db.String(100), nullable = False)
    strength = db.Column(db.String(100), nullable = False)
    time = db.Column(db.String(100), nullable = False)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(100), default="Course Running")


    def __repr__(self) -> str:
        return f'{self.id} - {self.name} - {self.type} - {self.strength} - {self.time}'
    


class HealthData(db.Model):
    
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        date = db.Column(db.String(100), nullable = False)
        weight = db.Column(db.Integer, nullable = False)
        etime = db.Column(db.String(100), nullable = False)
        fstep = db.Column(db.Integer, nullable = False)
        heartRate = db.Column(db.Integer, nullable = False)
        bloodPressure = db.Column(db.String(100), nullable = False)
        bloodSugar = db.Column(db.Integer, nullable = False)
        user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
        
        def __repr__(self) -> str:
            return f'{self.id} - {self.date} - {self.etime} - {self.heartRate} - {self.bloodPressure} - {self.bloodSugar}'
        



class DonationRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_name= db.Column(db.String(100), nullable=False)
    donor_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(100), nullable=False)
    is_seen = db.Column(db.String(100), default=None)
    accepted = db.Column(db.String(100), default=None)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    

    def __repr__(self) -> str:
        return f'{self.id} - {self.donor_id} - {self.donor_id} - {self.message} - {self.is_seen} - {self.accepted}'

    

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

   
#---------------------DB models end----------------------------------------#




#Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('useremail')
        username = request.form.get('username')
        password = request.form.get('userpassword')
        seq_q = request.form.get('seq_q')
        seq_a = request.form.get('seq_a')
        #aType = request.form.get('aType')
        #print(aType)
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password, method='sha256'), seq_q=seq_q, seq_a=seq_a, aType="User", flag="Unbanned")
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('index'))
        
    return render_template("signup.html", user=current_user)



@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('useremail')
        password = request.form.get('userpassword')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                if user.flag == "Banned":
                    return redirect(url_for('AccountBanned'))
                flash('Logged in successfully.', category='success')
                login_user(user, remember=True)
                if user.Fname==None or user.Lname==None or user.age==None or user.gender==None or user.height==None or user.weight==None or user.bloodType==None or user.allergies==None or user.medications==None or user.conditions==None or user.surgeries==None or user.familyHistory==None:
                    return redirect(url_for('setup'))

                return redirect(url_for('index'))
            
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)



@app.route("/setup", methods=['GET', 'POST'])
@login_required
def setup():
    user=current_user
    if request.method == 'POST':
        user.Fname = request.form.get('Fname')
        user.Lname = request.form.get('Lname')
        user.age = request.form.get('age')
        user.gender = request.form.get('gender')
        user.height = request.form.get('height')
        user.weight = request.form.get('weight')
        user.bloodType = request.form.get('bloodType')
        user.bloodDonate = request.form.get('bloodDonate')
        user.phone = request.form.get('phone')
        user.address = request.form.get('address')
        user.allergies = request.form.get('allergies')
        user.medications = request.form.get('medications')
        user.conditions = request.form.get('conditions')
        user.surgeries = request.form.get('surgeries')
        user.familyHistory = request.form.get('familyHistory')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("setup.html", user=current_user)



@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route("/forgotpassword", methods=['GET', 'POST'])
def forgotpassword():
    if request.method == 'POST':
        email = request.form.get('useremail')
        seq_q = request.form.get('seq_q')
        seq_a = request.form.get('seq_a')
        user = User.query.filter_by(email=email).first()
        if user:
            if user.seq_q == seq_q and user.seq_a == seq_a:
                return render_template("resetpassword.html", email=user.email)
            else:
                return render_template("index.html", user=current_user)
        else:
            return render_template("index.html", user=current_user)
    return render_template("forgotpassword.html", user=current_user)



@app.route("/resetpassword", methods=['GET', 'POST'])
def resetpassword():
    if request.method == 'POST':
        email = request.form.get('useremail')
        password = request.form.get('userpassword')
        user = User.query.filter_by(email=email).first()
        print(email)
        print(password)
        if user:
            user.password = generate_password_hash(password, method='sha256')
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return render_template("index.html", user=current_user)
    return render_template("resetpassword.html", user=current_user)




@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():   

    return render_template("profile.html", user=current_user)



@app.route("/AddGoal", methods=['GET', 'POST'])
@login_required
def AddGoal():
    if request.method == 'POST':
        name = request.form.get('gname')
        description = request.form.get('gdesc')
        status = request.form.get('gs')
        user_id = current_user.id
        new_goal = Goal(name=name, description=description, status=status, user=user_id)
        db.session.add(new_goal)
        db.session.commit()
        return redirect(url_for('ViewGoals'))
    return render_template("AddGoal.html", user=current_user)



@app.route("/ViewGoals", methods=['GET', 'POST'])
@login_required
def ViewGoals():
    goals = Goal.query.filter_by(user=current_user.id).all()
    return render_template("ViewGoals.html", user=current_user, goals=goals)


@app.route("/GoalReached/<int:id>", methods=['GET', 'POST'])
@login_required
def GoalReached(id):
    goal = Goal.query.get_or_404(id)

        
    goal.status = "Reached"
    db.session.commit()
    return redirect(url_for('ViewGoals'))
    


@app.route("/GoalFailed/<int:id>", methods=['GET', 'POST'])
@login_required
def GoalFailed(id):
    goal = Goal.query.get_or_404(id)        
    goal.status = "Failed"
    db.session.commit()
    return redirect(url_for('ViewGoals'))



    

@app.route("/AddHealthData", methods=['GET', 'POST'])
@login_required
def AddHealthData():
    if request.method == 'POST':
        date = request.form.get('date')
        weight = request.form.get('weight')
        etime = request.form.get('etime')
        fstep = request.form.get('fstep')
        heartRate = request.form.get('heartRate')
        bloodPressure = request.form.get('bloodPressure')
        bloodSugar = request.form.get('bloodSugar')
        user_id = current_user.id
        new_healthdata = HealthData(date=date, weight=weight, etime=etime, fstep=fstep, heartRate=heartRate, bloodPressure=bloodPressure, bloodSugar=bloodSugar, user=user_id)
        db.session.add(new_healthdata)
        db.session.commit()
        return redirect(url_for('ViewHealthData'))
    return render_template("AddHealthData.html", user=current_user)




@app.route("/ViewHealthData", methods=['GET', 'POST'])
@login_required
def ViewHealthData():
    healthdata = HealthData.query.filter_by(user=current_user.id).all()

    return render_template("ViewHealthData.html", user=current_user, healthdata=healthdata)



@app.route("/AddMed", methods=['GET', 'POST'])
@login_required
def AddMed():
    if request.method == 'POST':
        name= request.form.get('mname')
        type = request.form.get('mtype')
        strength = request.form.get('mstrength')
        time = request.form.get('mtime')
        user_id = current_user.id
        new_med = Med(name=name, type=type, strength=strength, time=time, user=user_id)
        db.session.add(new_med)
        db.session.commit()
        return redirect(url_for('ViewMeds'))
    return render_template("AddMed.html", user=current_user)



@app.route("/ViewMeds", methods=['GET', 'POST'])
@login_required
def ViewMeds():
    meds = Med.query.filter_by(user=current_user.id).all()
    return render_template("ViewMeds.html", user=current_user, meds=meds)


@app.route("/MedDone/<int:id>", methods=['GET', 'POST'])
@login_required
def MedDone(id):
    med = Med.query.get_or_404(id)        
    med.status = "Course Completed"
    db.session.commit()
    return redirect(url_for('ViewMeds'))


#---------------------------------blood donor routes----------------------------#

@app.route("/BloodDonorList", methods=['GET', 'POST'])
@login_required
def BloodDonorList():
    users = User.query.filter_by(aType="User",flag='Unbanned', bloodDonate='yes' ).all()
    return render_template("BloodDonorList.html", user=current_user, users=users) 


@app.route('/request_blood', methods=['GET','POST'])
def request_blood():
    if request.method == 'POST':
        requester_id = current_user.id
        donor_id = request.form.get('donor_id')
        user_name = current_user.username
        message = request.form.get('message')

        # timezone 
        bd_tz = timezone('Asia/Dhaka')
        current_time = datetime.now().astimezone(bd_tz)


        new_request = DonationRequest(user_id=requester_id, donor_id=donor_id, user_name=user_name, message=message, accepted="Pending", timestamp=current_time)
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("request_blood.html", user=current_user)



#----------------------------------------notifications------------------------------------#


@app.route("/BloodDonationNotifications", methods=['GET', 'POST'])
@login_required
def BloodDonationNotifications():
    current_user_id = current_user.id
    
    # donation requests made by the current user (requester)
    requester_requests = DonationRequest.query.filter_by(user_id=current_user_id).all()

    # donation requests received by the current user (donor)
    donor_requests = DonationRequest.query.filter_by(donor_id=current_user_id).all()

    # additional information of donors based on donor_id (Not Using this anymore)
    donor_ids = [request.donor_id for request in requester_requests]
    donors_info = User.query.filter(User.id.in_(donor_ids)).all()

    return render_template("BloodDonationNotifications.html",
                           user=current_user,
                           requester_requests=requester_requests,
                           donor_requests=donor_requests,
                           donors_info=donors_info) 



@app.route("/NotificationsAccept/<int:id>", methods=['GET', 'POST'])
@login_required
def NotificationsAccept(id):
    request = DonationRequest.query.get_or_404(id)
    if request.accepted == "Pending":
        request.accepted = "Accepted"
        db.session.commit()
    return redirect(url_for('BloodDonationNotifications'))

@app.route("/NotificationsReject/<int:id>", methods=['GET', 'POST'])
@login_required
def NotificationsReject(id):
    request = DonationRequest.query.get_or_404(id)
    if request.accepted == "Pending":
        request.accepted = "Rejected"
        db.session.commit()
    return redirect(url_for('BloodDonationNotifications'))





# Route to get goal statistics for all users
@app.route('/statistics', methods=['GET', 'POST'])
@login_required
def get_statistics():
    #with app.app_context():    
    total_users = Goal.query.distinct(Goal.id).count()

    running_count = Goal.query.filter_by(status='Running').count()
    reached_count = Goal.query.filter_by(status='Reached').count()
    failed_count = Goal.query.filter_by(status='Failed').count()
    running_percentage = round((running_count / total_users) * 100,2) if total_users > 0 else 0
    reached_percentage = round((reached_count / total_users) * 100,2) if total_users > 0 else 0
    failed_percentage = round((failed_count / total_users) * 100,2) if total_users > 0 else 0
    current_user_id = current_user.id     
    c_running_count = Goal.query.filter_by(user=current_user_id, status='Running').count()
    c_reached_count = Goal.query.filter_by(user=current_user_id, status='Reached').count()
    c_failed_count = Goal.query.filter_by(user=current_user_id, status='Failed').count()
    c_total_count = c_running_count + c_reached_count + c_failed_count
    c_running_percentage = round((c_running_count / c_total_count) * 100, 2) if c_total_count > 0 else 0
    c_reached_percentage = round((c_reached_count / c_total_count) * 100, 2) if c_total_count > 0 else 0
    c_failed_percentage = round((c_failed_count / c_total_count) * 100, 2) if c_total_count > 0 else 0

    return render_template('statistics.html', 
            running_percentage= running_percentage,
            reached_percentage= reached_percentage,
            failed_percentage= failed_percentage,
            c_running_percentage= c_running_percentage,
            c_reached_percentage= c_reached_percentage,
            c_failed_percentage= c_failed_percentage)



#------------------------Admin panel start------------------------------------#

@app.route("/AdminBanList", methods=['GET', 'POST'])
@login_required
def AdminBanList():
    users = User.query.filter_by(aType="User").all()
    return render_template("AdminBanList.html", user=current_user, users=users)


@app.route("/AdminBan/<int:id>", methods=['GET', 'POST'])
@login_required
def AdminBan(id):
    user = User.query.get_or_404(id)
    
        
    user.flag = "Banned"
    db.session.commit()
    return redirect(url_for('AdminBanList'))

@app.route("/AdminUnban/<int:id>", methods=['GET', 'POST'])
@login_required
def AdminUnban(id):
    user = User.query.get_or_404(id)
    
        
    user.flag = "Unbanned"
    db.session.commit()
    return redirect(url_for('AdminBanList'))

@app.route("/AccountBanned", methods=['GET', 'POST'])
def AccountBanned():
    return render_template("AccountBanned.html", user=current_user)




#----------------------- Calculators start-----------------------#


@app.route("/BmiIndex", methods=['GET', 'POST'])
@login_required
def BmiIndex():
    return render_template('BmiIndex.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    if request.method == 'POST':
        weight = float(request.form['weight'])
        height = float(request.form['height'])
        age = int(request.form['age'])
        gender = request.form['gender']
        
        bmi = calculate_bmi(weight, height)
        return render_template('BmiResult.html', weight=weight, height=height, bmi=bmi, age=age, gender=gender)

def calculate_bmi(weight, height):
    bmi = weight / (height * height)
    return round(bmi, 2)




@app.route("/BmrIndex", methods=['GET', 'POST'])
@login_required
def BmrIndex():
    return render_template('BmrIndex.html')

@app.route('/calculate_bmr', methods=['POST'])
def calculate_bmr():
    if request.method == 'POST':
        weight = float(request.form['weight'])
        height = float(request.form['height'])
        age = int(request.form['age'])
        gender = request.form['gender']
        
        bmr = calculate_bmr_value(weight, height, age, gender)
        return render_template('BmrResult.html', weight=weight, height=height, age=age, gender=gender, bmr=bmr)

def calculate_bmr_value(weight, height, age, gender):
    if gender == 'male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height * 100) - (5.677 * age)
    else:  # female
        bmr = 447.593 + (9.247 * weight) + (3.098 * height * 100) - (4.330 * age)

    return round(bmr,2)
    


@app.route('/bodyfat_index', methods=['GET', 'POST'])
@login_required
def bodyfat_index():
    return render_template('bodyfat_index.html')


@app.route('/calculate_bodyfat', methods=['POST'])
def calculate_bodyfat():
    if request.method == 'POST':
        gender = request.form['gender']
        weight = float(request.form['weight'])
        waist = float(request.form['waist'])
        wrist = float(request.form['wrist'])
        hip = float(request.form['hip'])
        forearm = float(request.form['forearm'])

        body_fat = calculate_body_fat_percentage(gender, weight, waist, wrist, hip, forearm)
        fitness_evaluation = evaluate_fitness(body_fat, gender)

        return render_template('bodyfat_result.html', gender=gender, body_fat=body_fat, fitness_evaluation=fitness_evaluation)

def calculate_body_fat_percentage(gender, weight, waist, wrist, hip, forearm):
    if gender == 'male':
        body_fat = (weight * 0.732) + (waist / 3.785) - (wrist * 0.393) - (hip * 0.394) + (forearm * 0.434) - 28.57
    else:  # female
        body_fat = (weight * 0.732) + (waist / 3.786) - (wrist * 0.393) - (hip * 0.394) + (forearm * 0.434) - 28.57
    return round(body_fat, 2)

def evaluate_fitness(body_fat, gender):
    if gender == 'male':
        if body_fat < 8:
            return "Essential Fat"
        elif 8 <= body_fat < 14:
            return "Athletes"
        elif 14 <= body_fat < 18:
            return "Fitness"
        elif 18 <= body_fat < 25:
            return "Average"
        else:
            return "Obese"
    else:  # female
        if body_fat < 21:
            return "Essential Fat"
        elif 21 <= body_fat < 25:
            return "Athletes"
        elif 25 <= body_fat < 31:
            return "Fitness"
        elif 31 <= body_fat < 38:
            return "Average"
        else:
            return "Obese"
#----------------------- Calculators end-----------------------#




if __name__ == '__main__':
    app.run(debug=True)    
