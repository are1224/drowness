$(function() {
    $(window).bind("unload", (e) => {
        return confirm('real?');
    });
    
    $('#web_cam').bind('mouseover', (e)=>{
        $('.controller').show()
    });

    $('#web_cam').bind('mouseout', (e)=>{
        $('.controller').hide()
    });

    $('.controller').bind('mouseover', (e)=>{
        $('.controller').show()
    });

    $('.controller').bind('mouseout', (e)=>{
        $('.controller').hide()
    });

});

function printClock(superDate) {
    
    var clock = document.getElementById("clock");            // 출력할 장소 선택
    var currentDate = new Date();                                     // 현재시간
    var calendar = currentDate.getFullYear() + "-" + (currentDate.getMonth()+1) + "-" + currentDate.getDate() // 현재 날짜
    var amPm = 'AM'; // 초기값 AM
    var currentHours = addZeros(currentDate.getHours(),2); 
    var currentMinute = addZeros(currentDate.getMinutes() ,2);
    var currentSeconds =  addZeros(currentDate.getSeconds(),2);
    
    if(currentHours >= 12){ // 시간이 12보다 클 때 PM으로 세팅, 12를 빼줌
        amPm = 'PM';
        currentHours = addZeros(currentHours - 12,2);
    }

    if(currentSeconds >= 50){// 50초 이상일 때 색을 변환해 준다.
        currentSeconds = '<span style="color:#de1951;">'+currentSeconds+'</span>'
    }
    clock.innerHTML = currentHours+":"+currentMinute+":"+currentSeconds +" <span style='font-size:20px;'>"+ amPm+"</span>"; //날짜를 출력해 줌

    var divClock=document.getElementById("divClock");
    var time = (currentDate.getTime() - superDate.getTime())/1000;
    var hour = parseInt(time/3600);
    var min = parseInt((time%3600)/60);
    var sec = parseInt(time%60);

    var msg = "경과시간 : "+(currentDate.getHours()- superDate.getHours())+"시";
    msg += min + "분";
    msg += sec + "초";

    divClock.innerText=msg;
    
    setTimeout(printClock,1000, superDate);         // 1초마다 printClock() 함수 호출
}

function addZeros(num, digit) { // 자릿수 맞춰주기
    var zero = '';
    num = num.toString();
    if (num.length < digit) {
        for (i = 0; i < digit - num.length; i++) {
        zero += '0';
        }
    }
    return zero + num;
}
