import time
import httpx

start = time.perf_counter()

httpx.get("http://127.0.0.1:5001/nutrition/eggs")
httpx.get("http://127.0.0.1:5001/nutrition/eggs")
httpx.get("http://127.0.0.1:5001/nutrition/eggs")
httpx.get("http://127.0.0.1:5001/nutrition/eggs")
httpx.get("http://127.0.0.1:5001/nutrition/eggs")

end = time.perf_counter()
elapsed = end - start
print(elapsed)