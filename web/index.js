var connButton = document.getElementById("connButton");
connButton.addEventListener("click", doConnect, false);

function doConnect() {
    var theSocketId = 0;
    console.log("connect")
    /*
    chrome.socket.create("tcp", null, function(createInfo) {
        alert(createInfo.socketId);
        theSocketId = createInfo.socketId;
     });
     chrome.socket.connect(theSocketId, "http://www.yahoo.com", 80, function(result) {
        alert(result);
     });
    chrome.socket.read(theSocketId, 1000, function(readInfo) {
      alert(readInfo.resultCode);
  });
  */
  }