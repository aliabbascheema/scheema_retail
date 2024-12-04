# Scheema Retail
This project is a practical implementation focused on Ipswich Retail, aiming to transition from a monolithic system architecture to a more scalable and efficient Django MVT (Model-View-Template) framework. The goal is to address the limitations of the current system and enhance flexibility, maintainability, and performance by adopting a more modular approach.


## Views
### Overview
This is a Django views file for a retail store web application, handling various user interactions and e-commerce functionalities such as user authentication, product browsing, cart management, and order processing.

### Key Components
#### Authentication Views
- `CustomLoginView()`: Extends Django's default login view with cart migration for authenticated users
- `register()`: Handles user registration process
- `update_profile()`: Allows users to update their profile information
#### Product and Cart Management
- `home()`: Displays all available products
- `product_detail()`: Shows detailed information about a specific product
- `category_products()`: Lists products within a specific category
- `add_to_cart()`: Adds products to cart (supports both authenticated and guest users)
- `remove_from_cart()`: Reduces or removes cart items
- `view_cart()`: Displays current cart contents and calculates total cost
#### Order Processing
- `place_order()`: Creates an order from cart items
- `dashboard()`: Shows user's order history
#### Key Features
- Session-based cart for guest users
- Cart item migration during login
- Profile creation and management
- Product search functionality
- Dynamic cart total calculation