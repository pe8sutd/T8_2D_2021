# coding=utf-8
"""
#########Readme##########
Please Install the Pyserial via "pip install pyserial"
Connect two bluetooth modules to 2 USB-UART module which connect to PC and both of leds on the Bluetooth module should blink.
For the first time, Connect the Programmer to the PC, Please Enable CheckUart. You will find out 2 UART port COMXX and COMYY.
Set them as Programmers of Master Bluetooth Module and Slave Moudle accordingly (e.g. Port_M = "COMXX" Port_S = "COMYY") and Disable CheckUART. 
Then Enable the Configure = 1 which means two bluetooth modules will autoamaticly configured with a random PIN Number.
If you would like to check whether or not BLE modules were configured properaly, please disable Configure = 0,
reconnect with the same USB port(2 leds always on). Run and the programe will automaticly check the connnection within two BLE modules.
"""
import serial
import serial.tools.list_ports
import random
from time import sleep

CheckUART = 0
Configure = 0
Port_M = "COM11"
Port_S = "COM5"
BLE_Name = "Atlas200dk"

class HC08(serial.Serial):
    SetMaster = "AT+ROLE=M"
    SetSlaver = "AT+ROLE=S"
    QRole = "AT+ROLE?"
    RequestAddr="AT+ADDR?"
    QBind = "AT+BIND?"
    QName = "AT+NAME?"
    UART="AT+UART=9600,1,0"
    QUART = "AT+UART?"
    SetLUUID = "AT+LUUID="
    SetSUUID = "AT+SUUID="
    SetTUUID="AT+TUUID="
    # CMD (respone 1 line) Enquiry(respone 2 line)
    def __init__(self,portx,bps,tdelay = 5,UUID ="1234"):
        super(HC08, self).__init__(portx,bps,timeout=tdelay)
        print(portx, bps)
        if UUID=="1234" or (not(isinstance(UUID,str) and (len(UUID) ==4))):
            self.LUUID=self.SUUID=self.TUUID=hex(random.randint(0x1000,0xFFFF))[2:6]
        else:
            self.LUUID=self.SUUID=self.TUUID=UUID
        print("LUUID,TUUID,SUUID is:",self.LUUID)
        
    def CheckAT(self):
        self.write("AT".encode("utf-8"))
        sleep(0.05)
        Response = self.readline().decode("utf-8")
        if Response == "OK":
            return True
        else:
            return False
            
    def WriteCMD(self,CMD):
        self.write(CMD.encode("utf-8"))
        sleep(0.1)
        print(self.readline().decode())

    def Enquiry(self,CMD):
        self.write(CMD.encode("utf-8"))
        sleep(0.1)
        print(self.readline())

    def Reset(self):
        self.write("AT+RESET".encode("utf-8"))
        sleep(0.5)
        print("Reset:"+self.readline().decode("utf-8"))
        
    def ClearAddr(self):
        self.write("AT+CLEAR".encode("utf-8"))
        sleep(0.3)
        print("Clear Address:"+self.readline().decode("utf-8"))
                
    def ReadRole(self):
        self.Enquiry(self.QRole)

    def ReadSTATE(self):
        self.write("AT+RX".encode("utf-8"))
        sleep(0.1)
        for i in range(5):
            print(self.readline())

    def SetUUID(self,CMD):
        self.write(CMD.encode("utf-8"))
        # print(self.readline().decode("utf-8"))

    def ConfigureAsSlave(self):
        if self.CheckAT():
            pass
        else:
            print("Not AT Mode, Please Reconnected")
            self.close()
            exit(0)
        try:
            self.ClearAddr()
            self.Reset()
            print("Set as Slaver:",end="")
            self.WriteCMD(self.SetSlaver)
            print("Set UUID.\r",end="")
            self.SetUUID(self.SetLUUID + self.LUUID)
            print("Set UUID..\r",end="")
            self.SetUUID(self.SetSUUID+self.SUUID)            
            print("Set UUID...")
            self.SetUUID(self.SetTUUID + self.TUUID)
            print("Set Master BLE Name",end="")
            self.WriteCMD("AT+NAME="+BLE_Name+"_M")
            print("----Configure Successfully----")
        except Exception as e:
            print("---Slave Setting Error---：", e)

    def ConfigureMaster(self):
        if self.CheckAT():
            pass
        else:
            print("Not AT Mode, Please Reconnected")
            self.close()
            exit(0)
        try:
            self.ClearAddr()
            self.Reset()
            print("Set as Master:",end="")
            self.WriteCMD(self.SetMaster)
            print("Set UUID.\r",end="")
            self.SetUUID(self.SetLUUID + self.LUUID)
            print("Set UUID..\r",end="")
            self.SetUUID(self.SetSUUID+self.SUUID)            
            print("Set UUID...")
            self.SetUUID(self.SetTUUID + self.TUUID)
            print("Set Master BLE Name ",end="")
            self.WriteCMD("AT+NAME="+BLE_Name+"_M")
            print("----Configure Successfully----")
        except Exception as e:
            print("---Master Setting Error---：", e)

    def GetUUID(self):
        return self.LUUID

def AutoConfigure():
    BLE_M = HC08(Port_M,9600)
    BLE_S = HC08(Port_S,9600)
    BLE_S.ConfigureAsSlave()
    BLE_M.ConfigureMaster()
    BLE_M.close()
    BLE_S.close()

def AutoMaster(Port,baud=9600):
    BLE_M = HC08(Port,baud)
    BLE_M.ConfigureMaster()
    UID = BLE_M.GetUUID()
    BLE_M.close()
    return UID

def AutoSlave(Port,baud=9600,UID = "1234"):
    BLE_S = HC08(Port,baud,UUID=UID)
    BLE_S.ConfigureAsSlave()
    BLE_S.close()

def AutoTest():
    # COM15-FT 16-CH340
    BLE_M = HC08(Port_M,38400,tdelay =1)
    BLE_S = HC08(Port_S, 38400,tdelay =1)
    if (BLE_M.CheckAT() or BLE_S.CheckAT()):
        print("Still Work in the AT Mode, Please Remove 2 jumper and reconnect the USB")
        exit(0)
        BLE_M.close()
        BLE_S.close()
    else:
        BLE_M.close()
        BLE_S.close()
        BLE_M = HC08(Port_M,9600)
        BLE_S = HC08(Port_S, 9600)

    for i in range(15):
        BLE_S.write((str(i)+"\r\n").encode("utf-8"))
        sleep(0.1)
        Receive = BLE_M.readline().decode("utf-8")
        if Receive != (str(i) + "\r\n"):
            print("\r\nError")
            exit(0)
        else:
            print("Slave->Master:Testing"+(i//5)*'.', end='\r')
    print("")
    for i in range(15):
        BLE_M.write((str(i)+"\r\n").encode("utf-8"))
        sleep(0.1)
        Receive = BLE_S.readline().decode("utf-8")
        if Receive != (str(i) + "\r\n"):
            print("\r\nError")
            exit(0)
        else:
            print("Master->Slave:Testing"+(i//5)*'.',end='\r')

    print("\r\nSuccessful")
    
if __name__ == "__main__":
    if (CheckUART):
        port_list = list(serial.tools.list_ports.comports())
        if len(port_list) == 0:
            print('No UART detected')
        else:
            for i in range(0,len(port_list)):
                print(port_list[i])
    elif (Configure):
        input("Please Connect the Master BLE Module to the PC, and then press \"Enter\"")
        UID = AutoMaster(Port_M)
        print(UID)
        input("Please Disconnect the Master Module from the PC connect the Slaver Module to the PC, and then press \"Enter\"")
        AutoSlave(Port_S,UID = UID)
    else:
        AutoTest()
