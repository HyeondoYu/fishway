const socket = io();

function sendCommand(cmd){
	socket.emit('control', cmd);
}
