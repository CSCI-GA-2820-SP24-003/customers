$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#customer_id").val(res.id);
        $("#customer_username").val(res.username);
        $("#customer_password").val(res.password);
        $("#customer_first_name").val(res.first_name);
        $("#customer_last_name").val(res.last_name);
        $("#customer_gender").val(res.gender);
        if (res.active == true) {
            $("#customer_active").val("true");
        } else {
            $("#customer_active").val("false");
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

        let id = $("#customer_id").val();
        let username = $("#customer_username").val();
        let first_name = $("#customer_first_name").val();
        let last_name = $("#customer_last_name").val();
        let gender = $("#customer_gender").val();
        let active = $("#customer_active").val() == "true";
        let address = $("#customer_address").val();
        let email = $("#customer_email").val();
        

        let data = {
            "id": id,
            "username": username,
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
})