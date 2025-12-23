from accounting.models import TransactionDetail


def create_transaction_detail(data):
    try:
        TransactionDetail.objects.create(**data)
    except Exception as e:
        print(f'Failed to create TransactionDetail: {e}')