# Aliabba Retail - Practical Implementation of Scalable E-commerce with Django MVT Framework

## Overview

This project is a practical implementation focused on Ipswich Retail, aiming to transition from a monolithic system architecture to a more scalable and efficient Django MVT (Model-View-Template) framework. The goal is to address the limitations of the current system and enhance flexibility, maintainability, and performance by adopting a more modular approach.

The application includes key e-commerce functionalities such as user authentication, product browsing, cart management, and order processing, with a focus on seamless user experience and modularity.

![Screenshot 2024-12-04 at 18-05-42 Aliabba Retail](https://github.com/user-attachments/assets/ab292074-4659-4f44-86df-c05fbf74e955)


## Objectives

1. Replace the monolithic architecture with a modular Django MVT framework.
2. Enhance deployment workflows using Render’s automated services and built-in monitoring tools.
3. Improve scalability and application performance while minimizing downtime.
4. Implement CI/CD pipelines for continuous integration and delivery.
5. Use SQLite for a lightweight and easy-to-manage database.

## Project Structure:

```
scheema_retail/
│
├── scheema_retail/                # Django project folder (core functionality)
│   ├── __init__.py
│   ├── settings.py                # Django settings file
│   ├── urls.py                    # URL routing for the project
│   ├── wsgi.py                    # WSGI configuration for deployment
│   ├── asgi.py                    # ASGI configuration for asynchronous servers
│   ├── manage.py                  # Django manage.py script to run commands
│   ├── templates/                 # Django templates for HTML rendering
│   │   ├── base.html              # Base template for inheritance
│   │   ├── home.html              # Home page template
│   │   └── product_detail.html    # Product detail page template
│   ├── static/                    # Static assets (CSS, JS, images)
│   │   ├── css/
│   │   │   └── styles.css         # Compiled CSS files (Tailwind or custom)
│   │   ├── js/
│   │   │   └── app.js             # Custom JS (if needed)
│   │   └── images/                # Static images
│   └── scheema_retail_store/                  # App for product and cart management
│       ├── __init__.py
│       ├── models.py              # Django models for products, categories, etc.
│       ├── views.py               # Views for handling product display, cart, etc.
│       ├── urls.py                # URLs related to the products and cart
│       ├── forms.py               # Forms for handling user input (e.g., search, cart)
│       ├── admin.py               # Django admin configuration for product management
│       └── migrations/            # Database migration files
│
├── scheema_retail_frontend/       # Frontend related files (Tailwind, JS, etc.)
│   ├── templates/                 # Frontend templates
│   ├── stores/                    # Frontend templates for core functionality
│   │   │   ├── base.html              # Base template for inheritance (now in frontend)
│   │   │   ├── home.html              # Home page template
│   │   │   └── product_detail.html    # Product detail page template
│   ├── tailwind.config.js         # Tailwind configuration file
│   └── package.json              # NPM dependencies for frontend
│
├── docker-compose.yml            # Docker Compose file for containerized deployment
├── Dockerfile                    # Dockerfile for creating the app container
├── requirements.txt              # Python dependencies for the project
├── pytest.ini                    # Configuration for pytest testing framework
├── .gitignore                    # Git ignore file to exclude unnecessary files
├── .dockerignore                 # Docker ignore file for unnecessary files during build
└── README.md                     # Project README
```

### Breakdown of Key Directories and Files:

1. **`scheema_retail/`**: This is the main Django project folder that contains:
   - **`settings.py`**: Configuration settings for the Django project.
   - **`urls.py`**: URL routing for the entire project.
   - **`templates/`**: HTML templates rendered by Django views.
   - **`static/`**: Static assets like CSS (Tailwind), JavaScript, and images.
   - **`scheema_retail_store/`**: The main app for handling product management, cart functionality, and order processing.

2. **`scheema_retail_frontend/`**: Contains frontend-related configurations and files.
   - **`tailwind.config.js`**: Tailwind CSS configuration file to manage styling.
   - **`package.json`**: For managing JavaScript dependencies if required (like custom scripts).

3. **`docker-compose.yml` and `Dockerfile`**: Configuration files to containerize the application and manage deployments.

4. **`requirements.txt`**: Python package dependencies required for the project.

5. **`pytest.ini`**: Configuration file for setting up and running tests with pytest.

6. **`README.md`**: Documentation file that describes the project, setup, and usage instructions.


## Key Features

### Authentication Views
- **CustomLoginView():** Extends Django's default login view to include cart migration for authenticated users.
- **register():** Handles user registration.
- **update_profile():** Allows users to update their profile information.

### Product and Cart Management
- **home():** Displays all available products.
- **product_detail():** Shows detailed information about a specific product.
- **category_products():** Lists products within a specific category.
- **add_to_cart():** Adds products to the cart (supports both authenticated and guest users).
- **remove_from_cart():** Removes or reduces items in the cart.
- **view_cart():** Displays the current cart contents and dynamically calculates the total cost.

### Order Processing
- **place_order():** Processes orders based on cart items.
- **dashboard():** Provides users with a view of their order history.

### Additional Features
- **Session-based Cart:** Allows guest users to add products to a cart without logging in.
- **Cart Migration:** Transfers cart items seamlessly upon user login.
- **Profile Management:** Users can create and manage their profiles.
- **Product Search:** Includes functionality to search for products efficiently.
- **Dynamic Cart Totals:** Automatically updates cart totals based on items added or removed.

## Project Architecture

### 1. Frontend:
   - **Tailwind CSS:** Modern and responsive design.
   - **Django Templates:** For rendering dynamic content.

### 2. Backend:
   - **Django MVT Framework:** Modular architecture for improved scalability.
   - **SQLite Database:** Lightweight and easy to manage for the PoC.

### 3. DevOps Workflow:
   - **Continuous Integration:** Automated testing and code integration with GitHub Actions.
   - **Continuous Deployment:** Seamless updates via Render.
   - **Monitoring and Logging:** Leverages Render’s built-in tools for real-time insights.

## Workflow & models overview
### Models Overview
![Screenshot 2024-12-03 at 23-52-12 ](https://github.com/user-attachments/assets/8ee5ba85-3a32-440d-bc0e-4825d8fd536a)

### Workflow Structure
![Screenshot 2024-12-03 at 23-51-21 ](https://github.com/user-attachments/assets/8686a1f0-6155-4482-959a-565f6133dee1)


## Installation Guide

### Prerequisites
- Python 3.8+
- Node.js (for Tailwind CSS)
- Docker (optional for local containerized development)

### Steps to Set Up Locally
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/aliabbascheema/scheema_retail.git
   cd scheema_retail
   ```

2. **Backend Setup:**
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Apply migrations:
     ```bash
     python3 manage.py migrate
     ```
   - Run the server:
     ```bash
     python3 manage.py runserver
     ```

3. **Frontend Setup:**
   - Install Tailwind dependencies:
     ```bash
     python3 manage.py tailwind install
     ```
   - Start Tailwind CSS:
     ```bash
     python3 manage.py tailwind start
     ```

4. **Deploy to Render:**
   - Push the project to a GitHub repository.
   - Connect the repository to Render for automated deployment.
   - Configure environment variables and deploy services.

## Usage

- Access the application on Render’s hosted URL.
- Admin dashboard available at `/admin` for managing products and orders.

## Future Improvements

1. **Enhanced Orchestration:**
   - Introduce Kubernetes for managing large-scale deployments and auto-scaling.
2. **PWA Features:**
   - Enable offline functionality and app-like experiences for users.
3. **AI-Driven Recommendations:**
   - Leverage machine learning for personalized user experiences.
4. **Global Adaptation:**
   - Support multiple languages, currencies, and regional tax compliance.
5. **Security Enhancements:**
   - Automate vulnerability scans and adopt robust security protocols.

## Reflection

This project demonstrates how transitioning to a Django MVT framework and adopting DevOps practices can address challenges posed by legacy systems. By using Render’s deployment and monitoring tools, alongside a modular architecture, Ipswich Retail achieves enhanced flexibility, maintainability, and performance. While SQLite meets current requirements, scaling may necessitate transitioning to PostgreSQL or MySQL in the future.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
