import argparse
import requests
import threading
import time

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

parser = argparse.ArgumentParser()
parser.add_argument("target_ips", help="file containing IP addresses to target")
parser.add_argument("target_domains", help="file containing vhosts to test")
parser.add_argument("log_file", help="log file")
args = parser.parse_args()

## varibles for tweaking
protolols = ["http://", "https://"]
num_threads = 10
request_delay = 0.01 # time to sleep (seconds) between requests in each thread
timeout = 2

## Class/thinger
class uri_class(object):
    ip = ""
    proto = 0
    domain = ""

    def __init__(self, ip, proto, domain):
        self.ip = ip
        self.proto = proto
        self.domain = domain

def build_uri(ip, proto, domain):
    uri = uri_class(ip, proto, domain)
    return uri

def chunks(l, n):
	for i in range(0, len(l), n):
		yield l[i:i + n]

## Open files
try:
	ips = [line.strip() for line in open(args.target_ips, 'r')]
except:
	print("Unable to read IPs file")
	exit()

try:
	domains = [line.strip() for line in open(args.target_domains, 'r')]
except:
	print("Unable to read domains file")
	exit()

try:
	logFile  = open(args.log_file, "w")
except:
	print("Unable to open log file for output")
	exit()

## Worker for threading
def worker(scan_uris):
	for uri in scan_uris:
		time.sleep(request_delay)
		try:
			result = requests.get(uri.proto+uri.ip, headers={'host': uri.domain}, timeout=timeout)
			if result.status_code != 404:
				print("IP: " +uri.ip +" URL: " + uri.proto+uri.domain + " Status: " + str(result.status_code))
				logFile.write("IP: " +uri.ip +" URL: " + uri.proto+uri.domain + " Status: " + str(result.status_code)+"\n")
		except requests.exceptions.ConnectionError:
			pass
			#print("Could not connect to: " +uri.proto+uri.ip)
		except requests.exceptions.ReadTimeout:
			pass
			#print("Could not connect to: " +uri.proto+uri.ip)
		except:
			print("Something else went wrong -- IP: " +uri.ip +" URL: " + uri.proto+uri.domain)
	return

uris = []
for ip in ips:
	for domain in domains:
		for proto in protolols:
			uris.append(build_uri(ip, proto, domain))

## ok time to set up threads  k
threads = []
for chunk in chunks(uris, num_threads):
    t = threading.Thread(target=worker, args=(chunk,))
    threads.append(t)
    t.start()
