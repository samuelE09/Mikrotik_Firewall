""" 
/ip firewall address-list print where address=192.168.1.100
/ip firewall address-list remove [find address="192.168.1.100"]
/ip firewall address-list add address=192.168.1.100 list=allowed
"""

import ros_api
import paramiko
import configparser
from prettytable import PrettyTable


def conexion_rosapi(ip,user,password, port):
    try:
        router = ros_api.Api(f'{ip}', user=f'{user}', password=f'{password}', port=port)
        return router
    except:
        print("Conexion no establecida")
        
def conexion_paramiko(ip,user,password,port):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(f"{ip}", username=f"{user}", password=f"{password}")
        return client
    except:
        return "Conexión Falló"
    
def add_ip_to_list(client,add_ip,ip_to_list):
    try:
        stdin, stdout, stderr = client.exec_command(f"/ip firewall address-list add address={add_ip} list={ip_to_list}") 
        client.close()
        return "Se agregó Ip Satisfactoriamente"
    except :
        return "No se pudo Agregar"
    
def remove_ip_to_list(client, remove_ip, remove_to_list=""):
    try:
        if remove_to_list != "": 
            stdin, stdout, stderr = client.exec_command(f'/ip firewall address-list remove [find address="{remove_ip}"]')
            stdin, stdout, stderr = client.exec_command(f'/ip firewall address-list add address={remove_ip} list={remove_to_list}')
            client.close()
            return "Se agregó Movio Satisfactoriamente"
        else:
            stdin, stdout, stderr = client.exec_command(f'/ip firewall address-list remove [find address="{remove_ip}"]')
            return "Se Eliminó Satisfactoriamente"
            
    
    except :
        return "No se pudo Mover"   
        
    
def firewall_address_list(con):
    r = con.talk('/ip/firewall/address-list/print')
    list_count = {}
    for item in r:
        if item["list"] not in list_count:
            list_count[item["list"]] = 1
        else:
            list_count[item["list"]] += 1
    table = PrettyTable()
    # Añade las columnas de índice y list
    table.add_column("#", range(1, len(list_count) + 1))
    table.add_column("List", [key for key in list_count.keys()])
    table.add_column("Count Address", [value for value in list_count.values()])
    
    return r,table,list_count

def listar_ips(buscado):
    table = PrettyTable()
    # Añade las columnas de índice y list
    table.add_column("#", range(1, len(buscado) + 1))
    table.add_column("Address", [item["address"] for item in buscado])
    table.add_column("Comment", [item.get("comment", "N/A") for item in buscado])
    
    return table



if __name__ == "__main__":
    print("Bienvenidos")
    opciones = {"1":"Address List Firewall",
                "2":"Agregar IP a Address List",
                "3":"Mover Ip a Otra Address List",
                "4":"Listar Direcciones IP",
                "5": "Salir"}
    print('\n'.join(f"{id}:{valor}" for id, valor in opciones.items()))
    
    config = configparser.ConfigParser()
    config.read('settings.ini')    
    ip = config.get("configuracion", "direccion_ip")
    user = config.get("configuracion", "usuario")
    password = config.get("configuracion", "pass")
    port = config.get("configuracion", "puerto")  
    
    resp = input("Que va hacer el dia de Hoy : ")
    print("=======================================\n")
    if resp in opciones:
        if resp == "1":
            con = conexion_rosapi(ip,user,password,port)  
            r,table,list_count = firewall_address_list(con)
            print("Listas Registradas en tu Mikrotik")
            print(table)
            print(f"Total Listas : {len(list_count)}")
            print(f"Total Address : {len(r)}")

            
        elif resp == "2":
            add_ip= input("Cual es la Ip que vas a Agregar : ")
            con = conexion_rosapi(ip,user,password,port)  
            r,table,list_count = firewall_address_list(con)
            print("Listas Registradas en tu Mikrotik")
            print(table)
            print(f"Total Listas : {len(list_count)}")
            print(f"Total Address : {len(r)}")

            ip_to_list = input("Coloca el nombre de la lista: ")
            client = conexion_paramiko(ip,user,password,port)
            resultado = add_ip_to_list(client,add_ip,ip_to_list)
            print(f"\n{resultado}")
            
        elif resp == "3":
            remove_ip= input("Cual es la Ip que vas a Mover : ")
            con = conexion_rosapi(ip,user,password,port)  
            r,table,list_count = firewall_address_list(con)
            
            buscado = list(filter(lambda x: x["address"] == remove_ip, r))
            
            print(f'La Ip {buscado[0]["address"]}, se encuentra en {buscado[0]["list"]}\n')
            print(table)
            print(f"Total Listas : {len(list_count)}")
            print(f"Total Address : {len(r)}")
            remove_to_list= input("\nA que lista desea mover? : ")
            client = conexion_paramiko(ip,user,password,port)
            resultado = remove_ip_to_list(client, remove_ip, remove_to_list)
            print(f"\n{resultado}")
            
        elif resp == "4":
            con = conexion_rosapi(ip,user,password,port)  
            r,table,list_count = firewall_address_list(con)
            print(f"{table}")
            print(f"Total Listas : {len(list_count)}")
            print(f"Total Address : {len(r)}")
            lista_ips= input("\nQue lista quieres Visualizar : ")
            buscado = list(filter(lambda x: x["list"] == lista_ips, r))
            print(f"\n Direcciones IP de la Lista '{lista_ips}'")
            tabla_ip =listar_ips(buscado)
            print(tabla_ip)
            print(f"Total {len(buscado)}")

    else:
        print("Opcion no valida")