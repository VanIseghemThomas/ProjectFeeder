//Injects pagescript
//let tag = document.createElement('script');
//let extension = chrome.extension.getURL('pageScript.js');
//console.log(extension);
//tag.src = extension;
//(document.head || document.documentElement).appendChild(tag);



// Listen for messages
//chrome.runtime.onMessage.addListener(receiver);

// Callback for when a message is received
function receiver(request, sender, sendResponse) {
    if (request.message === "go") {
        console.log("Alerting injected script");
        let event = new CustomEvent('GO');
        window.dispatchEvent(event);
    }
}
