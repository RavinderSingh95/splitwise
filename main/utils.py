from django.core.mail import send_mail

def send_expense_email(recipient_email, expense_data):

    subject = 'Expense Split Notification'
    message = f'You have been added for splitting an expense. Amount: {expense_data["amount"]}, Description: {expense_data["description"]}'
    from_email = 'your@gmail.com'
    recipient_list = [recipient_email]

    send_mail(subject, message, from_email, recipient_list)
