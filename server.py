"""TCP + UDP multi-client server (multiplexed on two ports)."""
import socket, threading, random, time, argparse


def tcp_client_handler(conn, addr):
    print(f"[TCP] Connection established with {addr}")
    with conn, conn.makefile("rwb") as f:
        for line in f:  # reliable, ordered byte stream
            cid, seq, msg = line.decode().strip().split("|", 2)
            print(f"[TCP] {cid} seq={seq} received: {msg}")
            f.write(f"ACK|{cid}|{seq}|{msg.upper()}\n".encode())
            f.flush()
    print(f"[TCP] Connection closed with {addr}")


def tcp_server(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(20)
    print(f"[TCP] Listening on {host}:{port}")
    while True:
        conn, addr = s.accept()  # 3-way handshake completed here
        threading.Thread(target=tcp_client_handler, args=(conn, addr),
                         daemon=True).start()


def udp_server(host, port, loss):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print(f"[UDP] Listening on {host}:{port} (simulated loss={loss:.0%})")
    while True:
        data, addr = s.recvfrom(2048)  # no connection, each datagram independent
        if random.random() < loss:  # optional artificial packet loss
            continue
        cid, seq, msg = data.decode().split("|", 2)
        print(f"[UDP] {cid} seq={seq} from {addr}: {msg}")
        s.sendto(f"ACK|{cid}|{seq}|{msg.upper()}".encode(), addr)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--tcp-port", type=int, default=5000)
    p.add_argument("--udp-port", type=int, default=5001)
    p.add_argument("--loss", type=float, default=0.0)
    a = p.parse_args()
    threading.Thread(target=tcp_server, args=(a.host, a.tcp_port), daemon=True).start()
    threading.Thread(target=udp_server, args=(a.host, a.udp_port, a.loss), daemon=True).start()
    while True:
        time.sleep(1)
