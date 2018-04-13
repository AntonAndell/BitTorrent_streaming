var connButton = document.getElementById("connButton");
connButton.addEventListener("click", doConnect, false);

function doConnect() {
    var theSocketId = 0;
    console.log("connect")

    var tcp = chrome.sockets.tcp;
    /*
    tcp.create(null, function(createInfo) {
        alert(createInfo.socketId);
        theSocketId = createInfo.socketId;
    });
    tcp.connect(theSocketId, "http://www.yahoo.com", 80, function(result) {
        alert(result);
    });
    tcp.read(theSocketId, 1000, function(readInfo) {
        alert(readInfo.resultCode);
    });
  */
}