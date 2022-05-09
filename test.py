
from asyncio.windows_events import NULL
from contextlib import nullcontext
from distutils.log import error
import email
from unicodedata import name
from unittest import result
from flask import Flask, jsonify, redirect, render_template, request, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import null

app = Flask(__name__)
app.secret_key = "hello"

app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:741222@localhost/covid_hospital'

db = SQLAlchemy(app)

# ------------Models------------

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    sits = db.Column(db.Integer, nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Paitent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    h_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    u_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(10), nullable=False)

#-----------------------x------------------------


# ------------Login------------


@app.route('/')
def index():
    return render_template('loging.html')

#-----------------------x------------------------


# ------------Existance Checking------------
def exist(email, password):

    email_exist = Users.query.filter_by(email=email).first()
    if not email_exist:
        return False
    else:
        real_password = email_exist.password
        if (real_password == password):
            return True
        else:
            flash("Incorrect pass")
            return False

#-----------------------x------------------------


# ------------Register------------

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register',methods=["POST"])
def succ():

    names = request.form.get("name")
    emails = request.form.get("email")
    passwords = request.form.get("pass")
    print(names)
    print(emails)
    print(passwords)

    entry = Users(fname=names, email = emails, password=passwords)
    db.session.add(entry)
    db.session.commit()

    return render_template("loging.html")

#-----------------------x------------------------


user_id = NULL

# ------------Back to dashbord------------

@app.route('/back_dashbord')
def back_to_dashbord():
    us_name = session["user"]
    hospital_list = db.session.query(Hospital.name, Hospital.sits).all()
    return render_template("dashbord.html",us_name = us_name, hospital_list = hospital_list)

#-----------------------x------------------------

# ------------Login in Dashbord------------

@app.route('/dashbord', methods=['POST'])
def dashbord():
    log_email = request.form.get("log_email")
    log_pass = request.form.get("log_pass")
    if not log_email or not log_pass:
        flash("Please Fillup all fields")
        return render_template("loging.html")
    else:
        result = exist(log_email, log_pass)
        if (result == False):
            flash("Invalid Email & Password")
            return redirect("/")
        else:
            user_email = Users.query.filter_by(email=log_email).first()
            global user_id
            user_id = user_email.id
            us_name = user_email.fname
            session["user"] = us_name
            hospital_list = db.session.query(Hospital.name, Hospital.sits).all()
            return render_template("dashbord.html", us_name=us_name, hospital_list=hospital_list)

#-----------------------x------------------------

# ------------Hospital Added------------
@app.route('/add_success', methods=['POST'])
def add_success():
    id = Users.query.filter_by()
    hospital_name = request.form.get("hospital_name")
    avl_bed = request.form.get("avl_beds")
    if not hospital_name or not avl_bed:
        flash("Please Fill all Fields")
        return render_template("dashbord.html")
    else:
        entry = Hospital(name=hospital_name, sits = avl_bed, hospital_id = user_id)
        db.session.add(entry)
        db.session.commit()
        flash("Added Successfull")
        return redirect("/back_dashbord")
    
#-----------------------x------------------------


# ------------Display Hospital---------------

@app.route('/visit_hospital')
def visit_hospital():
    result = db.session.query(Hospital.name, Hospital.sits, Hospital.id).filter(Hospital.hospital_id == user_id)
    
    return render_template('visit_hospital.html', data=result)

#-----------------------x------------------------


# -----------Delete Hospital---------------

@app.route('/delete')
def delete():
        flash("Hospital can not be Deleted")
        return redirect('/visit_hospital')

#-----------------------x------------------------

hospita_update_id = null

# -----------Update Hospital---------------

@app.route('/update_hospital/<int:id>')
def update_hospital(id):
    global hospita_update_id
    hospita_update_id = id
    data = db.session.query(Hospital.name, Hospital.sits).filter(Hospital.id == id)
    return render_template('updateHospital.html', data = data)

@app.route('/hospital_uptodate', methods=['POST'])
def hospital_uptodate():
    global hospita_update_id
    id = hospita_update_id
    print(id)
    hospital_name = request.form.get("new_name")
    avl_bed = request.form.get("new_beds")
    if not hospital_name or not avl_bed:
        flash("Please Fill all Fields")
        return render_template("dashbord.html")
    else:
        data = Hospital.query.filter_by(id = id).first()
        data.name = hospital_name
        data.sits = avl_bed
        db.session.commit()
        return redirect('/visit_hospital')

#-----------------------x------------------------


# -----------Add Paitent--------------

@app.route('/paitent_add', methods=['POST'])
def paitent_add():
    paitent_name = request.form.get("paitent_name")
    age = request.form.get("age")
    ph_number = request.form.get("ph_number")
    paitent_hospital = str(request.form.get("paitent_hospital"))
    head, sep, tail = paitent_hospital.partition(' ')
    if not paitent_name or not age or not ph_number or not paitent_hospital:
        flash("Please Fill all Fields")
        return render_template("dashbord.html")
    else:

        hospital_details = Hospital.query.filter_by(name=head).first()
        h_id = hospital_details.id

        entry = Paitent(h_id = h_id, u_id = user_id, name = paitent_name, age = age, phone = ph_number)
        db.session.add(entry)
        db.session.commit()
        flash("Added Successfull")
        return redirect('/back_dashbord')

#-----------------------x------------------------


# -----------Visit Paitent--------------

@app.route('/visit_paitent')
def visit_paitent():

    result = db.session.query(Hospital, Paitent).join(Paitent).all()
    for hospital, paitent in result:
        print(hospital.name, paitent.name)
    
    return render_template('visit_paitent.html', result = result)

#-----------------------x------------------------


# -----------Delete Paitent--------------

@app.route('/delete_paitent/<int:id>')
def delete_paitent(id):
    obj = Paitent.query.filter_by(id=id).one()
    db.session.delete(obj)
    db.session.commit()
    return redirect('/visit_paitent')

#-----------------------x------------------------


# -----------Edite Paitent--------------
paitent_update_id = null
@app.route('/edite_paitent/<int:id>')
def edite_paitent(id):
    global paitent_update_id
    paitent_update_id = id
    data = db.session.query(Paitent.name, Paitent.age, Paitent.phone).filter(Paitent.id == id)
    return render_template('updatePaitent.html', data = data)

@app.route('/paitent_uptodate', methods=['POST'])
def paitent_uptodate():
    global paitent_update_id
    id = paitent_update_id
    paitent_name = request.form.get("paitent_name")
    age = request.form.get("age")
    ph_number = request.form.get("ph_number")
    if not paitent_name or not age or not ph_number:
        flash("Please Fill all Fields")
        return render_template("dashbord.html")
    else:
        obj = Paitent.query.filter_by(id=id).one()
        obj.name = paitent_name
        obj.age = age
        obj.phone = ph_number
        db.session.commit()
        return redirect('/visit_paitent')

#-----------------------x------------------------

if __name__ == '__main__':
    app.run(debug=True)
