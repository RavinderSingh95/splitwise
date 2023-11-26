import uuid
from django.db import models


class BaseModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True)
    mobile_number = models.CharField(max_length=15, null=True)


class Expense(BaseModel):
        
    EXPENSE_TYPE_CHOICES = [
    ('EQUAL', 'Equal'),
    ('EXACT', 'Exact'),
    ('PERCENT', 'Percent'),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, null=True)
    payer = models.ForeignKey(User, on_delete=models.CASCADE)
    expenseType = models.CharField(max_length=10, choices=EXPENSE_TYPE_CHOICES)
    notes = models.TextField(null=True)
    images = models.JSONField(null=True)


class ExpenseParticipant(BaseModel):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    share = models.DecimalField(max_digits=10, decimal_places=2, null=True)