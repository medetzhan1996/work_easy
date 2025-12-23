import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType

from account.models import Company, Department, User
from customers.models import Customer
from products.models import Product, ProductCategory, Material, MaterialCategory
from orders.models import Order
from sales_funnel.models import Funnel, Card
from warehouse.models import Storage, Contractor
from dynamic_forms.models import FormField, FormFieldPermission
from accounting.models import PaymentMethod, PaymentMethodCommission


class Command(BaseCommand):
    help = "Populate database with test data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before populating",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            self.clear_data()

        self.stdout.write("Creating test data...")

        # Create companies
        companies = self.create_companies()
        self.stdout.write(self.style.SUCCESS(f"Created {len(companies)} companies"))

        # Create departments and users
        departments, users = self.create_departments_and_users(companies)
        self.stdout.write(self.style.SUCCESS(f"Created {len(departments)} departments"))
        self.stdout.write(self.style.SUCCESS(f"Created {len(users)} users"))

        # Create customers
        customers = self.create_customers(companies)
        self.stdout.write(self.style.SUCCESS(f"Created {len(customers)} customers"))

        # Create product categories and products
        product_categories = self.create_product_categories(companies)
        products = self.create_products(companies)
        self.stdout.write(self.style.SUCCESS(f"Created {len(products)} products"))

        # Create material categories and materials
        material_categories = self.create_material_categories(companies)
        materials = self.create_materials(material_categories)
        self.stdout.write(self.style.SUCCESS(f"Created {len(materials)} materials"))

        # Create storages
        storages = self.create_storages(companies)
        self.stdout.write(self.style.SUCCESS(f"Created {len(storages)} storages"))

        # Create contractors
        contractors = self.create_contractors(companies)
        self.stdout.write(self.style.SUCCESS(f"Created {len(contractors)} contractors"))

        # Create payment methods
        payment_methods = self.create_payment_methods(companies)
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(payment_methods)} payment methods")
        )

        # Create form fields
        form_fields = self.create_form_fields(companies)
        self.stdout.write(self.style.SUCCESS(f"Created {len(form_fields)} form fields"))

        # Create orders
        orders = self.create_orders(users, customers, products)
        self.stdout.write(self.style.SUCCESS(f"Created {len(orders)} orders"))

        # Create funnels and cards
        funnels = self.create_funnels(companies)
        cards = self.create_cards(funnels, customers, users)
        self.stdout.write(self.style.SUCCESS(f"Created {len(cards)} funnel cards"))

        self.stdout.write(
            self.style.SUCCESS("Successfully populated database with test data!")
        )

    def clear_data(self):
        """Clear existing test data"""
        Order.objects.all().delete()
        Card.objects.all().delete()
        Funnel.objects.all().delete()
        FormFieldPermission.objects.all().delete()
        FormField.objects.all().delete()
        PaymentMethodCommission.objects.all().delete()
        PaymentMethod.objects.all().delete()
        Customer.objects.all().delete()
        Product.objects.all().delete()
        ProductCategory.objects.all().delete()
        Material.objects.all().delete()
        MaterialCategory.objects.all().delete()
        Storage.objects.all().delete()
        Contractor.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Department.objects.all().delete()
        Company.objects.all().delete()

    def create_companies(self):
        """Create test companies"""
        companies = []
        company_names = [
            "Tech Solutions Ltd",
            "Beauty Studio Premium",
            "Construction Group",
        ]

        for name in company_names:
            company = Company.objects.create(
                title=name,
                phone_number=f"+7777{random.randint(1000000, 9999999)}",
                address=f"Address for {name}",
                slug=slugify(name),
            )
            companies.append(company)

        return companies

    def create_departments_and_users(self, companies):
        """Create departments and users for each company"""
        from constants import OWNER, MASTER, SALES, MANAGER

        departments = []
        users = []

        department_names = ["Sales", "Production", "Management"]

        for company in companies:
            # Create departments
            for dept_name in department_names:
                dept = Department.objects.create(title=dept_name, company=company)
                departments.append(dept)

            # Create owner
            owner = User.objects.create_user(
                username=f"owner_{company.slug}",
                email=f"owner@{company.slug}.com",
                password="testpass123",
                first_name="Owner",
                last_name=company.title.split()[0],
                company=company,
                user_type=OWNER,
            )
            users.append(owner)

            # Create masters
            for i in range(2):
                master = User.objects.create_user(
                    username=f"master_{i + 1}_{company.slug}",
                    email=f"master{i + 1}@{company.slug}.com",
                    password="testpass123",
                    first_name=f"Master{i + 1}",
                    last_name=company.title.split()[0],
                    company=company,
                    department=departments[1],  # Production department
                    user_type=MASTER,
                )
                users.append(master)

            # Create salesmen
            for i in range(2):
                sales = User.objects.create_user(
                    username=f"sales_{i + 1}_{company.slug}",
                    email=f"sales{i + 1}@{company.slug}.com",
                    password="testpass123",
                    first_name=f"Sales{i + 1}",
                    last_name=company.title.split()[0],
                    company=company,
                    department=departments[0],  # Sales department
                    user_type=SALES,
                )
                users.append(sales)

        return departments, users

    def create_customers(self, companies):
        """Create test customers"""
        customers = []
        first_names = ["John", "Jane", "Bob", "Alice", "Mike", "Sarah", "Tom", "Emma"]
        last_names = [
            "Smith",
            "Johnson",
            "Williams",
            "Brown",
            "Jones",
            "Garcia",
            "Miller",
            "Davis",
        ]

        for company in companies:
            for _ in range(10):
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                customer = Customer.objects.create(
                    full_name=f"{first_name} {last_name}",
                    phone_number=f"+7777{random.randint(1000000, 9999999)}",
                    social_account=f"@{first_name.lower()}{last_name.lower()}",
                    company=company,
                )
                customers.append(customer)

        return customers

    def create_product_categories(self, companies):
        """Create product categories"""
        categories = []
        category_names = [
            "Premium Services",
            "Standard Services",
            "Basic Services",
            "VIP Package",
        ]

        for company in companies:
            for name in category_names[:2]:  # Create 2 categories per company
                category = ProductCategory.objects.create(
                    title=name,
                    company=company,
                    comment=f"Category description for {name}",
                )
                categories.append(category)

        return categories

    def create_products(self, companies):
        """Create test products"""
        products = []
        product_names = [
            "Basic Service Package",
            "Premium Service Package",
            "Deluxe Service Package",
            "VIP Service Package",
            "Standard Consultation",
            "Extended Consultation",
        ]

        for company in companies:
            for name in product_names[:4]:  # Create 4 products per company
                product = Product.objects.create(
                    title=name,
                    price=Decimal(random.randint(5000, 50000)),
                    actual_price=Decimal(random.randint(3000, 40000)),
                    company=company,
                    comment=f"Description for {name}",
                )
                products.append(product)

        return products

    def create_material_categories(self, companies):
        """Create material categories"""
        categories = []
        category_names = ["Raw Materials", "Consumables", "Tools", "Equipment"]

        for company in companies:
            for name in category_names[:2]:  # Create 2 categories per company
                category = MaterialCategory.objects.create(
                    title=name, company=company, comment=f"Material category: {name}"
                )
                categories.append(category)

        return categories

    def create_materials(self, material_categories):
        """Create test materials"""
        materials = []
        material_names = [
            "Material A",
            "Material B",
            "Material C",
            "Consumable X",
            "Consumable Y",
            "Consumable Z",
        ]

        for category in material_categories:
            for name in material_names[:3]:  # Create 3 materials per category
                material = Material.objects.create(
                    title=name,
                    category=category,
                    barcode=f"BAR{random.randint(100000, 999999)}",
                    sale_unit=random.choice([1, 2, 3, 4]),
                    write_off_unit=random.choice([1, 2, 3, 4]),
                    unit_equals=random.randint(1, 10),
                    price=Decimal(random.randint(100, 5000)),
                    actual_price=Decimal(random.randint(80, 4500)),
                    critical_amount=random.randint(5, 20),
                    desired_amount=random.randint(50, 200),
                    comment=f"Material: {name}",
                )
                materials.append(material)

        return materials

    def create_storages(self, companies):
        """Create test storages"""
        storages = []
        storage_names = ["Main Storage", "Secondary Storage", "Reserve Storage"]

        for company in companies:
            for name in storage_names[:2]:  # Create 2 storages per company
                storage = Storage.objects.create(title=name, company=company)
                storages.append(storage)

        return storages

    def create_contractors(self, companies):
        """Create test contractors"""
        contractors = []
        contractor_names = [
            "Supplier A",
            "Supplier B",
            "Partner Company",
            "Wholesale Distributor",
        ]

        for company in companies:
            for name in contractor_names[:2]:  # Create 2 contractors per company
                contractor = Contractor.objects.create(title=name, company=company)
                contractors.append(contractor)

        return contractors

    def create_orders(self, users, customers, products):
        """Create test orders"""
        orders = []

        # Filter users who can create orders (masters and sales)
        from constants import MASTER, SALES

        order_users = [u for u in users if u.user_type in [MASTER, SALES]]

        for _ in range(30):  # Create 30 orders
            user = random.choice(order_users)
            # Get customers from the same company
            company_customers = [c for c in customers if c.company == user.company]
            # Get products from the same company
            company_products = [p for p in products if p.company == user.company]

            if not company_customers or not company_products:
                continue

            customer = random.choice(company_customers)
            product = random.choice(company_products)

            # Get masters and salesmen from same company
            company_masters = [
                u for u in users if u.company == user.company and u.user_type == MASTER
            ]
            company_sales = [
                u for u in users if u.company == user.company and u.user_type == SALES
            ]

            order = Order.objects.create(
                customer=customer,
                salesman=random.choice(company_sales) if company_sales else None,
                product=product,
                price=product.price or Decimal("10000"),
                deadline=datetime.now().date() + timedelta(days=random.randint(1, 30)),
                user=user,
                master=random.choice(company_masters) if company_masters else None,
                extra_data="{}",
            )
            orders.append(order)

        return orders

    def create_payment_methods(self, companies):
        """Create payment methods"""
        payment_methods = []
        method_names = [
            ("Cash", "Наличные", 0),
            ("Card", "Карта", 2),
            ("Bank Transfer", "Банковский перевод", 1.5),
            ("Online Payment", "Онлайн оплата", 3),
        ]

        for company in companies:
            for name, title, commission in method_names[
                :3
            ]:  # Create 3 payment methods per company
                payment_method = PaymentMethod.objects.create(
                    title=title, company=company, commission=Decimal(commission)
                )
                payment_methods.append(payment_method)

                # Create payment method commission history
                PaymentMethodCommission.objects.create(
                    payment_method=payment_method,
                    commission=float(commission),
                    company=company,
                    date=datetime.now().date(),
                )

        return payment_methods

    def create_form_fields(self, companies):
        """Create form fields for orders"""
        from constants import (
            TEXT,
            NUMBER,
            DATE,
            SELECT,
            OWNER,
            MASTER,
            SALES,
            MANAGER,
            FULL,
        )

        form_fields = []
        order_ct = ContentType.objects.get_for_model(Order)

        field_definitions = [
            ("customer_name", "Customer Name", TEXT, False),
            ("order_notes", "Order Notes", TEXT, False),
            ("quantity", "Quantity", NUMBER, False),
            ("discount", "Discount %", NUMBER, False),
            ("delivery_date", "Delivery Date", DATE, False),
        ]

        # User types that should have access to form fields
        user_types = [OWNER, MASTER, SALES, MANAGER]

        for company in companies:
            for i, (name, label, field_type, required) in enumerate(
                field_definitions[:3]
            ):  # Create 3 fields per company
                # Make field name unique per company
                unique_name = f"{name}_{company.slug}"

                form_field = FormField.objects.create(
                    label=label,
                    name=unique_name,
                    field_type=field_type,
                    content_type=order_ct,
                    company=company,
                    is_required=required,
                    sorting=i,
                )
                form_fields.append(form_field)

                # Create FormFieldPermission for each user type
                for user_type in user_types:
                    FormFieldPermission.objects.create(
                        form_field=form_field,
                        user_type=user_type,
                        permission=FULL,
                        sorting=i,
                    )

        return form_fields

    def create_funnels(self, companies):
        """Create sales funnels"""
        funnels = []
        funnel_names = [
            "New Leads",
            "In Progress",
            "Negotiation",
            "Closed Won",
            "Closed Lost",
        ]

        for company in companies:
            for i, name in enumerate(funnel_names):
                funnel = Funnel.objects.create(title=name, company=company, sorting=i)
                funnels.append(funnel)

        return funnels

    def create_cards(self, funnels, customers, users):
        """Create funnel cards"""
        cards = []

        for _ in range(50):  # Create 50 cards
            funnel = random.choice(funnels)
            # Get customers from the same company
            company_customers = [c for c in customers if c.company == funnel.company]
            # Get users from the same company
            company_users = [u for u in users if u.company == funnel.company]

            if not company_customers or not company_users:
                continue

            customer = random.choice(company_customers)
            user = random.choice(company_users)

            card = Card.objects.create(
                funnel=funnel,
                customer=customer,
                comment=f"Follow up with customer about their interest",
                user=user,
                notification_date=datetime.now().date()
                + timedelta(days=random.randint(1, 14)),
            )
            cards.append(card)

        return cards
