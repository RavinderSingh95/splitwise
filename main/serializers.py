# serializers.py
from rest_framework import serializers
from .models import User, Expense, ExpenseParticipant

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ExpenseParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseParticipant
        fields = '__all__'

class ExpenseSerializer(serializers.ModelSerializer):
    share = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = '__all__'

    def get_share(self, instance):
        if ExpenseParticipant.objects.filter(user=instance.payer, expense=instance.uuid).exists():
            return ExpenseParticipant.objects.get(user=instance.payer, expense=instance.uuid).share
        else:
            return 0.00
