$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
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
        $("#customer_data").val("");
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
        let active = $("#customer_active").val() == "true";
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
            url: "/customers",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
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
        url: "/customers", // Adjust the URL to match your API endpoint for fetching customers
        contentType: "application/json",
        data: ''
    });

    ajax.done(function (res) {
        $("#search_results").empty();
        let table = '<table class="table table-striped" cellpadding="10">'
        table += '<thead><tr>'
        table += '<th class="col-md-2">ID</th>'
        table += '<th class="col-md-2">Username</th>'
        table += '<th class="col-md-2">First Name</th>'
        table += '<th class="col-md-2">Last Name</th>'
        table += '<th class="col-md-2">Email</th>'
        table += '<th class="col-md-2">Active</th>'
        table += '</tr></thead><tbody>'
        let firstCustomer = "";
        // for (let i = 0; i < res.length; i++) {
        //     let customer = res[i];
        //     table += `<tr id="row_${i}"><td>${customer.id}</td><td>${customer.username}</td><td>${customer.first_name}</td><td>${customer.last_name}</td><td>${customer.email}</td><td>${customer.active}</td></tr>`;
        //     if (i == 0) {
        //         firstCustomer = customer;
        //     }
        // }

        for (let i = 0; i < res.length; i++) {
            let customer = res[i];
            table += `<tr id="row_${customer.id}" class="customer-row" data-customer-id="${customer.id}">
                <td>${customer.id}</td>
                <td>${customer.username}</td>
                <td>${customer.first_name}</td>
                <td>${customer.last_name}</td>
                <td>${customer.email}</td>
                <td>${customer.active}</td>
                <td><button class="btn btn-info view-details-btn" data-customer-id="${customer.id}">View Details</button></td>
            </tr>`;
        }

        table += '</tbody></table>';
        $("#search_results").append(table);

        flash_message("Success")
    });

    ajax.fail(function (res) {
        flash_message(res.responseJSON.message)
    });
});
})


// Event Listener for 'View Details' Button Clicks
$(document).on('click', '.view-details-btn', function() {
    var customerId = $(this).data('customer-id');
    fetchCustomerDetails(customerId);
});

// The function fetchCustomerDetails should send an AJAX request to your server to retrieve customer data and then display it in the modal
function fetchCustomerDetails(customerId) {
    $.ajax({
        type: "GET",
        url: "/customers/" + customerId,
        contentType: "application/json",
        success: function(response) {
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
        error: function(xhr) {
            flash_message('Error: ' + xhr.responseJSON.message);
        }
    });
}
