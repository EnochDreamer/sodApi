from flask import Flask ,jsonify,request, abort
from models import Register,Coupon,db_setup
from flask_cors import CORS
from auth import requires_auth
from urllib.request import urlopen
import dotenv
import os
import random
import json
import requests

def create_app(test_config=None):
    app=Flask(__name__)
    db_setup(app)

    # enables CORS for any origin with the specified URI 
    CORS(app , resources={r"\*/\*":{"origins":["http://localhost:5173","localhost:5173","https://fcs-sod-website.vercel.app/"]}})
    # Access control setups
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization, true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,POST,OPTIONS,DELETE,PUT"
        )
        # response.headers.add(
        #     "Access-Control-Allow-Origin", "*"
        # )
        return response


    @app.route('/register',methods=['POST'])
    def register():
        current_user_email=request.args.get('email')
        body=json.loads(request.form.get("data"))
        if ('user_email' or 'department' or 'user_name' or 'user_surname') not in body :
            return  jsonify ({
                'success':False,
                'status':422,
                'error':'missing a required field'}),422
        new_entry=Register(user_name=body['user_name'],user_surname=body['user_surname'],user_email=current_user_email,department=body['department'])
        #new_entry.make_matric_no()
        if request.files.get('image') is None:
            return  jsonify ({
                'success':False,
                'status':400,
                'error':'missing a required field'}),422
        new_entry.save_image(request.files.get('image'))
        new_entry.registered=True
        try:
            new_entry.insert()
            return jsonify({
                'success':True,
                'status':200,
                'data':new_entry.format()
            })
        except Exception as e:
            return jsonify ({
                'success':False,
                'status':422,
                'error':str(e)}),422
                
    @app.route('/coupon/make/<int:x>',methods=['GET'])
    def make_coupon(x):
        coupons=[]
        count=0
        while count<x:
            coupon=random.randint(1000000000,9999999999)
            tank=[instance.coupon for instance in (Coupon.query.all())]
            while coupon in tank:
                coupon=random.randint(1000000000,9999999999)
            entry=Coupon(coupon=coupon)
            entry.insert()
            coupons.append(coupon)
            count+=1
        return jsonify({

            "success":True,
            "coupon":coupons
        })

    @app.route('/coupon/<coupon>', methods=['GET'])
    def process_coupon(coupon):
        current_user_email=request.args.get('email')
        coupon=Coupon.query.filter_by(coupon=str(coupon)).one_or_none()
        if coupon is None:
            return jsonify ({
                'success':False,
                'status':404,
                'error':'coupon not recognised'}),404
        if coupon.used:
            return jsonify ({
                'success':False,
                'status':422,
                'error':'coupon has been used'}),422
        current_user=Register.query.filter_by(user_email=current_user_email).one_or_none()
        if current_user is None:
            return jsonify ({
                'success':False,
                'status':404,
                'error':'user not found'}),404
        if not (current_user.registered):
            return jsonify ({
                'success':False,
                'status':422,
                'error':'user not registered'
                }),422


        # now get user and mark them paid
        current_user.paid=True
        current_user.make_matric_no()
        current_user.insert()
        
        coupon.used=True
        coupon.insert()
        return jsonify({
            "success":True,
            "coupon":coupon.format(),
            "data":current_user.format()
        })

            
    
    @app.route('/register/verify_pay/<reference>/',methods=['GET'])
    def verify_pay(reference):
        current_user_email=request.args.get('email')
        current_user=Register.query.filter_by(user_email=current_user_email).one_or_none()
        if current_user is None:
            return jsonify ({
                'success':False,
                'status':404,
                'error':'user not found'}),404
        if not (current_user.registered):
            return jsonify ({
                'success':False,
                'status':422,
                'error':'user not registered'
                }),422
        print(os.environ.get('PAYSTACK_SECRET'))
        url=f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            'Authorization':os.environ.get('PAYSTACK_SECRET')
        }
        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )
        print(response.json())
        res=response.json()['data']
        print(res)
        if not (res['status']=='success'):
            return jsonify ({
                'success':False,
                'status':422,
                'error':'could not verify transaction'}),422
        if not (int(res['amount'])==int(request.args.get('amount'))):
            return jsonify ({
                'success':False,
                'status':422,
                'error':'mismatch in amount to be paid'}),422
        current_user.paid=True
        current_user.make_matric_no()
        current_user.insert()
        return jsonify({
                'success':True,
                'status':200,
                'data':current_user.format()
            })

    @app.route('/user',methods=['GET'])
    def user():
        current_user_email=request.args.get('email')
        current_user=Register.query.filter_by(user_email=current_user_email).one_or_none()
        if current_user is None:
            return jsonify ({
                'success':False,
                'status':404,
                'error':'user not found'}),404

        return jsonify({
                'success':True,
                'status':200,
                'data':current_user.format()
            })

    return app