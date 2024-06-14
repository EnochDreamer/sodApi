from flask import Flask ,jsonify,request, abort
from models import Register,Coupon,db_setup
from flask_cors import CORS
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
    CORS(app , resources={r"/*":{"origins":["http://localhost:5173","localhost:5173","https://fcs-sod-website.vercel.app/"]}})
    # Access control setups
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization, true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,POST,OPTIONS,DELETE,PUT"
        )
        response.headers.add(
            "Access-Control-Allow-Origin", "*"
        )
        return response


    def process_coupon(coupon,current_user):
        current_user_email=request.args.get('email')
        coupon=Coupon.query.filter_by(coupon=str(coupon)).one_or_none()
        if coupon is None:
            abort(404)
        if coupon.used:
            abort(422)
        # now get user and mark them paid
        current_user.registered=True
        current_user.paid=True
        current_user.insert()
        current_user.make_matric_no()
        current_user.insert()
        coupon.used=True
        coupon.insert()
        return True
       
    def verify_pay(reference,current_user):
        
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
            abort(422)
        if not (int(res['amount'])==int(request.args.get('amount'))):
            abort(422)
        current_user.paid=True
        current_user.registered=True
        current_user.insert()
        current_user.make_matric_no()
        current_user.insert()
        return True
        





    @app.route('/register',methods=['POST'])
    def register():
        current_user_email=request.args.get('email')
        #body=json.loads(request.form.get("data"))
        body=request.get_json()

        if ('image' or 'department' or 'user_name' or 'user_surname') not in body :
            return  jsonify ({
                'success':False,
                'status':422,
                'message':'missing a required field'}),422
        print(body)
        if ('coupon'  not in body) and ('reference' not in body):
            return  jsonify ({
                'success':False,
                'status':422,
                'message':'missing a coupon or reference'}),422
        already_exists=Register.query.filter_by(user_email=current_user_email).one_or_none()
        if already_exists:
            return jsonify({
                'success':False,
                'status':403,
                'message':'user already registered'
            }),403
        new_entry=Register(image=body['image'],user_name=body['user_name'],user_surname=body['user_surname'],user_email=current_user_email,department=body['department'])
        if 'coupon' in body:
            process_coupon(body['coupon'],new_entry)
        elif 'reference' in body:
            verify_pay(body['reference'],new_entry)

        return jsonify({
            'success':True,
            'status':200,
            'data':(Register.query.filter_by(user_email=current_user_email).one()).format()
            
        })

                
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

    @app.route('/user',methods=['GET'])
    def user():
        current_user_email=request.args.get('email')
        current_user=Register.query.filter_by(user_email=current_user_email).one_or_none()
        if current_user is None:
            return jsonify ({
                'success':False,
                'status':404,
                'message':'user not found'}),404

        return jsonify({
                'success':True,
                'status':200,
                'data':current_user.format()
            })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404
    
    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessible request,could be used coupon or invalid payment amount "
        }), 422


    return app