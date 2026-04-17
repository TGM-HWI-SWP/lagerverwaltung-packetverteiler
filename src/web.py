from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for

from .adapters.repository import RepositoryFactory
from .domain.order import OrderStatus
from .services import WarehouseService

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "dev-secret-key"

repository = RepositoryFactory.create_repository("memory")
service = WarehouseService(repository)


def _generate_order_id() -> str:
    return f"order_{int(datetime.now().timestamp() * 1000)}"


@app.route("/", methods=["GET"])
def index():
    products = list(service.get_all_products().values())
    movements = service.get_movements()
    orders = list(service.get_all_orders().values())
    total_value = service.get_total_inventory_value()
    return render_template(
        "index.html",
        products=products,
        movements=movements,
        orders=orders,
        total_value=total_value,
    )


@app.route("/add-product", methods=["POST"])
def add_product():
    try:
        service.create_product(
            product_id=request.form["product_id"].strip(),
            name=request.form["name"].strip(),
            description=request.form.get("description", "").strip(),
            price=float(request.form.get("price", 0)),
            category=request.form.get("category", "").strip(),
            initial_quantity=int(request.form.get("quantity", 0)),
        )
        flash("Produkt erfolgreich hinzugefügt.", "success")
    except Exception as error:
        flash(str(error), "error")
    return redirect(url_for("index"))


@app.route("/delete-product/<product_id>", methods=["POST"])
def delete_product(product_id: str):
    try:
        service.delete_product(product_id)
        flash("Produkt gelöscht.", "success")
    except Exception as error:
        flash(str(error), "error")
    return redirect(url_for("index"))


@app.route("/stock-in", methods=["POST"])
def stock_in():
    try:
        service.add_to_stock(
            product_id=request.form["product_id"],
            quantity=int(request.form.get("quantity", 0)),
            reason=request.form.get("reason", "Einlagerung"),
            user=request.form.get("user", "WebUI"),
        )
        flash("Bestand erfolgreich erhöht.", "success")
    except Exception as error:
        flash(str(error), "error")
    return redirect(url_for("index"))


@app.route("/stock-out", methods=["POST"])
def stock_out():
    try:
        service.remove_from_stock(
            product_id=request.form["product_id"],
            quantity=int(request.form.get("quantity", 0)),
            reason=request.form.get("reason", "Auslagerung"),
            user=request.form.get("user", "WebUI"),
        )
        flash("Bestand erfolgreich verringert.", "success")
    except Exception as error:
        flash(str(error), "error")
    return redirect(url_for("index"))


@app.route("/create-order", methods=["POST"])
def create_order():
    customer_id = request.form.get("customer_id", "").strip()
    customer_name = request.form.get("customer_name", "").strip() or customer_id
    product_id = request.form.get("product_id", "")
    quantity = int(request.form.get("quantity", 0))

    try:
        if not customer_id:
            raise ValueError("Customer ID ist erforderlich.")

        if not service.get_customer(customer_id):
            service.create_customer(
                customer_id=customer_id,
                name=customer_name,
                contact_email=f"{customer_id}@example.local",
            )

        order_id = _generate_order_id()
        order = service.create_order(order_id=order_id, customer_id=customer_id)
        service.add_item_to_order(order_id=order.id, product_id=product_id, quantity=quantity)
        flash("Bestellung erstellt.", "success")
    except Exception as error:
        flash(str(error), "error")
    return redirect(url_for("index"))


@app.route("/update-order/<order_id>", methods=["POST"])
def update_order(order_id: str):
    status = request.form.get("status")
    try:
        if status not in [
            "pending",
            "confirmed",
            "shipped",
            "delivered",
            "cancelled",
        ]:
            raise ValueError("Ungültiger Bestellstatus.")

        service.update_order_status(order_id, OrderStatus(status))
        flash("Bestellstatus aktualisiert.", "success")
    except Exception as error:
        flash(str(error), "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
