from flask import Flask, render, request, redirect, url_for, flash, session
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = "kisan_setu_bca_project_2026"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
print("================================")
print("URL:", repr(SUPABASE_URL))
print("KEY:", repr(SUPABASE_KEY))
print("================================")

try:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Missing Supabase credentials. Check .env file.")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    SUPABASE_CONNECTED = True
except Exception as error:
    print("Supabase connection error:", error)
    supabase = None
    SUPABASE_CONNECTED = False


def current_user():
    return {
        "id": session.get("user_id"),
        "username": session.get("username"),
        "role": session.get("role")
    }


@app.route("/")
def home():
    return render("home.html", connected=SUPABASE_CONNECTED, user=current_user())


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            profile_data = {
                "username": request.form.get("username"),
                "email": request.form.get("email"),
                "password": request.form.get("password"),
                "role": request.form.get("role"),
                "location": request.form.get("location")
            }

            if not all([profile_data["username"], profile_data["email"], profile_data["password"], profile_data["role"]]):
                flash("Please fill all required fields.", "error")
                return redirect(url_for("register"))

            if not supabase:
                flash("Supabase is not connected. Please check .env file.", "error")
                return redirect(url_for("register"))

            # Supabase API call: insert new farmer/buyer profile
            response = supabase.table("profiles").insert(profile_data).execute()
            print("REGISTER RESPONSE:", response.data)

            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))

        except Exception as error:
            print("Registration error:", error)
            flash("Registration failed. Email may already exist or database setup is incomplete.", "error")
            return redirect(url_for("register"))

    return render("register.html", user=current_user())


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            email = request.form.get("email")
            password = request.form.get("password")

            if not supabase:
                flash("Supabase is not connected. Please check .env file.", "error")
                return redirect(url_for("login"))

            # Supabase API call: check matching email and password
            response = supabase.table("profiles").select("*").eq("email", email).eq("password", password).execute()
            print("LOGIN RESPONSE:", response.data)
            if not response.data:
                flash("Invalid email or password.", "error")
                return redirect(url_for("login"))

            user = response.data[0]
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            flash("Login successful.", "success")

            if user["role"] == "farmer":
                return redirect(url_for("farmer_dashboard"))
            return redirect(url_for("buyer_dashboard"))

        except Exception as error:
            print("Login error:", error)
            flash("Login failed.", "error")
            return redirect(url_for("login"))

    return render("login.html", user=current_user())


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))


@app.route("/farmer-dashboard")
def farmer_dashboard():
    if session.get("role") != "farmer":
        flash("Please login as farmer.", "error")
        return redirect(url_for("login"))

    try:
        products = []
        orders = []
        if supabase:
            products = supabase.table("products").select("*").eq("farmer_id", session["user_id"]).execute().data
            all_orders = supabase.table("orders").select("*").execute().data
            product_ids = [p["id"] for p in products]
            orders = [o for o in all_orders if o.get("product_id") in product_ids]

        return render("farmer_dashboard.html", products=products, orders=orders, user=current_user())

    except Exception as error:
        print("Farmer dashboard error:", error)
        flash("Unable to load farmer dashboard.", "error")
        return render("farmer_dashboard.html", products=[], orders=[], user=current_user())


@app.route("/buyer-dashboard")
def buyer_dashboard():
    if session.get("role") != "buyer":
        flash("Please login as buyer.", "error")
        return redirect(url_for("login"))

    try:
        orders = []
        if supabase:
            orders = supabase.table("orders").select("*").eq("buyer_id", session["user_id"]).execute().data

        return render("buyer_dashboard.html", orders=orders, user=current_user())

    except Exception as error:
        print("Buyer dashboard error:", error)
        flash("Unable to load buyer dashboard.", "error")
        return render("buyer_dashboard.html", orders=[], user=current_user())


@app.route("/products")
def products():
    try:
        if not supabase:
            flash("Supabase is not connected.", "error")
            return render("products.html", products=[], user=current_user())

        # Supabase API call: fetch all products from database
        response = supabase.table("products").select("*").execute()
        return render("products.html", products=response.data, user=current_user())

    except Exception as error:
        print("Fetch products error:", error)
        flash("Unable to fetch products.", "error")
        return render("products.html", products=[], user=current_user())


@app.route("/add-product", methods=["GET", "POST"])
def add_product():
    if session.get("role") != "farmer":
        flash("Only farmers can add products.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            product_data = {
                "farmer_id": session["user_id"],
                "farmer_name": session["username"],
                "crop_name": request.form.get("crop_name"),
                "category": request.form.get("category"),
                "price": float(request.form.get("price")),
                "quantity": request.form.get("quantity"),
                "description": request.form.get("description")
            }

            if not product_data["crop_name"] or not product_data["quantity"]:
                flash("Crop name and quantity are required.", "error")
                return redirect(url_for("add_product"))

            if not supabase:
                flash("Supabase is not connected.", "error")
                return redirect(url_for("add_product"))

            # Supabase API call: insert product into products table
            response = supabase.table("products").insert(product_data).execute()
            print("ADD PRODUCT RESPONSE:", response.data)

            flash("Product added successfully.", "success")
            return redirect(url_for("farmer_dashboard"))

        except Exception as error:
            print("Add product error:", error)
            flash("Unable to add product.", "error")
            return redirect(url_for("add_product"))

    return render("add_product.html", user=current_user())


@app.route("/edit-product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if session.get("role") != "farmer":
        flash("Only farmers can edit products.", "error")
        return redirect(url_for("login"))

    try:
        product = supabase.table("products").select("*").eq("id", product_id).execute().data[0]

        if request.method == "POST":
            updated_data = {
                "crop_name": request.form.get("crop_name"),
                "category": request.form.get("category"),
                "price": float(request.form.get("price")),
                "quantity": request.form.get("quantity"),
                "description": request.form.get("description")
            }

            # Supabase API call: update product
            supabase.table("products").update(updated_data).eq("id", product_id).execute()

            flash("Product updated successfully.", "success")
            return redirect(url_for("farmer_dashboard"))

        return render("edit_product.html", product=product, user=current_user())

    except Exception as error:
        print("Edit product error:", error)
        flash("Unable to edit product.", "error")
        return redirect(url_for("farmer_dashboard"))


@app.route("/delete-product/<int:product_id>")
def delete_product(product_id):
    if session.get("role") != "farmer":
        flash("Only farmers can delete products.", "error")
        return redirect(url_for("login"))

    try:
        # Supabase API call: delete product
        supabase.table("products").delete().eq("id", product_id).execute()
        flash("Product deleted successfully.", "success")
    except Exception as error:
        print("Delete product error:", error)
        flash("Unable to delete product.", "error")

    return redirect(url_for("farmer_dashboard"))


@app.route("/order/<int:product_id>", methods=["GET", "POST"])
def order_product(product_id):
    if session.get("role") != "buyer":
        flash("Please login as buyer to place order.", "error")
        return redirect(url_for("login"))

    try:
        product = supabase.table("products").select("*").eq("id", product_id).execute().data[0]

        if request.method == "POST":
            qty = float(request.form.get("quantity_ordered"))
            total = qty * float(product["price"])
            payment_method = request.form.get("payment_method")

            order_data = {
                "buyer_id": session["user_id"],
                "buyer_name": session["username"],
                "product_id": product["id"],
                "crop_name": product["crop_name"],
                "quantity_ordered": qty,
                "total_amount": total,
                "payment_method": payment_method,
                "status": "Payment Completed"
            }

            # Supabase API call: insert order into orders table
            response = supabase.table("orders").insert(order_data).execute()
            print("ORDER RESPONSE:", response.data)

            return render("success.html", order=order_data, user=current_user())

        return render("order.html", product=product, user=current_user())

    except Exception as error:
        print("Order error:", error)
        flash("Unable to place order.", "error")
        return redirect(url_for("products"))


@app.route("/database-status")
def database_status():
    try:
        profiles = supabase.table("profiles").select("*").execute().data if supabase else []
        products_data = supabase.table("products").select("*").execute().data if supabase else []
        orders_data = supabase.table("orders").select("*").execute().data if supabase else []

        return render(
            "database_status.html",
            profiles=profiles,
            products=products_data,
            orders=orders_data,
            connected=SUPABASE_CONNECTED,
            user=current_user()
        )
    except Exception as error:
        print("Database status error:", error)
        flash("Unable to load database data.", "error")
        return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
