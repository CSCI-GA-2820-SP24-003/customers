######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Customer Store Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Customers from the inventory of customers in the CustomerShop
"""
import hashlib
from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Customer, Gender
from service.common import status  # HTTP Status Codes


def encrypt_password(password):
    """Hashing Passwords"""
    return hashlib.sha256(password.encode("UTF-8")).hexdigest()


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for root URL")
    return app.send_static_file("index.html")


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# READ A CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>", methods=["GET"])
def get_customers(customer_id):
    """
    Retrieve a single Customer

    This endpoint will return a Customer based on it's id
    """
    app.logger.info("Request for customer with id: %s", customer_id)

    customer = Customer.find(customer_id)
    if not customer:
        error(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    app.logger.info("Returning customer: %s", customer.id)
    return jsonify(customer.serialize()), status.HTTP_200_OK


######################################################################
# CREATE CUSTOMER
######################################################################
@app.route("/customers", methods=["POST"])
def create_customers():
    """
    Creates a Customer

    This endpoint will create a Customer based the data in the body that is posted
    """
    app.logger.info("Request to create a customer")
    check_content_type("application/json")

    customer = Customer()
    customer.deserialize(request.get_json())
    customer.create()
    message = customer.serialize()
    location_url = url_for("get_customers", customer_id=customer.id, _external=True)

    app.logger.info("Customer with ID: %d created.", customer.id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# DELETE A CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customers(customer_id):
    """
    Delete a Customer

    This endpoint will delete a Customer based the id specified in the path
    """
    app.logger.info("Request to delete customer with id: %d", customer_id)
    customer = Customer.find(customer_id)
    if customer:
        customer.delete()

    app.logger.info("Customer with ID: %d delete complete.", customer_id)
    return "", status.HTTP_204_NO_CONTENT


######################################################################
# LIST ALL CUSTOMERS BY ATTRIBUTES
######################################################################
@app.route("/customers", methods=["GET"])
def list_customers():
    """Returns all of the Customers by some Attributes"""
    app.logger.info("Request for customer list")

    query = Customer.query

    # if 'username' in request.args:
    #     query = Customer.query_by_username(request.args.get('username'))
    # if 'email' in request.args:
    #     query = Customer.query_by_email(request.args.get('email'))
    # if 'first_name' in request.args:
    #     query = Customer.find_by_name(request.args.get('first_name'))
    # if 'last_name' in request.args:
    #     query = Customer.query_by_last_name(request.args.get('last_name'))
    # if 'address' in request.args:
    #     query = Customer.query_by_address(request.args.get('address'))

    # dynamic querying
    for param in ["username", "email", "address", "first_name", "last_name"]:
        if param in request.args:
            value = request.args.get(param)
            if value.startswith('"') and value.endswith('"'):
                # Exact search
                exact_value = value[1:-1]
                query = query.filter(getattr(Customer, param) == exact_value)
            else:
                # Fuzzy search
                query = query.filter(getattr(Customer, param).ilike(f"%{value}%"))

    if "gender" in request.args:
        gender_value = request.args.get("gender").upper()
        if gender_value in Gender.__members__:
            query = query.filter(getattr(Customer, "gender") == Gender[gender_value])
        else:
            return jsonify({"error": "Invalid gender value"}), 400

    if "active" in request.args:
        active_value = request.args.get("active").lower()
        if active_value in ["true", "1"]:
            query = query.filter(Customer.active)
        elif active_value in ["false", "0"]:
            query = query.filter(~Customer.active)
        else:
            return jsonify({"error": "Invalid active value"}), 400

    customers = query.all()
    results = [customer.serialize() for customer in customers]
    app.logger.info("Returning %d customers", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customers(customer_id):
    """
    Update a Customer

    This endpoint will update a Customer based the body that is posted
    """
    app.logger.info("Request to update customer with id: %d", customer_id)
    check_content_type("application/json")
    # original_password = None
    customer = Customer.find(customer_id)
    if not customer:
        error(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id: '{customer_id}' was not found.",
        )
    # else:
    original_hashed_password = customer.password

    customer.deserialize(request.get_json())
    customer.id = customer_id
    # Hash the new password if it's different from the original
    if customer.password != original_hashed_password:
        customer.password = encrypt_password(customer.password)
    customer.update(original_hashed_password)

    app.logger.info("Customer with ID: %d updated.", customer.id)
    return jsonify(customer.serialize()), status.HTTP_200_OK


######################################################################
# ACTIVATE A CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>/activate", methods=["PUT"])
def activate_customer(customer_id):
    """
    Activate a customer
    This endpoint will activate a customer based on the id specified in the path
    """
    customer = Customer.find(customer_id)
    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    customer.activate()
    return jsonify(""), status.HTTP_204_NO_CONTENT


######################################################################
# DEACTIVATE A CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>/deactivate", methods=["PUT"])
def deactivate_customer(customer_id):
    """
    Deactivate a customer
    This endpoint will deactivate a customer based on the id specified in the path
    """
    customer = Customer.find(customer_id)
    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    customer.deactivate()
    return jsonify(""), status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
@app.route("/customers/<int:customer_id>/check_content_type", methods=["PUT"])
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        error(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    error(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# Logs error messages before aborting
######################################################################
def error(status_code, reason):
    """Logs the error and then aborts"""
    app.logger.error(reason)
    abort(status_code, reason)
