from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

# ============================================================
# PHASE 1: THE GATEKEEPER (Page 8) + STATE (Page 10)
# ============================================================
# The accumulator MUST live outside any loop/request handler.
# This is the "Initialization (Memory)" from Page 10A.
# If this were inside the handler, it would reset every request
# (the "Iteration Amnesia" disaster from Page 10B).

total_spent = 0.0
transaction_count = 0
transaction_history = []
 

class ExpenseTrackerHandler(BaseHTTPRequestHandler):
    """
    The 'Engine' (Page 7: Process) that receives raw input,
    validates it, transforms it, and outputs refined reality.
    """

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self._set_headers(200)

    def do_GET(self):
        """
        OUTPUT: The Display (Page 14)
        Return current state without modifying it.
        """
        global total_spent, transaction_count, transaction_history

        if self.path == '/api/status':
            self._set_headers(200)
            response = {
                "total": round(total_spent, 2),
                "count": transaction_count,
                "history": transaction_history,
                "status": "active"
            }
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """
        INPUT: The Gate (Page 7)
        PROCESS: The Engine (Pages 8-13)
        """
        global total_spent, transaction_count, transaction_history

        if self.path == '/api/add_expense':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode('utf-8'))
                raw_input = str(data.get('amount', '')).strip()

                # ================================================
                # KILL SWITCH: Graceful Shutdown (Page 13)
                # ================================================
                if raw_input.lower() == 'quit':
                    self._set_headers(200)
                    response = {
                        "success": True,
                        "shutdown": True,
                        "final_total": round(total_spent, 2),
                        "message": f"Final Total: ${total_spent:.2f}",
                        "count": transaction_count
                    }
                    self.wfile.write(json.dumps(response).encode())
                    return

                # ================================================
                # THE GATEKEEPER: Defensive Coding (Pages 8-9)
                # ================================================
                try:
                    expense = float(raw_input)
                except ValueError:
                    # The Digital Poka-Yoke: Invalid input blocked
                    self._set_headers(400)
                    response = {
                        "success": False,
                        "error": f"Invalid Data: '{raw_input}' is not a number.",
                        "total": round(total_spent, 2)
                    }
                    self.wfile.write(json.dumps(response).encode())
                    return

                # Edge case: negative expenses?
                if expense < 0:
                    self._set_headers(400)
                    response = {
                        "success": False,
                        "error": "Expense cannot be negative.",
                        "total": round(total_spent, 2)
                    }
                    self.wfile.write(json.dumps(response).encode())
                    return

                # ================================================
                # THE ACCUMULATOR PATTERN (Page 11)
                # State(new) = State(old) + Input
                # ================================================
                total_spent += expense
                transaction_count += 1
                transaction_history.append({
                    "id": transaction_count,
                    "amount": round(expense, 2),
                    "running_total": round(total_spent, 2)
                })

                # ================================================
                # OUTPUT: Decoupled Display (Page 14)
                # ================================================
                self._set_headers(200)
                response = {
                    "success": True,
                    "added": round(expense, 2),
                    "total": round(total_spent, 2),
                    "count": transaction_count,
                    "message": f"Added ${expense:.2f}. Total: ${total_spent:.2f}"
                }
                self.wfile.write(json.dumps(response).encode())

            except json.JSONDecodeError:
                self._set_headers(400)
                response = {"success": False, "error": "Malformed JSON payload"}
                self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        """Cleaner console logging"""
        print(f"[ENGINE] {self.address_string()} - {format % args}")


def run_server(port=8000):
    """
    Boot the backend engine.
    This is the 'Backend Engineering' foundation (Page 18).
    """
    server_address = ('', port)
    httpd = HTTPServer(server_address, ExpenseTrackerHandler)

    print("=" * 55)
    print("  DECODELABS PROJECT 2: EXPENSE TRACKER ENGINE")
    print("=" * 55)
    print(f"  State initialized: total = {total_spent}")
    print(f"  Server running at: http://localhost:{port}")
    print(f"  Endpoints:")
    print(f"    GET  /api/status       -> View current total")
    print(f"    POST /api/add_expense  -> Add an expense")
    print(f"  Send 'quit' to trigger kill switch.")
    print("=" * 55)
    print("  AUDIT CHECKLIST (Page 17):")
    print("    [x] Handles 5+ transactions")
    print("    [x] 'total' initialized OUTSIDE the loop")
    print("    [x] Defensive: catches ValueError")
    print("    [x] Kill switch prints final total")
    print("=" * 55)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n[SHUTDOWN] Sentinel received. Final total: "
              f"${total_spent:.2f}")
        httpd.server_close()


if __name__ == '__main__':
    run_server(8000)