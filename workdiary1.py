from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name)

# Configure the MySQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/workdetails'
db = SQLAlchemy(app)

# Create a model for the workdetails table
class WorkDetail(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    employee_id = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(255), nullable=False)
    from_time = db.Column(db.String(255), nullable=False)
    to_time = db.Column(db.String(255), nullable=False)
    hours_worked = db.Column(db.String(255), nullable=False)
    reporting_to = db.Column(db.String(255), nullable=False)
    work_story = db.Column(db.Text, nullable=False)
    remember_token = db.Column(db.String(100))

# Route to display the work details
@app.route('/')
def work_details():
    work_details = WorkDetail.query.all()
    return render_template('workdiary1.html', work_details=work_details)

if __name__ == '__main__':
    app.run(debug=True)
