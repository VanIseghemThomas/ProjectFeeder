// Add a listener for the browser action
//chrome.browserAction.onClicked.addListener(buttonClicked);


function buttonClicked(tab) {
    // The user clicked the button!
    // 'tab' is an object with information about the current open tab
    //Go to timestamp
    console.log("Clicked");
    var msg = {
        message: "go"
    }
    //This feature enables communication with page
    //chrome.tabs.sendMessage(tab.id, msg);
    amount = 60;
}


