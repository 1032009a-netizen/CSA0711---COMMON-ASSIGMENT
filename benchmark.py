import threading, statistics, time, json, sys
from client import run_tcp, run_udp
import io, contextlib

N, CLIENTS = 500, 5


def bench(fn, port, label):
    out = {}

    def w(i):
        with contextlib.redirect_stdout(io.StringIO()):
            out[i] = fn(f"C{i}", "127.0.0.1", port, ["x"*64]*N)

    t0 = time.perf_counter()
    th = [threading.Thread(target=w, args=(i,)) for i in range(1, CLIENTS+1)]
    [t.start() for t in th]
    [t.join() for t in th]
    el = time.perf_counter()-t0
    allr = [r for v in out.values() for r in v]
    ok = [r for r in allr if r is not None]
    return dict(label=label, sent=len(allr), acked=len(ok),
                loss=100*(1-len(ok)/len(allr)), avg=statistics.mean(ok),
                p95=sorted(ok)[int(.95*len(ok))-1], mn=min(ok), mx=max(ok),
                tput=len(ok)/el, elapsed=el)


# Usage: python benchmark.py <udp_port> <udp_label> <output.json>
res = [bench(run_tcp, 5000, "TCP"), bench(run_udp, int(sys.argv[1]), sys.argv[2])]
json.dump(res, open(sys.argv[3], "w"), indent=1)
print(json.dumps(res, indent=1))
