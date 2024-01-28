let seconds = 00;
let minutes = 00;
let hours = 00;
let ID = null;

function stopwatch() {
    seconds++;
    if (seconds == 60) {
        seconds = 0;
        minutes++;

        if (minutes == 60) {
            minutes = 0;
            hours++;
        }
    }
    displayTime(hours, minutes, seconds);

}

function displayTime(hours, minutes, seconds) {
    const dHours = document.getElementById("hours");
    const dMin = document.getElementById("minutes");
    const dSec = document.getElementById("seconds");

    dHours.innerHTML = hours < 10 ? "0" + hours : hours;
    dMin.innerHTML = minutes < 10 ? "0" + minutes : minutes;
    dSec.innerHTML = seconds < 10 ? "0" + seconds : seconds;
}

function startWatch() {
    ID = setInterval(stopwatch, 1000);
    document.getElementById("start").disabled = true;
}

function pauseWatch() {
    clearInterval(ID);
    document.getElementById("start").disabled = false;
}

function resetWatch() {
    clearInterval(ID);

    // Help required from CS50 AJAX shorts and logic from ChatGPT
    const xhr = new XMLHttpRequest();
    xhr.open("POST", '/timer', true);
    xhr.setRequestHeader("Content-Type", 'application/json');

    const data = {
        hours: hours,
        minutes: minutes,
        seconds: seconds
    };

    xhr.send(JSON.stringify(data));

    // resetting the time values
    [hours, minutes, seconds] = [0, 0, 0];

    displayTime(hours, minutes, seconds);
    // startWatch();
    pauseWatch();
}
