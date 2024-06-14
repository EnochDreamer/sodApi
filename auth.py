import json
from flask import request
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH_DOMAIN = 'enochdreamer.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'thrive'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    auth = request.headers['Authorization']
    print(auth)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split(' ')
    if parts[0].lower() != 'bearer':
        abort(401)

    elif len(parts) != 2:
        abort(401)


    token = parts[1]
    return token

'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
# def check_permissions(permission, payload):
#     if "permissions" not in payload:
#         abort(400)
#     if permission not in payload["permissions"]:
#         abort(403)
#     return True

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    print(token)
    payload={
        "email":"enochekele5@gmail.com"
    }
    return payload
    # jsonurl = urlopen(f'https://{AUTH_DOMAIN}/.well-known/jwks.json')
    # jwks = json.loads(jsonurl.read())
    # unverified_header = jwt.get_unverified_header(token)
    # rsa_key = {}
    # if 'kid' not in unverified_header:
    #     raise AuthError({
    #         'code': 'invalid_header',
    #         'description': 'Authorization malformed.'
    #     }, 401)

    # for key in jwks['keys']:
    #     if key['kid'] == unverified_header['kid']:
    #         rsa_key = {
    #             'kty': key['kty'],
    #             'kid': key['kid'],
    #             'use': key['use'],
    #             'n': key['n'],
    #             'e': key['e']
    #         }
    # if rsa_key:
    #     try:
    #         payload = jwt.decode(
    #             token,
    #             rsa_key,
    #             algorithms=ALGORITHMS,
    #             audience=API_AUDIENCE,
    #             issuer='https://' + AUTH_DOMAIN + '/'
    #         )

    #         return payload
    #     except:
    #         abort(401)
'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = get_token_auth_header()
        payload = verify_decode_jwt(token)
        #check_permissions(permission, payload)
        current_user_email=payload['email']
        return f(current_user_email, *args, **kwargs)

    return wrapper
    # @app.route('/coupon/<coupon>', methods=['GET'])
    # def process_coupon(coupon):
    #     current_user_email=request.args.get('email')
    #     coupon=Coupon.query.filter_by(coupon=str(coupon)).one_or_none()
    #     if coupon is None:
    #         return jsonify ({
    #             'success':False,
    #             'status':404,
    #             'message':'coupon not recognised'}),404
    #     if coupon.used:
    #         return jsonify ({
    #             'success':False,
    #             'status':422,
    #             'message':'coupon has been used'}),422
    #     current_user=Register.query.filter_by(user_email=current_user_email).one_or_none()
    #     if current_user is None:
    #         return jsonify ({
    #             'success':False,
    #             'status':404,
    #             'message':'user not found'}),404
    #     if not (current_user.registered):
    #         return jsonify ({
    #             'success':False,
    #             'status':422,
    #             'message':'user not registered'
    #             }),422


    #     # now get user and mark them paid
    #     current_user.paid=True
    #     current_user.make_matric_no()
    #     current_user.insert()
        
    #     coupon.used=True
    #     coupon.insert()
    #     return jsonify({
    #         "success":True,
    #         "coupon":coupon.format(),
    #         "data":current_user.format()
    #     })
    # @app.route('/register/verify_pay/<reference>/',methods=['GET'])
    # def verify_pay(reference):
    #     current_user_email=request.args.get('email')
    #     current_user=Register.query.filter_by(user_email=current_user_email).one_or_none()
    #     if current_user is None:
    #         return jsonify ({
    #             'success':False,
    #             'status':404,
    #             'message':'user not found'}),404
    #     if not (current_user.registered):
    #         return jsonify ({
    #             'success':False,
    #             'status':422,
    #             'message':'user not registered'
    #             }),422
    #     print(os.environ.get('PAYSTACK_SECRET'))
    #     url=f"https://api.paystack.co/transaction/verify/{reference}"
    #     headers = {
    #         'Authorization':os.environ.get('PAYSTACK_SECRET')
    #     }
    #     response = requests.get(
    #         url,
    #         headers=headers,
    #         timeout=30
    #     )
    #     print(response.json())
    #     res=response.json()['data']
    #     print(res)
    #     if not (res['status']=='success'):
    #         return jsonify ({
    #             'success':False,
    #             'status':422,
    #             'message':'could not verify transaction'}),422
    #     if not (int(res['amount'])==int(request.args.get('amount'))):
    #         return jsonify ({
    #             'success':False,
    #             'status':422,
    #             'message':'mismatch in amount to be paid'}),422
    #     current_user.paid=True
    #     current_user.make_matric_no()
    #     current_user.insert()
    #     return jsonify({
    #             'success':True,
    #             'status':200,
    #             'data':current_user.format()
    #         })