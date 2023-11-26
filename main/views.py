from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from main.models import Expense, ExpenseParticipant, User
from main.serializers import ExpenseSerializer, ExpenseParticipantSerializer, UserSerializer
from main.utils import send_expense_email


class UserPassbook(APIView):
    """This API takes user uuid as query param and returns user data and expenses"""
    def get(self, request, user_id):
        try:
            user_profile = User.objects.get(uuid=user_id)
            user_expenses = Expense.objects.filter(payer=user_profile)

            # Serialize data
            user_profile_serializer = UserSerializer(user_profile)
            user_expenses_serializer = ExpenseSerializer(user_expenses, many=True)

            return Response({
                'user_profile': user_profile_serializer.data,
                'user_expenses': user_expenses_serializer.data,
            })

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error":"Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
        

class UserBalances(APIView):

    def get(self, request, user_id):

        expense_data = {}
        
        expenses = Expense.objects.filter(payer=user_id).values_list('uuid', flat=True)
        for expense in expenses:
            expense_users = ExpenseParticipant.objects.filter(expense=expense).exclude(user=user_id).values('user', 'share')
            for expense_user in expense_users:
                expense_user['user'] = str(expense_user['user'])
                if expense_user['user'] in expense_data.keys():
                    expense_data[expense_user['user']] = expense_data[expense_user['user']] + expense_user['share']
                else:
                    expense_data[expense_user['user']] = expense_user['share']

        expenses = ExpenseParticipant.objects.filter(user=user_id).exclude(expense__payer=user_id).values('expense', 'share')
        for expense in expenses:
            payer = Expense.objects.get(uuid=expense['expense']).payer
            payer = str(payer.uuid)
            if payer in expense_data.keys():
                expense_data[payer] = expense_data[payer] - expense['share']
            else:
                expense_data[payer] = -expense['share']

        balances = []
        for user, share in expense_data.items():
            user_data = User.objects.values('uuid', 'name', 'email', 'mobile_number').get(uuid=user)
            user_data['share'] = share
            balances.append(user_data)

        return Response(balances, status=status.HTTP_200_OK)


class AddExpense(APIView):
    
    def post(self, request):

        data = request.data.copy()
        expense_type = data.get('expenseType', None).upper()

        if expense_type not in ['EQUAL', 'EXACT', 'PERCENT']:
            return Response({'error': 'Invalid expense type'}, status=status.HTTP_400_BAD_REQUEST)
        
        if data.get('amount') > 10000000:
            return Response({'error': 'maximum amount for an expense can go up to INR 1,00,00,000/-'}, status=status.HTTP_400_BAD_REQUEST)
        
        participants_data = data.get('participants', [])
        expense_data = []

        if len(participants_data) > 1000:
            return Response({'error': 'Exceeded the limit of 1000 participants.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ExpenseSerializer(data=data)
        
        with transaction.atomic():
            if serializer.is_valid(raise_exception=True):
                expense = serializer.save()
                expense_id = serializer.data.get('uuid')
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            if expense_type == 'EQUAL':
                share_amount = expense.amount / len(participants_data)
                
                for participant_data in participants_data:
                    expense_data.append(
                        {
                            "expense": expense_id,
                            "user": participant_data['uuid'],
                            "share": share_amount
                        }
                    )
                    
            elif expense_type == 'EXACT':
                total_exact_amount = sum(float(item['share']) for item in participants_data)
                if total_exact_amount != expense.amount:
                    return Response({'error': 'Total exact amounts do not match the expense amount'}, status=status.HTTP_400_BAD_REQUEST)
                
                for participant_data in participants_data:
                    expense_data.append(
                        {
                            "expense": expense_id,
                            "user": participant_data['uuid'],
                            "share": participant_data['share']
                        }
                    )
                    
            elif expense_type == 'PERCENT':
                total_percent = sum(float(item['share']) for item in participants_data)
                if total_percent != 100:
                    return Response({'error': 'Total percentage shares must be 100'}, status=status.HTTP_400_BAD_REQUEST)
                
                for participant_data in participants_data:
                    share_amount = expense.amount * Decimal(str(participant_data['share']/100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    share_amount = format(share_amount, '.2f')
                    expense_data.append(
                            {
                                "expense": expense_id,
                                "user": participant_data['uuid'],
                                "share": share_amount
                            }
                        )

            for expense_data_item in expense_data:

                serializer = ExpenseParticipantSerializer(data=expense_data_item)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    
                    #NOTE: Email part can run asynchronously and weekly reminder part can be sent we need to introduce celery
                    email = User.objects.get(uuid=expense_data_item['user']).email
                    send_expense_email(email, data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)