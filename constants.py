from decimal import Decimal

ADMINISTRATOR = 1
GENERAL_MANAGER = 2
MANAGER = 3
LOGISTIC = 4
MASTER = 5
ACCOUNTANT = 6
OWNER = 7
SUPERVISOR_PRODUCTION = 8
DESIGNER = 9
ACCOUNTANT_SALES = 10
SALES = 11
USER_TYPE_CHOICES = (
    (ADMINISTRATOR, 'Администратор'),
    (GENERAL_MANAGER, 'Главный менеджер'),
    (MANAGER, 'Менеджер'),
    (LOGISTIC, 'Логистика'),
    (MASTER, 'Мастер'),
    (ACCOUNTANT, 'Бухгалтер'),
    (ACCOUNTANT_SALES, 'Бухгалтер оптавиков'),
    (OWNER, 'Владелец'),
    (SUPERVISOR_PRODUCTION, 'Супервайзер производства'),
    (DESIGNER, 'Дизайнер'),
    (SALES, 'Оптовик'),
)

TEXT = 'text'
TEXTAREA = 'textarea'
SELECT = 'select'
NUMBER = 'number'
DATALIST = 'datalist'
CHECKBOX = 'checkbox'
RADIO = 'radio'
DATE = 'date'
SURCHARGE = 'surcharge'
BANK = "bank"
ACCEPTING_PAYMENT = 'accepting_payment'
DISCOUNT = 'discount'
REMAINDER = 'remainder'
RECEIPT_AMOUNT = 'receipt_amount'
DISCOUNTED_AMOUNT = 'discounted_amount'
TOTAL_PAYMENT = 'total_payment'
PAYMENT_METHOD = 'payment_method'
PAYMENT_CONFIRMATION = 'payment_confirmation'
INLINE_FIELD = 'inline_field'
MATERIAL_BY_CATEGORY = 'material_by_category'
PAYMENT_AFTER_COMMISSION = 'payment_after_commission'
DELIVERY_CONSUMPTION = 'delivery_consumption'
CONSUMPTION = 'consumption'
SALESMAN = 'salesman'


FIELD_TYPE_CHOICES = (
    (TEXT, "Ввод текста"),
    (NUMBER, 'Число'),
    (TEXTAREA, "textarea"),
    (SELECT, "select"),
    (DATALIST, 'datalist'),
    (CHECKBOX, 'checkbox'),
    (RADIO, 'radio'),
    (INLINE_FIELD, 'Встроенное поле'),
    (DATE, 'Дата'),
    (ACCEPTING_PAYMENT, 'Принятие оплаты'),
    (PAYMENT_AFTER_COMMISSION, 'Сумма после комиссии'),
    (PAYMENT_METHOD, 'Способ оплаты'),
    (PAYMENT_CONFIRMATION, 'Подтверждение оплаты'),
    (SURCHARGE, 'Доплата'),
    (DISCOUNT, 'Скидка'),
    (DISCOUNTED_AMOUNT, 'Сумма со скидкой'),
    (TOTAL_PAYMENT, 'Общая сумма к оплате'),
    (REMAINDER, 'Остаток оплаты'),
    (BANK, "Банк"),
    (MATERIAL_BY_CATEGORY, "Материал по категориям"),
    (RECEIPT_AMOUNT, "Сумма поступления"),
    (DELIVERY_CONSUMPTION, "Расходы доставки"),
    (SALESMAN, "Оптовики")
)


SALARY_NO_PREMIUM = 'salary'
SALARY_FIXED_PREMIUM = 'salary_fixed_premium'
SALARY_PERCENTAGE_PREMIUM = 'salary_percentage_premium'
PERCENTAGE = 'percentage'

SALARY_TYPE_CHOICES = (
    (SALARY_NO_PREMIUM, 'Оклад'),
    (SALARY_FIXED_PREMIUM, 'Оклад + фиксированная надбавка'),
    (SALARY_PERCENTAGE_PREMIUM, 'Оклад + процентная надбавка'),
    (PERCENTAGE, 'Процентная оплата'),
)

FIXED_BONUS = 'fixed'
PERCENTAGE_BONUS = 'percentage'

BONUS_TYPE_CHOICES = (
    (FIXED_BONUS, 'Фиксированный бонус'),
    (PERCENTAGE_BONUS, 'Процентный бонус'),
)

FULL = 'full'
READ_ONLY = 'read_only'
PERMISSION_CHOICES = (
    (FULL, 'Полный доступ'),
    (READ_ONLY, 'Только чтение'),
)

DISCOUNT_PERCENT = Decimal('0.01')

PERIOD_CHOICES = (
    ('year', 'На год'),
    ('month', 'За месяц'),
    ('range', 'За период'),
)
