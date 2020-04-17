import time, automationhat, sys, numpy as np, json, os
from Hologram.HologramCloud import HologramCloud
from scripts import hologram_modem
from Hologram.CustomCloud import CustomCloud

time.sleep(.01)
refreshrate = 300

while True:
        automationhat.light.power.on()
        #Grabs Voltage and Moisture
        voltage=automationhat.analog.one.read()
        moisture=(automationhat.analog.two.read()/3.3)

        #Temperature Logic
        #Thermister Constants
        A=0.0021085
        B=0.00007979
        C=0.0000006535
        vin=automationhat.analog.three.read()
        r2=5400
        r1 = (((5/vin)-1)*r2)
        tempc = (1/(A+(B*(np.log(r1)))+(C*((np.log(r1))**3))))
        tempf = ((tempc-273)*(9/5))+32
        tempf = (float("{0:.2f}".format(tempf)))
        print("Temperature: "+str(tempf) + "°F")

        #Voltage Logic
        if voltage<=10: #Battery below 10V
                automationhat.light.warn.on()
                print("Warning: Voltage Low")
                print("Voltage: " +  str(voltage) + "V" )
        else:
                automationhat.light.warn.off()
                print("Voltage: " + str(voltage) + "V")

        #Moisture Logic
        moisturepercent = moisture*100
        moisturepercent = (float("{0:.2f}".format(moisturepercent)))
        print("Soil Moisture Percentage: " + str(moisturepercent) + "%")

	#Grabs location data according to cell service
	cloud = CustomCloud(None, network='cellular')
	location_obj = cloud.network.location
	t = hologram_modem.convert_location_into_json(location_obj)
	
	#Grabs Latitude and Longitude from location data
	latitude = (float(t[60:70]))
	longitude = (float(t[87:98]))

        #Constructs payload of information to be sent
        payload = {"Voltage":voltage,"Moisture":moisturepercent,"Temperature":tempf,"Latitude":latitude,"Longitude":longitude)}
        
	#Prints Kind of Internet Connection
        hologram = HologramCloud(dict(), network='cellular')
        print('Cloud type: ' + str(hologram))
        
	#Sends Moisture and Voltage to Hologram
        recv=hologram.sendMessage(json.dumps(payload))
        
	# Prints ('Message sent successfully') if message sent succesfully
        print('RESPONSE MESSAGE: ' + hologram.getResultString(recv))
		
	#Turns on Comms Light if succesfully sent
	if hologram.getResultString(recv)==1:
		automationhat.light.comms.on()
		
	#Waits to send data again
        time.sleep(refreshrate)
