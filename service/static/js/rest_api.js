$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    let BASE_URL = "/api/customers";

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#customer_id").val(res.id);
        $("#customer_username").val(res.username);
        $("#customer_password").val(res.password);
        $("#customer_first_name").val(res.first_name);
        $("#customer_last_name").val(res.last_name);
        $("#customer_gender").val(res.gender);
        if (res.active == true) {
            $("#customer_active").val("True");
        } else {
            $("#customer_active").val("False");
        }
        $("#customer_address").val(res.address);
        $("#customer_email").val(res.email);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#customer_username").val("");
        $("#customer_password").val("");
        $("#customer_first_name").val("");
        $("#customer_last_name").val("");
        $("#customer_gender").val("");
        $("#customer_active").val("");
        $("#customer_address").val("");
        $("#customer_email").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Customer
    // ****************************************

    $("#create-btn").click(function () {

        let username = $("#customer_username").val();
        let password = $("#customer_password").val();
        let first_name = $("#customer_first_name").val();
        let last_name = $("#customer_last_name").val();
        let gender = $("#customer_gender").val();
        let active = $("#customer_active").val() == "True";
        let address = $("#customer_address").val();
        let email = $("#customer_email").val();


        let data = {
            "username": username,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "active": active,
            "address": address,
            "email": email,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: BASE_URL,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // List all Customers
    // ****************************************

    $("#list-btn").click(function () {
        $("#flash_message").empty();
    
        let ajax = $.ajax({
            type: "GET",
            url: BASE_URL, 
            contentType: "application/json",
            data: ''
        });
    
        ajax.done(function (res) {
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">ID</th>'
            table += '<th class="col-md-2">Username</th>'
            table += '<th class="col-md-2">First Name</th>'
            table += '<th class="col-md-2">Last Name</th>'
            table += '<th class="col-md-2">Email</th>'
            table += '<th class="col-md-1">Active</th>'
            table += '<th class="col-md-2">Actions</th>'
            table += '</tr></thead><tbody>'
    
            res.forEach(function(customer) {
                table += `<tr id="row_${customer.id}" class="customer-row" data-customer-id="${customer.id}">
                    <td>${customer.id}</td>
                    <td>${customer.username}</td>
                    <td>${customer.first_name}</td>
                    <td>${customer.last_name}</td>
                    <td>${customer.email}</td>
                    <td>${customer.active}</td>
                    <td>
                        <button class="btn btn-info view-details-btn" data-customer-id="${customer.id}">View Details</button>
                        <button class="btn btn-success activate-btn" data-customer-id="${customer.id}" ${customer.active ? 'disabled' : ''}>Activate</button>
                        <button class="btn btn-warning deactivate-btn" data-customer-id="${customer.id}" ${!customer.active ? 'disabled' : ''}>Deactivate</button>
                    </td>
                </tr>`;
            });
    
            table += '</tbody></table>';
            $("#search_results").append(table);
            flash_message("Success")
        });
    
        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Update a Customer
    // ****************************************

    $("#update-btn").click(function () {
        let customer_id = $("#customer_id").val();
        let username = $("#customer_username").val();
        let password = $("#customer_password").val();
        let first_name = $("#customer_first_name").val();
        let last_name = $("#customer_last_name").val();
        let gender = $("#customer_gender").val();
        let active = $("#customer_active").val() == "True";
        let address = $("#customer_address").val();
        let email = $("#customer_email").val();

        let data = {
            "customer_id": customer_id,
            "username": username,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "active": active,
            "address": address,
            "email": email,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `${BASE_URL}/${customer_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Customer
    // ****************************************

    $("#retrieve-btn").click(function () {

        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `${BASE_URL}/${customer_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a customer by id
    // ****************************************

    $("#delete-btn").click(function () {

        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `${BASE_URL}/${customer_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Customer has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });


    // Event Listener for 'View Details' Button Clicks
    $(document).on('click', '.view-details-btn', function () {
        var customerId = $(this).data('customer-id');
        fetchCustomerDetails(customerId);
    });

    // ****************************************
    // Activate and deactivate buttons
    // ****************************************

    $(document).on('click', '.activate-btn', function () {
        let customerId = $(this).data('customer-id');
        toggleActiveStatus(customerId, true); 
    });
        
    $(document).on('click', '.deactivate-btn', function () {
        let customerId = $(this).data('customer-id');
        toggleActiveStatus(customerId, false); 
    });
        
    function toggleActiveStatus(customerId, isActive) {
        let statusText = isActive ? "Activating" : "Deactivating";
        let endpoint = isActive ? `${BASE_URL}/${customerId}/activate` : `${BASE_URL}/${customerId}/deactivate`;
    
        $.ajax({
            type: "PUT",
            url: endpoint,
            contentType: "application/json",
            data: '', 
            success: function () {
                flash_message(`${statusText} successful`);
                $('#' + `row_${customerId} .activate-btn`).prop('disabled', isActive);
                $('#' + `row_${customerId} .deactivate-btn`).prop('disabled', !isActive);
            },
            error: function (xhr) {
                flash_message(`${statusText} failed: ` + xhr.responseJSON.message);
            }
        });
    }
    
    // The function fetchCustomerDetails should send an AJAX request to your server to retrieve customer data and then display it in the modal
    function fetchCustomerDetails(customerId) {
        $.ajax({
            type: "GET",
            url: BASE_URL + "/" + customerId,
            contentType: "application/json",
            success: function (response) {
                // Assuming 'response' is the customer data
                $('#detail-id').text(response.id);
                $('#detail-username').text(response.username);
                $('#detail-first-name').text(response.first_name);
                $('#detail-last-name').text(response.last_name);

                $('#detail-gender').text(response.gender);
                $('#detail-active').text(response.active ? 'True' : 'False');
                $('#detail-address').text(response.address);
                $('#detail-email').text(response.email);
                // Show the modal
                $('#customerDetailsModal').modal('show');
            },
            error: function (xhr) {
                flash_message('Error: ' + xhr.responseJSON.message);
            }
        });
    }

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#customer_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });


    $("#search-btn").click(function () {

        let username = $("#customer_username").val();
        let email = $("#customer_email").val();
        let address = $("#customer_address").val();
        let first_name = $("#customer_first_name").val();
        let last_name = $("#customer_last_name").val();
        let gender = $("#customer_gender").val();
        let active = $("#customer_active").val();

        let queryString = ""

        if (username) {
            queryString += 'username=' + username
        }
        if (email) {
            if (queryString.length > 0) {
                queryString += '&email=' + email
            } else {
                queryString += 'email=' + email
            }
        }
        if (address) {
            if (queryString.length > 0) {
                queryString += '&address=' + address
            } else {
                queryString += 'address=' + address
            }
        }
        if (first_name) {
            if (queryString.length > 0) {
                queryString += '&first_name=' + first_name
            } else {
                queryString += 'first_name=' + first_name
            }
        }
        if (last_name) {
            if (queryString.length > 0) {
                queryString += '&last_name=' + last_name
            } else {
                queryString += 'last_name=' + last_name
            }
        }
        if (gender) {
            if (queryString.length > 0) {
                queryString += '&gender=' + gender
            } else {
                queryString += 'gender=' + gender
            }
        }
        if (active) {
            if (queryString.length > 0) {
                queryString += '&active=' + active
            } else {
                queryString += 'active=' + active
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `${BASE_URL}?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Username</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Gender</th>'
            table += '<th class="col-md-2">Active</th>'
            table += '<th class="col-md-2">Email</th>'
            table += '<th class="col-md-2">Address</th>'
            table += '</tr></thead><tbody>'
            let firstCustomer = "";

            for (let i = 0; i < res.length; i++) {
                let customer = res[i];
                let fullName = `${customer.first_name} ${customer.last_name}`;
                table += `<tr id="row_${customer.id}" class="customer-row" data-customer-id="${customer.id}">
                <td>${customer.id}</td>
                <td>${customer.username}</td>
                <td>${fullName}</td>
                <td>${customer.gender}</td>
                <td>${customer.active}</td>
                <td>${customer.email}</td>
                <td>${customer.address}</td>
                <td>
                    <button class="btn btn-success activate-btn" data-customer-id="${customer.id}" ${customer.active ? 'disabled' : ''}>Activate</button>
                    <button class="btn btn-warning deactivate-btn" data-customer-id="${customer.id}" ${!customer.active ? 'disabled' : ''}>Deactivate</button>
                </td>
            </tr>`;
                if (i == 0) {
                    firstCustomer = customer;
                }
            }
            

            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstCustomer != "") {
                update_form_data(firstCustomer)
            }

            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
        
    });
})
