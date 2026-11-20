"""TCP/UDP client: reports status, transmission time and acknowledgment."""
import socket, time, argparse


def run_tcp(cid, ip, port, msgs):
    t0 = time.perf_counter()
    s = socket.create_connection((ip, port), timeout=2)  # SYN, SYN-ACK, ACK
    print(f"[{cid}] Connection Status: CONNECTED "
          f"(handshake {1000*(time.perf_counter()-t0):.3f} ms)")
    f = s.makefile("rwb")
    results = []
    for seq, m in enumerate(msgs, 1):
        t = time.perf_counter()
        f.write(f"{cid}|{seq}|{m}\n".encode())
        f.flush()
        reply = f.readline().decode().strip()
        rtt = 1000*(time.perf_counter()-t)
        results.append(rtt)
        print(f"[{cid}] TCP seq={seq} sent='{m}' received='{reply.split('|')[-1]}' "
              f"time={rtt:.3f} ms ACK=RECEIVED")
    s.close()
    print(f"[{cid}] Connection Status: CLOSED")
    return results


def run_udp(cid, ip, port, msgs, timeout=0.3):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    print(f"[{cid}] Connection Status: CONNECTIONLESS (no handshake)")
    results = []
    for seq, m in enumerate(msgs, 1):
        t = time.perf_counter()
        s.sendto(f"{cid}|{seq}|{m}".encode(), (ip, port))
        try:
            reply = s.recvfrom(2048)[0].decode()
            rtt = 1000*(time.perf_counter()-t)
            results.append(rtt)
            print(f"[{cid}] UDP seq={seq} sent='{m}' received='{reply.split('|')[-1]}' "
                  f"time={rtt:.3f} ms ACK=RECEIVED")
        except socket.timeout:
            results.append(None)
            print(f"[{cid}] UDP seq={seq} sent='{m}' time>{timeout*1000:.0f} ms "
                  f"ACK=NOT RECEIVED (packet lost, no retransmission)")
    s.close()
    return results


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--id", default="C1")
    p.add_argument("--ip", default="127.0.0.1")
    p.add_argument("--port", type=int, required=True)
    p.add_argument("--proto", choices=["tcp", "udp"], required=True)
    p.add_argument("--msg", nargs="+", default=["hello server"])
    a = p.parse_args()
    (run_tcp if a.proto == "tcp" else run_udp)(a.id, a.ip, a.port, a.msg)
