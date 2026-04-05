import time
import random
import threading
from queue import Queue
from datetime import datetime

class MockStreamClient:
    def __init__(self):
        self.queue = Queue()
        self.running = False
        self._thread = None
        
        self.mock_templates = [
            "Failed password for invalid user admin from {ip} port {port} ssh2",
            "Connection closed by authenticating user root {ip} port {port} [preauth]",
            "Invalid user admin from {ip} port {port}",
            "Accepted publickey for ubuntu from {ip} port {port} ssh2",
            "POST /api/v1/auth HTTP/1.1 401 112 - Mozilla/5.0",
            "GET /etc/passwd HTTP/1.1 404 231 - curl/7.68.0",
            "Login success for user sysadmin from {ip}"
        ]
        
        # Simulating external threat signatures for the AI to catch
        self.attack_templates = [
            "Attempted exploit detected: SQL Injection in login portal via {ip}",
            "CRITICAL: Multiple failed sudo attempts by user www-data from {ip}"
        ]

    def _generate_ip(self):
        return f"{random.randint(10, 200)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

    def _worker(self):
        while self.running:
            # Emits 1 log approximately every 1 to 2.5 seconds
            time.sleep(random.uniform(1.0, 2.5))
            if not self.running:
                break
                
            ip = self._generate_ip()
            port = random.randint(1024, 65535)
            
            # 10% chance to emit a glaring attack log
            if random.random() < 0.10:
                msg_tmpl = random.choice(self.attack_templates)
            else:
                msg_tmpl = random.choice(self.mock_templates)
                
            msg = msg_tmpl.format(ip=ip, port=port)
            
            timestamp = datetime.now().strftime("%b %d %H:%M:%S")
            log_line = f"{timestamp} server-node01 sshd[{random.randint(100, 999)}]: {msg}"
            
            self.queue.put(log_line)

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            
    def get_logs(self):
        logs = []
        while not self.queue.empty():
            logs.append(self.queue.get())
        return logs
