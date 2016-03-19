$(document).ready(function(){
    $.get("/users/sessionVerify", function(data) {
        if (data.code == 0) {
            $(".logger").css('display', 'none');
            $(".user-center").css('display', 'block');
            $("#user-nickname-a").html("&nbsp;" + data.nickname);
        }
        else {
            $(".logger").css('display', 'block');
            $(".user-center").css('display', 'none');
        }
    });

    $("#head-a-login").click(function(event) {
        event.preventDefault();
        var redirectable_login = "/users/login?redirect=" + $("#redirect").html();
        window.location = redirectable_login;
    });
    $("#head-a-regi").click(function(event) {
        event.preventDefault();
        var redirectable_login = "/users/register?redirect=" + $("#redirect").html();
        window.location = redirectable_login;
    });
    $("#user-logout-a").click(function(event) {
        event.preventDefault();
        $.get("/users/logout", function(data) {
            if (data.code == 0) {
                var redirectable_login = "/users/login?redirect=" + $("#redirect").html();
                window.location = redirectable_login;
            }
        });
    });
});
