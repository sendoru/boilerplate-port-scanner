import socket
import asyncio
from asyncio import open_connection
from common_ports import ports_and_services

async def is_port_open(target: str, port: int):
    async def subroutine():
        try:
            reader, writer = await open_connection(target, port)
            writer.close()
            await writer.wait_closed()
            return True
        except:
            return False
    try:
        res = await asyncio.wait_for(subroutine(), timeout=3)
        return res
    except:
        return False

def is_ip_format(ip: str):
    ip = ip.split('.')
    if len(ip) != 4:
        return False
    for i in ip:
        if not i.isdigit():
            return False
        
    return True

def is_valid_ip(ip: str):
    try:
        socket.inet_aton(ip)
        return True
    except:
        return False

def is_valid_hostname(hostname: str):
    try:
        socket.gethostbyname(hostname)
        return True
    except:
        return False

def get_open_ports(target: str, port_range: list[int], verbose:bool = False):
    if not is_ip_format(target) and not is_valid_hostname(target):
        return "Error: Invalid hostname"
    if is_ip_format(target) and not is_valid_ip(target):
        return "Error: Invalid IP address"
    
    open_ports = []
    ports = range(port_range[0], port_range[1] + 1)

    async def subroutine():
        coroutines = [is_port_open(target, port) for port in ports]
        results = await asyncio.gather(*coroutines)
        return results

    results = asyncio.run(subroutine())

    for port, result in zip(ports, results):
        if result:
            open_ports.append(port)

    if not verbose:
        return(open_ports)

    ret = []
    if is_ip_format(target):
        try:
            dns = socket.gethostbyaddr(target)
            ret.append(f"Open ports for {dns[0]} ({target})")
        except:
            ret.append(f"Open ports for {target}")
    else:
        ip = socket.gethostbyname(target)
        ret.append(f"Open ports for {target} ({ip})")
    ret.append("PORT     SERVICE")
    for port in open_ports:
        service = ports_and_services.get(port, "")
        ret.append(f"{port:<9}{service}")
    return '\n'.join(ret)