
//This function enables all of the fields for creating a new institution
function enableSchoolFields(chkbx) {
    //if the checkbox is checked, make all institution fields required
    //and make them visible
    if (chkbx.checked) {
        var fs = document.getElementById('schoolfields');
        var fields = fs.getElementsByTagName('input');
        for (var i = fields.length; i-->0;) {
        fields[i].required=true;
        }
        fs.disabled = false;
    //otherwise make all fields not required and disablethem
    } else {
        var fs = document.getElementById('schoolfields');
        var fields = fs.getElementsByTagName('input');
        for (var i = fields.length; i-->0;) {
         fields[i].required=false;
        }
        fs.disabled = true;
    }
}
  //simple passwordchecker to make sure that passwords match
function checkPassword() {
    var pw1 = document.getElementById("pw1");
    var pw2 = document.getElementById("pw2");
    var message = document.getElementById("confirmMessage");
    var btn = document.getElementById("registerButton")
    if((pw1.value == pw2.value) && (pw1.value.length > 0) && (pw2.value.length > 0)) {
      message.style.background = "#5da423";
      message.innerHTML = "Passwords match!"
      btn.disabled = false
    } else {
      message.style.background = "#c60f13"
      message.innerHTML = "Passwords do not match!"
      btn.disabled = true
    }
}