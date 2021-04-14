

const socket = io();
var img = document.getElementById('imgDiv');
socket.on('imgChannel',(data)=>{
	//console.log(data)
    img.src = "data:image/jpg;base64, " + data.data;
})
