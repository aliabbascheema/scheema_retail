from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from django.forms import ValidationError
from django.utils.text import slugify


class Category(models.Model):
    """
    Category represents a category with a name and a unique slug. It automatically generates the slug from the name if it is not provided.

    Attributes:
        name (str): The name of the category.
        slug (str): A unique slug for the category, generated from the name if not provided.

    Methods:
        save(*args, **kwargs): Saves the category instance, generating the slug if it is not set.
        __str__(): Returns the name of the category as its string representation.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product represents an item for sale, including its details such as name, SKU, price, and associated category. It automatically generates a slug from the name if it is not provided.

    Attributes:
        name (str): The name of the product.
        slug (str): A unique slug for the product, generated from the name if not provided.
        sku (str): A unique stock keeping unit identifier for the product.
        description (str): A detailed description of the product.
        price (Decimal): The price of the product.
        category (Category): The category to which the product belongs.
        stock (int): The quantity of the product available in stock.
        features (str): Additional features of the product, optional.
        reviews (ManyToManyField): A collection of reviews associated with the product.
        images_urls (list): A list of image URLs for the product.

    Methods:
        save(*args, **kwargs): Saves the product instance, generating the slug if it is not set.
        __str__(): Returns the name of the product as its string representation.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)
    features = models.TextField(blank=True, null=True)
    reviews = models.ManyToManyField(
        'Review', blank=True, related_name='products')
    images_urls = models.JSONField(default=list)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """
    ProductImage represents an image associated with a specific product. It allows for the storage of multiple images for each product, facilitating better visual representation.

    Attributes:
        product (Product): The product to which the image belongs.
        image (ImageField): The image file uploaded for the product.

    Methods:
        __str__(): Returns a string representation of the product image, typically the product's name or identifier.
    """

    product = models.ForeignKey(
        Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')


class Review(models.Model):
    """
    Review represents a user's feedback on a product, including a rating and optional comment. It ensures that the rating is within a valid range before saving the review.

    Attributes:
        user (User): The user who submitted the review.
        product (Product): The product being reviewed.
        rating (int): A rating for the product, constrained to be between 1 and 5.
        comment (str): An optional comment providing additional feedback.
        created_at (datetime): The timestamp when the review was created.

    Methods:
        clean(): Validates the rating to ensure it is between 1 and 5.
        save(*args, **kwargs): Saves the review instance after validation.
        __str__(): Returns a string representation of the review, including the user's username and the product's name.
    """
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=1)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not (1 <= self.rating <= 5):
            raise ValidationError("Rating must be between 1 and 5.")

    def save(self, *args, **kwargs):
        self.clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Review by {self.user.username} for {self.product.name}'


class Cart(models.Model):
    """
    Cart represents a shopping cart associated with a user or a session. It stores the user information and session key for managing the cart's contents.

    Attributes:
        user (User): The user associated with the cart, optional.
        session_key (str): A unique session identifier for the cart, optional.

    Methods:
        __str__(): Returns a string representation of the cart, including the user and the label "Cart".
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(
        max_length=40, null=True, blank=True)

    def __str__(self):
        return f"{self.user} - Cart"


class CartItem(models.Model):
    """
    CartItem represents an item in a shopping cart, linking a specific product to the cart along with its quantity. It provides a way to calculate the total price for the item based on the product's price and the quantity specified.

    Attributes:
        cart (Cart): The cart that contains this item.
        product (Product): The product associated with this cart item.
        quantity (int): The number of units of the product in the cart.

    Properties:
        total_price (Decimal): The total price for the cart item, calculated as the product price multiplied by the quantity.

    Methods:
        __str__(): Returns a string representation of the cart item, including the cart, product, and quantity.
    """

    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return Decimal(self.product.price) * self.quantity

    def __str__(self):
        return f"{self.cart} - {self.product} - {self.quantity}"


class Wishlist(models.Model):
    """
    Wishlist represents a collection of products that a user wishes to purchase in the future. It links a user to specific products they have added to their wishlist.

    Attributes:
        user (User): The user who owns the wishlist.
        product (Product): The product that has been added to the user's wishlist.

    Methods:
        __str__(): Returns a string representation of the wishlist item, typically including the user's identifier and the product's name.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Order(models.Model):
    """
    Order represents a customer's order, including the user who placed the order and the total price of the order. It tracks when the order was created and provides a way to retrieve the items associated with the order.

    Attributes:
        user (User): The user who placed the order.
        total_price (Decimal): The total price of the order.
        created_at (datetime): The timestamp when the order was created.

    Methods:
        __str__(): Returns a string representation of the order, including the order ID, user, and total price.
        get_items(): Retrieves all items associated with the order.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user or 'Guest'} - ${self.total_price}"

    def get_items(self):
        return self.items.all()


class OrderItem(models.Model):
    """
    OrderItem represents an individual item within an order, linking a specific product to the order along with its quantity and price. It also allows for the storage of an optional image associated with the order item.

    Attributes:
        order (Order): The order to which this item belongs.
        product (Product): The product associated with this order item.
        quantity (int): The quantity of the product in the order.
        price (Decimal): The price of the product at the time of the order.
        image (ImageField): An optional image file associated with the order item.

    Methods:
        __str__(): Returns a string representation of the order item, including the product name, quantity, and price.
    """

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="order_items/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} - Qty: {self.quantity} - Price: ${self.price}"


class UserProfile(models.Model):
    """
    UserProfile represents additional information about a user, including their profile image, description, job title, and social links. It establishes a one-to-one relationship with the User model, allowing for the extension of user data.

    Attributes:
        user (User): The user associated with this profile.
        profile_image (ImageField): An optional image file for the user's profile.
        description (str): An optional description of the user.
        job_title (str): An optional job title for the user.
        social_links (dict): A JSON field to store the user's social media links.
        created_at (datetime): The timestamp when the profile was created.
        updated_at (datetime): The timestamp when the profile was last updated.

    Methods:
        __str__(): Returns a string representation of the user profile, including the user's username.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")
    profile_image = models.ImageField(
        upload_to='profile_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    social_links = models.JSONField(default=dict, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
