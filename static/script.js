//var cameras = new Array(); //create empty array to later insert available devices navigator.mediaDevices.enumerateDevices() // get the available devices found in the machine .then(function(devices) { devices.forEach(function(device) { if(device.kind=== "videoinput"){ //filter video devices only cameras.push(device.deviceId);// save the camera id's in the camera array } }) });
var attachWebcam = function() {
    var width = 640;
    var height = 480;

    if(screen.width < screen.height) {
      width = 480;
      height = 640;
    }

    Webcam.set({
      width: width,
      height: height,
      dest_width: width,
      dest_height: height,
      crop_width: width,
      crop_height: height
    });

    Webcam.set('constraints', {
      facingMode: "environment"
    })
    Webcam.attach('#my_camera');
};

window.addEventListener('orientationchange', function() {
    Webcam.reset();
    attachWebcam();
});
var tmp = '';
attachWebcam();
function take_snap() {
  if(!(Webcam.preview_active)) {
    Webcam.snap(function (data_uri) {
      tmp = data_uri;
    });
    Webcam.freeze();
  }
};
function retake() {
  tmp = ''
  Webcam.unfreeze();
};
var data = '';
function process() {
    if(Webcam.preview_active) {
    var fd = new FormData();
    fd.append('imgdata', tmp.replace(/^data:image\/[a-z]+;base64,/, ""));
    $.ajax({
       type: 'POST',
       url: '/postmethod',
       data: fd,
       processData: false,
       contentType: false
    }).done(function(err,req,resp) {
          if($("#results").length > 0) {
            var resultsdiv = document.getElementById("results")
            resultsdiv.remove();
          }
          data = resp["responseJSON"]["data"];
          var con = document.getElementById('resultsholder');
          con.innerHTML += "<div id=\"results\"><h3 id=\"resultheader\">Result :</h3><img id=\"playbtn\"src=\"/static/play.png\" onClick = \"play(data)\"><p id=\"resultdata\">"+ data +"</p></div>"
    });
  };
};
function play(data) {
    if(window.speechSynthesis.speaking) {
         window.speechSynthesis.cancel();
    }
    else {
        var pat = new RegExp("/<b>|</b>|<br>|</br>/", "g");
        data = data.replace(pat, '');
        data = data.replaceAll("</br>","");
        data = data.replaceAll("<b>","");
        console.log(data);
        var msg = new SpeechSynthesisUtterance(data);
        speechSynthesis.speak(msg);
    }
}