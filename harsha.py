from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/workdetails'
db = SQLAlchemy(app)

class WorkDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(255))
    date = db.Column(db.String(255))
    from_time = db.Column(db.String(255))
    to_time = db.Column(db.String(255))
    work_story = db.Column(db.Text)

@app.route('/')
def index():
    return render_template('workdiary1.html')

@app.route('/filter', methods=['POST'])
def filter_data():
    from_date = request.form['from_date']
    to_date = request.form['to_date']
    employee_id = request.form['employee_id']
    
    if employee_id == '':
        work_details = WorkDetail.query.filter(WorkDetail.date.between(from_date, to_date)).all()
    else:
        work_details = WorkDetail.query.filter(
            WorkDetail.date.between(from_date, to_date),
            WorkDetail.employee_id == employee_id
        ).all()
    
    return render_template('workdiary1.html', work_details=work_details)

if __name__ == '__main__':
    app.run(debug=True)
