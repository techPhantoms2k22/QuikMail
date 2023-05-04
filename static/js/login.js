$(document).ready(function () {
  $("#captch_form").on("submit", function (event) {
    var uname = $("#uname").val();
    if (uname == "") {
      $("#uname_error").html("Please Enter Username");
      $("#uname_error").show();
      $("#uname").css("border-color", "red");
      return false;
    }
    var psw = $("#password").val();
    var passw = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,20}$/;
    if (psw == "") {
      $("#pass_error").html("Please enter valid password");
      $("#pass_error").show();
      $("#password").css("border-color", "red");
      return false;
    }
  });

  $("#uname").focus(function (e) {
    $("#uname_error").hide();
    $("#uname").css("border-color", "");
  });
  $("#password").focus(function (e) {
    $("#pass_error").hide();
    $("#password").css("border-color", "");
  });
});
