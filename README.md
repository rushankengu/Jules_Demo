# ShopEnterprise

A modern, full-stack e-commerce application built with Flask, SQLite, and Bootstrap 5.

## Features

*   **User Authentication:** Login, Signup, and Admin roles.
*   **Product Catalog:** Browse products by category, search by name, and filter/sort.
*   **Shopping Cart:** Persistent cart backed by a database.
*   **Checkout:** Transactional checkout process with stock management.
*   **Recommendations:** ML-based substitute recommendations for out-of-stock items.
*   **Admin Dashboard:** Manage product inventory.
*   **Enterprise UI:** Responsive, professional design using Bootstrap 5.

## Setup Instructions

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Generate ML Models:**
    This step generates the similarity matrix for product recommendations.
    ```bash
    python generate_models.py
    ```

3.  **Seed Database:**
    Initialize the database and load product data.
    ```bash
    python seed_db.py
    ```
    *Note: Creates a default admin user with credentials: `admin` / `admin`.*

4.  **Run Application:**
    ```bash
    python app.py
    ```
    Access the app at `http://127.0.0.1:5000`.

## Project Structure

*   `app.py`: Main Flask application and routes.
*   `templates/`: HTML templates (Jinja2).
*   `static/`: CSS and assets.
*   `seed_db.py`: Script to populate the database.
*   `generate_models.py`: Script to generate recommendation models.
