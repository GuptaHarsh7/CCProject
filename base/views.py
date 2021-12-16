from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsMember
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.serializers import Serializer
from .models import *
from .serializers import *
import stripe
import datetime
from rest_framework.views import APIView
import math
from rest_framework import status
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
User = get_user_model()

# Create your views here.

######################################################################

# Create your views here.

## ALL THE ROUTES THAT WE WILL NEED
@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/inventories/',
        '/api/inventory/<str:pk>/',
        '/api/inventory/<str:pk>/create/',
        '/api/inventory/<str:pk>/<str:id>/update/',
        '/api/inventory/<str:pk>/<str:id>/delete/',
        '/api/users/login/',
        '/api/users/profile/',
        '/api/users/profile/update/',
        '/api/users/register/',
        '/api/users/delete/',
    ]
    return Response(routes)

#######################################################################

## User related Requests view settings

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import make_password

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = UserSerializerWithToken(self.user).data

        for k, v in serializer.items():
            data[k] = v

        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    member = Membership.objects.get(user=user)
    user_serial = UserSerializer(user, many=False)
    memb_serial = MembershipSerializer(member, many=False)
    dict1 = user_serial.data
    dict2 = memb_serial.data
    dict1.update(dict2)
    print(dict1)
    return Response(dict1)

@api_view(['POST'])
def registerUser(request):

    data = request.data
    try:
        user = User.objects.create(
                first_name = data['first_name'],
                last_name = data['last_name'],
                username = data['username'],
                email = data['email'],
                password = make_password(data['password']),
                phone_No = data['phone_No'],
                profile_pic = request.FILES.get('profile_pic')
            )
        serializer = UserSerializerWithToken(user, many=False)
        return Response(serializer.data)
    except:
        message = {'detail':'User With this email already exists'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    serial = UserSerializerWithToken(user, many=False)

    data = request.data

    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.username = data['email']
    user.email = data['email']
    user.phone_No = data['phone_No']
    user.profile_pic = request.FILES.get('profile_pic')
    
    if data['password'] != "":
        user.password = make_password(data['password'])

    user.save()

    return Response(serial.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteUser(request):
    userForDeletion = User.objects.get(email=request.user.email)
    userForDeletion.delete()
    return Response('User was deleted')

#####################################################################

## Inventory Related Request view settings

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllInventory(request):
    user = request.user
    queryInventory = Inventory.objects.filter(user=user)
    serializer = InventorySerializer(queryInventory,many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getInventory(request,filter_key):
    user = request.user
    queryInventory = Inventory.objects.filter(user=user,filter_key=filter_key)
    serializer = InventorySerializer(queryInventory,many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createInventoryItem(request):
    user = request.user
    data = request.data

    item = Inventory.objects.create(
        user = user,
        image = request.FILES.get('image'),
        item_name = data["item_name"],
        timestamp = timezone.now(),
        filter_key = data["filter_key"]
    )
    print(item.image)

    serialize = InventorySerializer(item,many=False)
    return Response(serialize.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateInventoryItem(request,filter_key):
    user = request.user
    # cat = MainCategory.objects.get(_id = pk)
    queryItem  = Inventory.objects.get(user = user,filter_key=filter_key)
    serialize = InventorySerializer(queryItem,many=False)

    data = request.data

    queryItem.filter_key = data["filter_key"]
    queryItem.item_name = data["item_name"]
    queryItem.image = request.FILES.get('image')

    queryItem.save()

    return Response(serialize.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteInventoryItem(request,filter_key):
    user = request.user
    ItemDelete = Inventory.objects.get(filter_key=filter_key,user=user)
    ItemDelete.delete()
    return Response("Item Deleted")


################################################################################################################################################################

## Subscription views
STRIPE_PLAN_ID = "prod_KbJMjHZ3gMHO1Q"

stripe.api_key = "sk_test_51Ix7DoSDH8LbnqpkT3MyKegLDXZWeBvwsCdrX5HyLpcbLxWfxCBRkA0TF1JUb1kezcDIHc26TC7DLQhpk9yQPudT00zZIB8J8w"


@api_view(['POST'])
def confirm_payment_intent(request):
    data = request.data
    payment_intent_id = data['payment_intent_id']

    stripe.PaymentIntent.confirm(payment_intent_id)

    return Response(status=status.HTTP_200_OK, data={"message": "Success"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createPaymentMethod(request):
    user = request.user
    data = request.data
    payment_method = stripe.PaymentMethod.create(
        type = data["type"],
        card = {
            'exp_month':data["exp_month"],
            'exp_year':data["exp_year"],
            'number':data["number"],
            'cvc':data["cvc"]
        }
    )
    pmd = PaymentMethodDatabase.objects.create(
        user = user,
        payment_method_id = payment_method.id,
        amount = data["amount"]
    )
    serialize = PaymentMethodSerializer(pmd,many=False)
    return Response(serialize.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_stripe_info(request):

    user = request.user
    membership = user.membership
    name = user.get_full_name()
    print(name)
    # address = user.address

    data = request.data
    email = user.email
    payment_method = PaymentMethodDatabase.objects.get(user=user)
    payment_method_id = payment_method.payment_method_id
    extra_msg = ''
    # checking if customer with provided email already exists
    customer_data = stripe.Customer.list(email=email).data
    print(customer_data)

    if len(customer_data) == 0:
        # creating customer
        customer = stripe.Customer.create(
            email=email,
            name=name,
            payment_method=payment_method_id,
            invoice_settings={
                'default_payment_method': payment_method_id
            }
        )
        user.stripe_customer_id = customer.id
    else:
        customer = customer_data[0]
        extra_msg = "Customer already existed."

    ItemSubscription = stripe.Price.retrieve("price_1Jw6jKSDH8Lbnqpkzh2UBQdt")
    amount = ItemSubscription["unit_amount"]

    # creating paymentIntent

    stripe.PaymentIntent.create(customer=customer,
                                payment_method=payment_method_id,
                                currency='inr', amount=amount,
                                confirm=True)

    # creating subscription

    subscription = stripe.Subscription.create(
        customer=customer,
        items=[
            {
                'price': 'price_1Jw6jKSDH8Lbnqpkzh2UBQdt'
            }
        ]
    )

# update the membership
    membership.stripe_subscribe_id = subscription.id
    membership.user_type = "M"
    membership.start_date = datetime.datetime.now()
    membership.stripe_subscription_item_id = subscription["items"]["data"][0]["id"]
    membership.end_date = datetime.datetime.fromtimestamp(
        subscription.current_period_end)
    membership.save()

    # update the user
    user.is_member = True
    user.on_free_trial = False
    user.save()

    payment = Payment()
    payment.amount = subscription.plan.amount
    payment.user = user
    payment.save()

    return Response(status=status.HTTP_200_OK, data={'message': 'Success', 'data': {'customer_id': customer.id,
                                                                                    'extra_msg': extra_msg}})


class CancelSubscription(APIView):
    permission_classes = (IsMember, )

    def post(self, request, *args, **kwargs):
        user = request.user
        membership = user.membership

        try:
            stripe.Subscription.delete(membership.stripe_subscribe_id)

            user.is_member = False
            user.save()

            membership.type = "N"
            membership.save()
        except Exception as e:
            return Response({"message": "We apologize for the error. We have been informed and are working on the issue. "}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Your Subscription was cancelled."}, status=status.HTTP_200_OK)
