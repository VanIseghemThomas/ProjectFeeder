"use strict";
let menuOpen = false;

let days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

//Setting container values
let container_capacity = 300 //In grams
let container_height = 202 //In milimeters

//Eating data to access globaly
let converted_labels = [];
let converted_stats = [];

const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

let html_btn_feed, html_btn_menu, html_events, html_presets, html_slider, html_data, html_data_graph;

//Moet via backend nog opgevraagd worden
let ip = window.location.hostname;
let ap = "Wifi accesspoint (Placeholder)"

const format_time = function(date){
    return (`${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`);
}

const format_date = function(date){
    return (`${date.getDate()}/${date.getMonth()+1}/${date.getFullYear()}`);
}

const map_to_range = function(num, in_min, in_max, out_min, out_max) {
    return (num - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

const lookForLastSession = function(measurements){
    let dt_finished = null
    let dt_init = null
    let last_index = null;

    let gmt_utc_offset = new Date(0)
    gmt_utc_offset.setHours(3)

    

    for(let m of measurements){
        //Search for sensorid 2 = IR Sensor
        if(m.sensorid == 2){
            //Look for timestamp when pet stopped eating
            if(dt_finished == null && m.value == 0){
                dt_finished = new Date(m.timestamp);
                dt_finished.setTime(dt_finished.getTime()-gmt_utc_offset.getTime());
            }

            //Look for timestamp where pet started the session
            if(dt_finished != null && dt_init == null && m.value == 1){
                let time = new Date(m.timestamp);
                time.setTime(time.getTime()-gmt_utc_offset.getTime());
                let diff =(dt_finished.getTime() - time.getTime()) / 1000;
                diff = Math.abs(Math.round(diff));

                //Only accept as eating session when time is longer than 10 seconds
                if(diff > 10){
                    dt_init = time;
                    last_index = measurements.indexOf(m);
                }
            }
            //When both timestamps are found, stop looking
            if(dt_finished != null && dt_init != null){
                break
            }
        }
    }

    //Calculate the difference in time (seconds)
    let diff =(dt_finished.getTime() - dt_init.getTime()) / 1000;
    diff = Math.abs(Math.round(diff));

    let date = new Date(0);
    date.setSeconds(diff); // specify value for SECONDS here
    diff = date.toISOString().substr(11, 8);
    return({"start": dt_init, "end": dt_finished, "delta": diff, "delta_sec":date, "last_index": last_index});
}

const createCSV = function(labels, data, sections){
    let csv = ""
    //Sections in header
    let counter = 0
    for(let section of sections){
        csv += `${section}`
        if(counter < sections.length-1){
            csv += ",";
        }
        counter++;
    }
    csv += `\r\n`

    //Add data rows
    for(let i = 0; i < labels.length; i++){
        csv += `"${labels[i]}",${data[i]}\r\n`
    }

    socket.emit("F2B_create_csv", {'string': csv});
}


function downloadFile(dataurl, filename) {
    var a = document.createElement("a");
    a.href = dataurl;
    a.setAttribute("download", filename);
    a.click();
}

const disableFeed = function(){
    html_btn_feed.innerHTML = "Feeding..."
    html_btn_feed.disabled = true;
    html_btn_feed.classList.add("o-button--feeding");
    
}

const callbackDeletePreset = function(response){
    console.log('Preset deleted: ', response);
    getPresets();
}

const callbackAddPreset = function(response){
    console.log('Preset created: ', response);
    getPresets();
}

const drawChart = function(labels, data, title){
    let ctx = html_data_graph.getContext('2d');
    let config = {
        type: 'line',
        data:{
            labels: labels,
            datasets:[
                {
                    label: title,
                    backgroundColor: '#F2E9E2',
                    borderColor: '#675F66',
                    data: data,
                    fill: false
                }
            ]
            
        },
        options:{
            responsive: true,
            maintainAspectRatio: false, 
            
            title: {
                display: false,
                text: ''
            },
            tooltips: {
                mode: 'index',
                intersect: true
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
  
            scales: {
                xAxes:[
                    {
                        display: false,
                        scaleLabel: {
                            display: true,
                            labelString: 'Day'
                        }
                    }
                ],
                yAxes:[
                    {
                        display: true,
                        scaleLabel: {
                            display: false,
                            labelString: 'Time (Seconds)'
                        }
                    }
                ]
            }
        }
    };
    let activeChart = new Chart(ctx, config)
}

const showMenu = function(){
    let menu = document.querySelector('.js-menu');
    if(menuOpen){
        menu.classList.remove('c-header__nav-show');
        menu.classList.remove('o-layout__item');
        menuOpen = false;
    }
    else{
        menu.classList.add('c-header__nav-show');
        menu.classList.add('o-layout__item');
        menuOpen = true;
    }
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
    let bar_height = document.querySelector('.js-container-bar').clientHeight
    document.querySelector('.c-bar-bottom').style.height = `${bar_height * (filled)}px`;

    //-----------LAST TIME EATEN--------------

    let dt_finished = null
    let dt_init = null

    let gmt_utc_offset = new Date(0)
    gmt_utc_offset.setHours(3)

    for(let m of response.measurements){
        //Search for sensorid 2 = IR Sensor
        if(m.sensorid == 2){
            //Look for timestamp when pet stopped eating
            if(dt_finished == null && m.value == 0){
                dt_finished = new Date(m.timestamp);
                dt_finished.setTime(dt_finished.getTime()-gmt_utc_offset.getTime());
            }

            //Look for timestamp where pet started the session
            if(dt_finished != null && dt_init == null && m.value == 1){
                let time = new Date(m.timestamp);
                time.setTime(time.getTime()-gmt_utc_offset.getTime());
                let diff =(dt_finished.getTime() - time.getTime()) / 1000;
                diff = Math.abs(Math.round(diff));

                //Only accept as eating session when time is longer than 10 seconds
                if(diff > 10){
                    dt_init = time
                }
            }
            //When both timestamps are found, stop looking
            if(dt_finished != null && dt_init != null){
                break
            }
        }
    }

    //Calculate the difference in time (seconds)
    let diff =(dt_finished.getTime() - dt_init.getTime()) / 1000;
    diff = Math.abs(Math.round(diff));

    let date = new Date(0);
    date.setSeconds(diff); // specify value for SECONDS here
    diff = date.toISOString().substr(11, 8);

    //Write to 
    //.log(dt_init, dt_finished);
    let html_string = `<div>${format_date(dt_init)}: ${format_time(dt_init)} --> ${format_time(dt_finished)}</div>`;
    html_string += `Session time: ${diff}`;
    document.querySelector('.js-last-session').innerHTML = html_string;
}

const showMeasurements = function(response){
    let html = `
    <table>
            <tr>
                <th>Timestamp</th>
                <th>Sensor</th>
                <th>Value</th>
                <th>Unit</th>
            </tr>
    `
    let counter = 0
    for(let m of response.measurements){
        let timestamp = m.timestamp;
        let name = m.name;
        let value = m.value;
        let unit = m.unit;

        //Determine color for table row
        if(counter % 2 == 0){
            html += `<tr class="odd">`
        }
        else{
            html += `<tr>`
        }

        //Insert data in table
        html += `
                <td>${timestamp}</td>
                <td>${name}</td>
                <td>${value}</td> 
                <td>${unit}</td>
            </tr>
        `
        counter++;
    }

    html += "</table>"
    html_measurements.innerHTML = html

    //Update status after measurement
    showStatus(response);
}

const showEvents = function(response){
    let html = `
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Value</th>
            <th>Unit</th>
            <th>Schema id</th>
            <th>Sensor</th>
            <th>Actuator</th>
        </tr>
    `
    let counter = 0
    for(let m of response.events){
        let timestamp = m.timestamp;
        let value = m.value;
        let unit = m.unit;
        let schemaid = m.schemaid;
        let sensorid = m.sensorid;
        let actuatorid = m.actuatorid; 

        //Determine color for table row
        if(counter % 2 == 0){
            html += `<tr class="odd">`
        }
        else{
            html += `<tr>`
        }

        //Insert data in table
        html += `
                <td>${timestamp}</td>
                <td>${value}</td> 
                <td>${unit}</td>
                <td>${schemaid}</td>
                <td>${sensorid}</td>
                <td>${actuatorid}</td>
            </tr>
        `
        counter++;
    }

    html += "</table>"
    html_events.innerHTML = html
}

const showPresets = function(response){

    let html_string = '<div class="c-preset o-layout__item o-layout o-layout--justify-space-between o-layout--align-center">'
    for(let s of response.presets){
        let amount = s.amount;
        let dayofweek = s.dayofweek;
        let hour = s.hour;
        let min = s.minute;
        let id = s.presetid

        html_string += 
        `<div class="c-preset o-layout__item o-layout o-layout--justify-space-between o-layout--align-center">
        <div class="o-setting js-preset-setting u-1-of-2">${dayofweek}, ${hour}:${min}h: ${amount}g</div>
        <div class="o-setting u-1-of-2 o-layout o-layout--justify-end">
            <svg data-presetid=${id} class="js-preset-edit" xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24"><path d="M0 0h24v24H0z" fill="none"/><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
            <svg data-presetid=${id} class="js-preset-delete" xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24"><path d="M0 0h24v24H0z" fill="none"/><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
        </div>`
        
        html_string += `<hr class="o-layout__item">
        </div>`
    }
    html_presets.innerHTML = html_string;
    listenToDelete();
    listenToEditPreset();
}

const showVideoFeed = function(data){
    let frame = data.img;
    let html_video = document.querySelector('.js-video');
    html_video.src = `data:image/jpeg;base64,${frame}`;
}

const showSliderValue = function(){
    let label = document.querySelector('.js-amount-label');
    label.innerHTML = `<strong>Set amount: </strong>${html_slider.value}g`
}

const showDataEating = function(response){
    //Chart
    converted_labels = [];
    converted_stats = [];
    
    //Table
    let html_string = `
        <tr class="table-head">
            <th>Time fed</th>
            <th>Time eaten (Seconds)</th>
        </tr>
    `
    let data = response.measurements;

    //Filter events
    let events = []
    for(let m of data){
        try{
            let eatEvent = lookForLastSession(data);
            events.push(eatEvent);
            //Slice data to start after last checked index
            let start_index = eatEvent.last_index+1;
            data = data.slice(start_index, data.length-1);
        }   
        catch{
            break;
        }
    }

    //Display table
    let counter = 0
    for(let e of events){
        let timestamp = new Date(e.start);
        let time = format_date(timestamp) + " at " + format_time(timestamp);
        let delta = e.delta;
        let delta_seconds = new Date(e.delta_sec).getSeconds();
        
        //Determine color for table row
        if(counter % 2 == 0){
            html_string += `<tr class="odd">`;
        }
        else{
            html_string += `<tr>`;
        }

        html_string +=
        `
            <td>${time}h</td>
            <td>${delta_seconds}</td>
        </tr>
        `;
        converted_labels.push(time);
        converted_stats.push(delta_seconds);
        counter++;
    }
    html_data.innerHTML = html_string;

    //Chart
    drawChart(converted_labels, converted_stats, "Time eaten");
    listenToDownload();
}

//#region ***  Data Access - get___ ***
const getEvents = function(){
    handleData(`http://${window.location.hostname}:5000/api/v1/events`, showEvents);
}
const getMeasurements = function(){
    handleData(`http://${window.location.hostname}:5000/api/v1/events/measurements`, showMeasurements);
}
const getDataEating = function(){
    handleData(`http://${window.location.hostname}:5000/api/v1/events/measurements`, showDataEating);
}
const getStatus = function(){
    handleData(`http://${window.location.hostname}:5000/api/v1/events/measurements`, showStatus);
}
const getPresets = function(){
    socket.emit('F2B_edit-preset');
    handleData(`http://${window.location.hostname}:5000/api/v1/presets`, showPresets);
}
//#endregion

//#region ***  Event Listeners - listenTo___ ***
const listenToSocket = function () {
    socket.on("connect", function () {
      console.log("verbonden met socket webserver");
    });
    socket.on("B2F_status", function(){
        console.log("Status");
        getStatus();
        //getMeasurements();
    })
    socket.on("B2F_feeding", function(){
        console.log("Update after feeding");
        getStatus();
        //getMeasurements();
    })
    socket.on("B2F_weight", function(){
        console.log("Weight measurement");
        getEvents();
        //getMeasurements();
    })
    socket.on("B2F_IR-detection", function(){
        console.log("IR detection");
        getStatus();
        //getMeasurements();
    })
    socket.on("B2F_edit-preset", function(){
        console.log("Preset edit!");
        getPresets();
        //getMeasurements();
    })

    socket.on("B2F_video", function(data){
        showVideoFeed(data);
    })

};

const listenToFeed = function(){
    let btn = document.querySelector('.js-feed');
    btn.addEventListener('click', function(){
        let amount = document.querySelector('.js-feed-amount').value;

        console.log("Feeding...");
        socket.emit('F2B_feed', {'amount': amount});
    })
}

const listenToMenu = function(){
    html_btn_menu.addEventListener('click', function(){
        console.log('Opening menu')
        showMenu();
    });
}

const listenToEditPreset = function(){
    let btns = document.querySelectorAll('.js-preset-edit');    
    for(let btn of btns){
        let id = btn.getAttribute('data-schemaid');
        btn.addEventListener('click', function(){
            console.log(id);
        });
    }
}

const listenToDelete = function(){
    
    let btns = document.querySelectorAll('.js-preset-delete');
    for(let btn of btns){
        btn.addEventListener('click', function(){
            let id = this.getAttribute('data-presetid');
            console.log(id);
            handleData(`http://${window.location.hostname}:5000/api/v1/presets/${id}`, callbackDeletePreset, null, 'DELETE');
        });
    }
}

const listenToAddPreset = function(){
    let btn = document.querySelector('.js-create-confirm');
    console.log(btn);

    btn.addEventListener('click', function(){
        console.log('click')
        let dayofweek_index = document.querySelector('.js-create-day').value - 1;
        let dayofweek = days[dayofweek_index];
        let time = document.querySelector('.js-create-time').value.split(':');
        let amount = document.querySelector('.js-create-amount').value;
        let hour = parseInt(time[0]);
        let minute = parseInt(time[1]);

        console.log(document.querySelector('.js-create-time').value)
        
        if(dayofweek != null && hour != null, minute != null && amount != null){
            if(amount <= container_capacity){
                
                let body = `
                {
                    "dayofweek": "${dayofweek}", 
                    "hour": ${hour},
                    "minute": ${minute},
                    "amount": ${amount}
                }`;

                
                handleData(`http://${window.location.hostname}:5000/api/v1/presets`, callbackAddPreset, null, 'POST', body);
            }
            else{
                console.log('Amount too large!');
            }
        }
        else{
            console.log('Fill in all parameters!');
        }
    });
}

const listenToSlider = function(){

    html_slider.addEventListener('input', function(){
        showSliderValue();
    })
}

const listenToDownload = function(){
    let btn = document.querySelector('.js-download');
    btn.addEventListener('click', function(){
        createCSV(converted_labels, converted_stats, ["Time fed", "Time eaten (s)"]);
        socket.on("B2F_download_ready", function(){
            console.log("Downloading CSV");
            downloadFile(`http://${window.location.hostname}:5000/api/v1/data/downloadcsv`, "feeder_data.csv")
        })
    });
}

//#endregion

document.addEventListener("DOMContentLoaded", function () {
    console.info("DOM geladen");

    html_btn_feed = document.querySelector('.js-feed');
    html_btn_menu = document.querySelector('.js-btn-menu');
    html_events = document.querySelector('.js-events');
    html_presets = document.querySelector('.js-presets')
    html_slider = document.querySelector('.js-feed-amount');
    html_data = document.querySelector('.js-data');
    html_data_graph = document.querySelector('.js-chart');

    if(html_btn_feed){
        getStatus();
        
        listenToFeed();
        listenToSocket();
        listenToSlider();

        showSliderValue();

        setInterval(function(){
            socket.emit('F2B_video')
        },500);
    }

    if(html_presets){
        getPresets();
        listenToAddPreset();
    }

    if(html_data){
        getDataEating();
    }

    listenToMenu();
    
  });