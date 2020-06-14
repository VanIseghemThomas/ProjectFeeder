`use strict`
//Global variables
let socket;

let container_capacity = 300 //In grams
let container_height = 202 //In milimeters

let hostname;

//HTML references
let html_settings, html_interface, html_slider, html_ip,html_ip_list, html_connect;

const map_to_range = function(num, in_min, in_max, out_min, out_max) {
    return (num - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

const showSliderValue = function(){
    let label = document.querySelector('.js-amount-label');
    label.innerHTML = `<strong>Set amount: </strong>${html_slider.value}g`
}

const showInterface = function(){
    html_interface.style.display = "flex";
    html_settings.style.display = "none";

    
    //Handle slider input
    showSliderValue();
    listenToSlider();

    //Handle button
    listenToButton();
}

const showStatus = function(response){
    //-----------CONTAINER STATUS--------------
    let dist = 0
    //Get last TOF measurement
    for(let m of response.measurements){
        //Search for sensorid 3 = TOF sensor
        if(m.sensorid == 3){
            dist = m.value
            break
        }
    }
    
    //Offset sensor to top container aprox. 20mm
    //200mm = 0, 20 = 1
    let filled = 1 - map_to_range(dist, 20, container_height-20, 0, 1) //Checks distance to top op container and calculates percentage
    if(filled < 0){
        filled = 0;
    }
    else if(filled > 1){
        filled = 1
    }
    let filled_perc = filled*100 //Remove decimal places and represent in percentage
    let filled_weight = container_capacity * filled

    document.querySelector('.js-container').innerHTML = `${filled_perc.toFixed(2)}%`;

    //Container graphic
    document.querySelector('.js-bar').style.width = `${filled_perc}%`;
}

const listenToInputIp = function(e){
    console.log('listening to ip input');
    html_connect.addEventListener('click', function(){

        //Get ip from input
        let ip = html_ip.value;
        //Try to connect to it
        connectToSocket(ip);
    });
}

const listenToSlider = function(){
    html_slider.addEventListener('input', function(){
        showSliderValue();
    })
}

const listenToButton = function(){
    //Get the popup's button element
    let btn = document.querySelector('.js-feed');
    btn.addEventListener('click', function(){
        amount = html_slider.value;
        socket.emit('F2B_feed', {'amount': amount});
    });  
}


const connectToSocket = function(ip){
    if(socket != null){        console.log('disposing previous connection')
        socket.close();
    }
    let host = `http://${ip}:5000`
    socket = io(host);
    console.log(`Connecting to: ${host}`);
    document.querySelector('.js-input-ip_message').innerHTML = "Connecting...";
    listenToSocket(ip);
}

const listenToSocket = function(ip){
    socket.on("connect", function () {
        //Hier nog systeem implementeren om aangepaste response van feeder te krijgen
        //Eerst in backend een emit toevoegen 
        console.log("popup extensie met socket webserver verbonden");
        hostname = ip;
        showInterface();
        getStatus();
        socket.on("B2F_feeding", function(){
            getStatus();
        })
    });
    socket.on('reconnect_attempt', function(){
        document.querySelector('.js-input-ip_message').innerHTML = "Failed to connect, retrying...";
    });
}

const getStatus = function(){
    handleData(`http://${hostname}:5000/api/v1/events/measurements`, showStatus);
}

const getHosts = function(){
    console.log('Looking for hosts on LAN...');
    let startIP = "192.168";
    let ips = []
    
    for(let n1 = 0; n1 < 3; n1++){
        for(let n2 = 2; n2 < 255; n2++){
            handleData(`http://${startIP}.${n1}.${n2}:5000/api/v1/discover`, function(response){
                try{
                    if(response.status == "Feeder available!"){
                        if(ips.length == 0){
                            //Delete searching text
                            html_ip_list.innerHTML = "";
                        }
                        //Save Ip in array
                        ips.push(`${startIP}.${n1}.${n2}`);

                        //Display while loading
                        //Get current html and append with new IP
                        let currentList = html_ip_list.innerHTML;
                        currentList += `${startIP}.${n1}.${n2}`;
                        html_ip_list.innerHTML = currentList;
                    }
                }
                catch{
                    //Next
                }
            });
        }
    }
}

document.addEventListener("DOMContentLoaded", function () {
    html_settings = document.querySelector('.c-settings');
    html_interface = document.querySelector('.c-controls');
    html_ip = document.querySelector('.js-input-ip');
    html_connect = document.querySelector('.js-connect');
    html_slider = document.querySelector('.js-slider');
    html_ip_list = document.querySelector('.js-discovered');

    //Disable interface first
    html_interface.style.display = "none";

    //Handle ip input
    listenToInputIp();
    //Discover Feeder hosts
    //getHosts();
});
