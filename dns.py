import socket
from dnslib import DNSRecord, RR, A
import threading
import sys

HOST = "0.0.0.0"
PORT = 53
DEFAULT_DNS = "8.8.8.8"
MOCK_ENTRIES = {
    "abcabc.com.": "11.1.1.1",
}

def query_external_dns(domain):
    try:
        query = DNSRecord.question(domain)
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(("0.0.0.0", 50))
            s.settimeout(2)
            s.sendto(query.pack(), (DEFAULT_DNS, 53))
            response_data, _ = s.recvfrom(512)
            response = DNSRecord.parse(response_data)
            
            if query.questions[0].qname != response.rr[0].rname:
                return None
            
            for rr in response.rr:
                if rr.rtype == 1:
                    return str(rr.rdata)

    except Exception as e:
        print(f"Error querying external DNS: {e}")
    return None

def handle_dns_request(data, addr, sock):
    request = DNSRecord.parse(data)
    reply = request.reply()
    
    for q in request.questions:
        domain = str(q.qname)
        
        if domain in MOCK_ENTRIES:
            ip = MOCK_ENTRIES[domain]
        else:
            ip = query_external_dns(domain)
            if ip:
                MOCK_ENTRIES[domain] = ip  # Cache the result
                print("Added", domain, ip)

        if ip:
            reply.add_answer(RR(q.qname, ttl=60, rdata=A(ip)))
            print(f"Responded to {addr} with {ip} for {domain}")
        else:
            print(f"Failed to resolve {domain}")
    
    sock.sendto(reply.pack(), addr)

def start_dns_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    print(f"DNS Server running on {HOST}:{PORT}")

    while True:
        try:
            data, addr = sock.recvfrom(512)  # Max DNS packet size
            threading.Thread(target=handle_dns_request, args=(data, addr, sock)).start()
        except Exception as e:
            print(f"Error: {e}")

def listen_for_clear_command():
    while True:
        command = input().strip().lower()
        if command == "c":
            MOCK_ENTRIES.clear()
            print("Cache cleared!")

if __name__ == "__main__":
    threading.Thread(target=listen_for_clear_command, daemon=True).start()
    start_dns_server()

