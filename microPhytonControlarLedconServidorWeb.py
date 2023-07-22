'''
    * Este programa controla unos LED´s usan un Servidro Web
'''

from machine import Pin, reset
import network
import socket
import time
import esp
import gc

esp.osdebug(None)  #Deshabilitar la salida de depuración
gc.collect() #Recupera la memoria ocupada por objetos que no son necesarios para el programa

#Conexión WiFi

ssid = 'INFINITUM5B71'  #Datos SSID y contraseña de la red WI-FI a las que se va a conectar
key = 'd6R9tC9TsA'

led_salida_indicador = Pin(2, Pin.OUT)  #Se estable la salida del LED que indicará la conexión
wlan = network.WLAN(network.STA_IF)  #Se crea el objeto de tipo network y se configura para conectarse a una red wifi
if not wlan.isconnected(): #sino hay conexión entra en la condición
    wlan.active(True)  #Incia la conexión
    wlan.connect(ssid, key)  #Envía los parámetros necesarios para conectarse
    print('Conectando a: %s' % ssid)  #Manda mensaje indicando la red que se va a conectar
    timeout = time.ticks_ms()  # tiempo que lleva el microcontrolador encendido en milisegundos

    while not wlan.isconnected():  #sino se ha establecido conexión entra al ciclo
        led_salida_indicador.on()  #va a encender y apagar el LED indicador hasta que se establezca conexión
        time.sleep(0.15)
        led_salida_indicador.off()
        time.sleep(0.15)
        if (time.ticks_diff (time.ticks_ms(), timeout) > 10000):  # Si el tiempo de espera sobrepasa los 10 segundos, sel ciclo se interrumpe
            break

    if wlan.isconnected():  #si se establece conexión, entra a la condición
        led_salida_indicador.on()  #una vez que se establece conexión, el LED se queda encendido
        print('Conexión establecida: %s' % ssid)
        print('IP: %snSUBNET: %snGATEWAY: %snDNS: %s' % wlan.ifconfig()[0:4]) #imprime la configuracion de red
    else:
        led_salida_indicador.off()  #si la conexión no se establece
        wlan.active(False)  #se finaliza la conexión
        print('Falló la conexión a: %s' % ssid)  #imprime el mensaje

else:
    led_salida_indicador.on() #si ya hay una conexión previa, solo imprime las parámetros de la conexión
    print('ConnectednIP: %snSUBNET: %snGATEWAY: %snDNS: %s' % wlan.ifconfig()[0:4])

#pines de salida para activar cualquier dispositivo
led_salida_motor = Pin(5, Pin.OUT)
led_salida_foco = Pin(21, Pin.OUT)

#Construcción de página web dentro de una función
def web_page():
    html = """
<!DOCTYPE html>
<html>
	<head>
		<title>Esp32 Servidor web</title>
    	<link rel="shortcut icon" href="https://microsulucionesmkz.000webhostapp.com/imagenes/microcontrolador.jpg">
    	<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
    	<meta name="viewport" content="width=device-width, initial-scale=1">
    	<style type="text/css">
	        *{
				padding: 0px; margin: 0px;
			}
			.home{
				padding: 0px 0px 10px 0px; background-color: #000000;
			}
			.nav{
				box-sizing: border-box; display: inline-block;
				padding: 10px 0px 10px 0px; background-color:#063d6d;
				width: 100%; height: auto;
			}
			.control{
				box-sizing: border-box; display: inline-block;
				padding: 0px 0px 15px 0px; background-color: #ffffff;
				border: 4px solid #063d6d; border-radius: 20px;
				width: auto; height: auto; margin: 30px;
			}
			.myline {
		 		border: 2px solid #063d6d;
			}
			#t1{
				font-family: Helvetica; font-weight: bold;
				text-align: center; font-size: 50px; color: white;
			}
			#t2{
				font-family: Helvetica; font-weight: bold;
				text-align: center; font-size: 20px; color: white;
			}
			#t3{
				font-family: Helvetica; font-weight: bold;
				font-size: 30px; color: #063d6d;
			}
			#imag{
				width: 200px; height: 200px; padding: 25px;
			}
			#on{
				border: 4px solid green; border-radius: 20px;
				background-color:white; color: green;
				font-weight: bold; font-size: 20px;
				width: 150px; height: 50px; cursor:pointer;
			}
			#off{
				border: 4px solid red; border-radius: 20px;
				background-color:white; color: red;
				font-weight: bold; font-size: 20px;
				width: 150px; height: 50px; cursor:pointer;
			}
  		</style>
	</head>
	<body>
        <div class='nav'>
            <h1 id='t1'>Servidor Web-ESP32</h1>
            <p id='t2'>Para mas información visita: <a id='t2' href="https://github.com/MrcGbrl/2-miroPhytonServidorWebEsp32" target="_blank" title="Go to
                           https://github.com/MrcGbrl/2-miroPhytonServidorWebEsp32">Proyecto completo en GitHub</a></p>
        </div>

        <div class="home">
            <center>
                <div class="control">
                    <img id="imag" src="https://microsulucionesmkz.000webhostapp.com/imagenes/foco.jpg" alt="img">
                    <hr class="myline"><br /> &ensp;
                    <button id='on' type="button" onclick="window.location.href='/?control1=on'">ON</button> &ensp;
                    <button id='off' type="button" onclick="window.location.href='/?control1=off'">OFF</button> &ensp;
                </div>
                <div class="control">
                    <img id="imag" src="https://microsulucionesmkz.000webhostapp.com/imagenes/motor.jpg" alt="img">
                    <hr class="myline"><br /> &ensp;
                    <button id='on' type="button" onclick="window.location.href='/?control2=on'">ON</button> &ensp;
                    <button id='off' type="button" onclick="window.location.href='/?control2=off'">OFF</button> &ensp;
                </div>
            </center>
        </div>
	</body>
</html>
"""
    return html

#Socket Configuration
try:
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # crear un objeto tipo socket INET, STREAMing
    tcp_socket.bind(('', 80))  # vincula el socket a un host público y un puerto conocido
    tcp_socket.listen(5)  # convierte en un socket servidor con cola de 5 clientes máximo
    time.sleep(1)
    print('Configuración de socket exitosa\n')
except OSError as e:
    print('No se pudo configurar el socket. Reiniciando...\n')
    time.sleep(3)
    reset()  #Restablece el socket al estado inicial
print('Listo...!\n********************************\n')
while True:
    try:
        if gc.mem_free() < 102000:  #Devuelve el número de bytes de memoria RAM disponible y lo compara
            gc.collect()   #libera memoria al ejecutar una recolección de basura.
        conn, addr = tcp_socket.accept()  #conn es un nuevo objeto de socket que se puede usar para enviar y recibir datos en la conexión
                                          #addr es la dirección vinculada al socket en el otro extremo de la conexión (host)
        conn.settimeout(3.0)  #Establece un tiempo de espera para bloquear las operaciones de socket
        print('Nueva conexión de: %s' % str(addr[0]))  #cliente conectado
        request = conn.recv(1024)  #Recibe datos del socket. El valor devuelto es un objeto de bytes que representa los datos recibidos, especifica la cantidad máxima de datos que se pueden recibir a la vez
        conn.settimeout(None)
        peticion = str(request)  #Convierte la solicitud en una cadena de texto y la guara en respuesta
        #print('Request:  %s' % request)
        if peticion.find('/?control1=on') == 6:  #busca dentro de la peticon la cadena y si la encuentra, toma un valor 6
            print('led_salida_motor: ON')
            led_salida_motor.value(1)
        if peticion.find('/?control1=off') == 6:  #debe comparar con 6 para cumplir la instrucción
            print('led_salida_motor: OFF')
            led_salida_motor.value(0)
        if peticion.find('/?control2=on') == 6:
            print('led_salida_foco: ON')
            led_salida_foco.value(1)
        if peticion.find('/?control2=off') == 6:
            print('led_salida_foco: OFF')
            led_salida_foco.value(0)
        conn.send('HTTP/1.1 200 OKn')
        conn.send('Content-Type: text/htmln')
        conn.send('Connection: closenn')
        conn.sendall(web_page())
        conn.close()
    except OSError as e:
        conn.close()
    time.sleep(0.1)
