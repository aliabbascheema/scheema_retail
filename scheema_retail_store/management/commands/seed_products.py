import json
import random
from django.core.management.base import BaseCommand
from scheema_retail_store.models import Product, Category, Review
from configs.json_configs import load_json_data
import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker


class Command(BaseCommand):
    help = "Seed product data from a JSON file into the database and generate fake users and reviews."

    def handle(self, *args, **kwargs):
        fake = Faker()

        json_file_path = 'products.json'

        users_csv_file = 'generated_users.csv'
        reviews_csv_file = 'generated_reviews.csv'

        with open(users_csv_file, mode='w', newline='', encoding='utf-8') as users_csv, \
                open(reviews_csv_file, mode='w', newline='', encoding='utf-8') as reviews_csv:

            users_writer = csv.writer(users_csv)
            reviews_writer = csv.writer(reviews_csv)

            users_writer.writerow(['Username', 'Email', 'Password'])
            reviews_writer.writerow(
                ['Username', 'Product', 'Rating', 'Comment'])

            try:
                products_data = load_json_data(json_file_path)
                created_users = []

                for product_data in products_data:
                    category_name = product_data["category"]
                    category, created = Category.objects.get_or_create(
                        name=category_name)

                    product_instance = Product.objects.create(
                        name=product_data["title"],
                        slug=product_data["slug"],
                        sku=product_data["sku"],
                        description=product_data["description"],
                        price=product_data["price"],
                        category=category,
                        image=product_data["image"],
                        stock=product_data["stock"],
                        features=product_data["specifications"],
                        images=product_data["images"],
                    )

                    user = User.objects.create_user(
                        username=fake.user_name(),
                        email=fake.email(),
                        password=fake.password(),
                    )
                    users_writer.writerow(
                        [user.username, user.email, user.password])
                    created_users.append(user)

                    generated_reviews = []

                    for _ in range(fake.random_int(1, 5)):
                        review = Review.objects.create(
                            user=random.choice(created_users),
                            product=product_instance,
                            rating=fake.random_int(1, 5),
                            comment=fake.sentence(),
                        )
                        generated_reviews.append(review)

                    product_instance.reviews.set(generated_reviews)
                    product_instance.save() 

                    self.stdout.write(self.style.SUCCESS(
                        f"Product '{product_data['title']}' seeded into database with fake users and reviews"))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error seeding data: {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"Generated users saved to {users_csv_file}"))
        self.stdout.write(self.style.SUCCESS(
            f"Generated reviews saved to {reviews_csv_file}"))
