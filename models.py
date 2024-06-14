from flask_sqlalchemy import SQLAlchemy
import os
import cloudinary
from cloudinary.uploader import upload
import dotenv
from flask import jsonify
from datetime import datetime


cloudinary.config(
  cloud_name=os.environ.get('cloud_name'),
  api_key=os.environ.get('api_key'),
  api_secret=os.environ.get('api_secret')
)

db_host=os.environ.get('RDS_HOSTNAME')
db=os.environ.get('RDS_DB_NAME')
db_username=os.environ.get('RDS_USERNAME')
db_password=os.environ.get('RDS_PASSWORD')


database_path=f'postgresql://{db_username}:{db_password}@{db_host}/{db}'
db=SQLAlchemy()
def db_setup(app,database_path=database_path,db=db):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"]="hello world"
    db.app = app
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app


class Register(db.Model):
    __tablename__='register'
    id=db.Column(db.Integer,primary_key=True)
    user_name=db.Column(db.String(30),nullable=False)
    user_surname=db.Column(db.String(30),nullable=False)
    user_email=db.Column(db.String(30),nullable=False,unique=True)
    department=db.Column(db.String(),nullable=False, default='a-DOE')
    registered=db.Column(db.Boolean,nullable=False,default=False)
    paid=db.Column(db.Boolean,nullable=False, default=False)
    matric_no=db.Column(db.String(), nullable=False, default='')
    image=db.Column(db.String(),default='')
    def insert(self):
        try:
            print("insert ran")
            db.session.add(self)
            db.session.commit()
            print("insert ran")
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success":False,
                "message":str(e)
            }),500
    def make_matric_no(self):
        _matric_no=f'SOD24/1/0{self.id}'
        print(f'{_matric_no}{(((self.department).split("-")[1]).upper())}')
        self.matric_no=f'{_matric_no}{(((self.department).split("-")[1]).upper())}'
    def format(self):
        return(
            {
                "id":self.id,
                "firstname":self.user_name,
                "surname":self.user_surname,
                "email":self.user_email,
                "image":self.image,
                "matric_no":self.matric_no,
                "department":self.department,
                "is_registered":self.registered,
                "paid":self.paid
            })
    def save_image(self, file):
        """Saves an image from `request.files`"""
        # _, fmt = os.path.splitext(file.filename)
        # newFileName = str(uuid4()).replace('-', '') + fmt
        # os.makedirs(os.path.join('static', 'img', 'profile_pics'), exist_ok=True)
        # path = os.path.join("static", "img", "profile_pics", newFileName)
        # print(path)
        # file.save(path)
        upload_result = upload(file)
        image_url = upload_result['secure_url']
        self.image = image_url


class Coupon(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    used=db.Column(db.Boolean, default=False , nullable=False)
    coupon=db.Column(db.String(),unique=True)
    #created_at=db.Column(db.DateTime , default=datetime.now())
    def format(self):
        return({
            "id":self.id,
            "used":self.used,
            "coupon":self.coupon
                })

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            return jsonify({
                "success":False,
                "message":str(e)
            }),500
        
