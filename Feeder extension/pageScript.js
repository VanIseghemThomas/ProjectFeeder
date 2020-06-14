// 2. This code loads the IFrame Player API code asynchronously.
console.log('script injected to page');

window.addEventListener('GO', function(event) {
    console.log("Feeding...")
    socket.emit("F2B_feed");
});
