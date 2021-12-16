from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id','username','email','profile_pic','first_name','last_name','phone_No' ]

class UserSerializerWithToken(serializers.ModelSerializer):

    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username','email','profile_pic','first_name','last_name','phone_No','token' ]

    def get_token(self,obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

class InventorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Inventory
        fields = "__all__"

class MembershipSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Membership
        fields = "__all__"

class PaymentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Payment
        fields = "__all__"

class PaymentMethodSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PaymentMethodDatabase
        fields = "__all__"