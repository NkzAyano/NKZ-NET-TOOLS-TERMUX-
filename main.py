
import os
import socket
import subprocess
import urllib.request
import json
import platform


RESET = "\033[0m"
PURPLE = "\033[95m"
CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"


def limpar():
    os.system("clear")


def titulo():
    print(PURPLE + r"""
 _   _ _  ______   _   _ _____ _____
| \ | | |/ /__  | | \ | | ____|_   _|
|  \| | ' /  / /  |  \| |  _|   | |
| |\  | . \ / /_  | |\  | |___  | |
|_| \_|_|\_\____| |_| \_|_____| |_|

          NKZ NET TOOLS
""" + RESET)
    print(CYAN + " Ferramentas de diagnostico de rede" + RESET)
    print("-" * 38)


def ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("192.0.2.1", 80))
        ip = s.getsockname()[0]
        s.close()
        print(GREEN + f"IP local: {ip}" + RESET)
    except OSError as e:
        print(RED + f"Nao foi possivel consultar: {e}" + RESET)


def ipv6_local():
    try:
        resultado = socket.getaddrinfo(
            socket.gethostname(), None, socket.AF_INET6
        )
        ips = sorted(set(item[4][0] for item in resultado))
        if ips:
            for ip in ips:
                print(GREEN + f"IPv6: {ip}" + RESET)
        else:
            print(YELLOW + "IPv6 local nao encontrado." + RESET)
    except OSError:
        print(YELLOW + "IPv6 indisponivel ou nao encontrado." + RESET)


def gateway_dns():
    print(CYAN + "\nInformacoes de rede:" + RESET)

    if os.path.exists("/proc/net/route"):
        try:
            with open("/proc/net/route", encoding="utf-8") as arquivo:
                linhas = arquivo.readlines()[1:]
                for linha in linhas:
                    campos = linha.split()
                    if len(campos) > 2 and campos[1] == "00000000":
                        valor = int(campos[2], 16)
                        gateway = socket.inet_ntoa(
                            valor.to_bytes(4, "little")
                        )
                        print(f"Gateway IPv4: {gateway}")
                        break
                else:
                    print("Gateway IPv4: nao encontrado")
        except (OSError, ValueError):
            print("Gateway: nao foi possivel consultar")
    else:
        print("Gateway: arquivo de rotas indisponivel")

    try:
        print("DNS configurado:")
        with open("/etc/resolv.conf", encoding="utf-8") as arquivo:
            encontrados = False
            for linha in arquivo:
                if linha.strip().startswith("nameserver"):
                    print("  " + linha.split()[1])
                    encontrados = True
            if not encontrados:
                print("  Nenhum servidor listado")
    except OSError:
        print("DNS: arquivo nao acessivel")


def testar_internet():
    try:
        urllib.request.urlopen(
            "https://www.google.com",
            timeout=5
        )
        print(GREEN + "Internet: conectada" + RESET)
    except Exception:
        print(RED + "Internet: sem conexao ou acesso bloqueado" + RESET)


def testar_ping():
    destino = input("Endereco para testar (ex: 1.1.1.1): ").strip()

    if not destino or any(c.isspace() for c in destino):
        print(RED + "Endereco invalido." + RESET)
        return

    sistema = platform.system().lower()
    comando = ["ping", "-c", "4", destino] if sistema != "windows" else [
        "ping", "-n", "4", destino
    ]

    try:
        subprocess.run(comando, timeout=12, check=False)
    except FileNotFoundError:
        print(RED + "Comando ping nao encontrado." + RESET)
    except subprocess.TimeoutExpired:
        print(YELLOW + "O teste demorou demais." + RESET)


def ip_publico():
    try:
        with urllib.request.urlopen(
            "https://api.ipify.org?format=json",
            timeout=5
        ) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))
        print(GREEN + f"IP publico: {dados['ip']}" + RESET)
    except Exception:
        print(RED + "Nao foi possivel consultar o IP publico." + RESET)


def adaptadores():
    print(CYAN + "\nInterfaces de rede:" + RESET)
    try:
        resultado = subprocess.run(
            ["ip", "addr"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        if resultado.returncode == 0 and resultado.stdout.strip():
            print(resultado.stdout)
        else:
            print("Comando ip indisponivel.")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("Instale o pacote iproute2 para consultar interfaces.")


def menu():
    while True:
        limpar()
        titulo()
        print("01. Consultar IP local")
        print("02. Consultar IPv6")
        print("03. Consultar gateway e DNS")
        print("04. Testar conexao com a internet")
        print("05. Testar latencia (ping)")
        print("06. Consultar IP publico")
        print("07. Consultar adaptadores")
        print("00. Sair")

        opcao = input(CYAN + "\nNKZ >> " + RESET).strip()

        if opcao == "1":
            ip_local()
        elif opcao == "2":
            ipv6_local()
        elif opcao == "3":
            gateway_dns()
        elif opcao == "4":
            testar_internet()
        elif opcao == "5":
            testar_ping()
        elif opcao == "6":
            ip_publico()
        elif opcao == "7":
            adaptadores()
        elif opcao == "0" or opcao == "00":
            print(GREEN + "Obrigado por usar NKZ NET TOOLS!" + RESET)
            break
        else:
            print(RED + "Opcao invalida." + RESET)

        input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nEncerrando NKZ NET TOOLS...")
