$(document).ready(function (e) {
  $("#btn_register").click(function (e) {
    var uID = $("#uID").val();
    if (uID == "") {
      $("#uID_error").html("Please enter User Name");
      $("#uID_error").show();
      $("#uID").css("border-color", "red");
      return false;
    }
    var fname = $("#fname").val();
    if (fname == "") {
      $("#fname_error").html("Please enter First Name");
      $("#fname_error").show();
      $("#fname").css("border-color", "red");
      return false;
    }
    var lname = $("#lname").val();
    if (lname == "") {
      $("#lname_error").html("Please enter Last Name");
      $("#lname_error").show();
      $("#lname").css("border-color", "red");
      return false;
    }

    var psw = $("#psw").val();
    var psw_repeat = $("#psw_repeat").val();
    var passw = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,20}$/;
    if (psw == "") {
      $("#p1_error").html("Enter Password");
      $("#p1_error").show();
      $("#psw").css("border-color", "red");
      return false;
    }
    if ($("#psw").val() != $("#psw_repeat").val()) {
      $("#p_error").html("Passwords do not match");
      $("#p_error").show();
      $("#psw_repeat").css("border-color", "red");
      return false;
    }
  });
  $("#uID").focus(function (e) {
    $("#uID_error").hide();
    $("#uID").css("border-color", "");
  });
  $("#fname").focus(function (e) {
    $("#fname_error").hide();
    $("#fname").css("border-color", "");
  });
  $("#lname").focus(function (e) {
    $("#lname_error").hide();
    $("#lname").css("border-color", "");
  });

  $("#psw_repeat").focus(function (e) {
    $("#p_error").hide();
    $("#psw_repeat").css("border-color", "");
  });
  $("#psw").focus(function (e) {
    $("#p1_error").hide();
    $("#psw").css("border-color", "");
  });
});
