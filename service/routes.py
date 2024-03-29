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
from service.models import Customer
from service.common import status  # HTTP Status Codes


def encrypt_password(password):
    """ Hashing Passwords """
    return hashlib.sha256(password.encode("UTF-8")).hexdigest()


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    # return (
    #     "Reminder: return some useful information in json format about the service here",
    #     status.HTTP_200_OK,
    # )
    return jsonify({
        "1_Customers": "Welcome to the Customer Store Service API. This API allows you to manage the customers.",
        "2_methods_available": {
            "2.1 GET /customers/<customer_id>": "Retrieve a single customer by ID.",
            "2.2 POST /customers": "Create a new customer.",
            "2.3 DELETE /customers/<customer_id>": "Delete a customer by ID.",
            "2.4 GET /customers": "Retrieve a list of all customers.",
            "2.5 PUT /customers/<customer_id>": "Update an existing customer by ID."
        },
        "3_contact": "For more information, refer to the API documentation or contact support@example.com."
    }), status.HTTP_200_OK


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

    app.logger.info(
        "Returning customer: %s", customer.id
    )
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
# LIST ALL CUSTOMERS
######################################################################
@app.route("/customers", methods=["GET"])
def list_customers():
    """Returns all of the Customers"""
    app.logger.info("Request for customer list")

    customers = Customer.all()

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
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
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
