from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO
from prometheus_client import Counter, Gauge, generate_latest

app = Flask(__name__)
socketio = SocketIO(app)

# Function to send live stats to Socket.IO clients
def send_stats(total_transactions, total_amount, total_ecocash, total_onemoney, total_zesa):
    socketio.emit(
        "update_stats",
        {
            "total_transactions": total_transactions,
            "total_amount": total_amount,
            "total_ecocash": total_ecocash,
            "total_onemoney": total_onemoney,
            "total_zesa": total_zesa,
        },
    )

# Prometheus metrics
total_transactions_metric = Counter('total_transactions', 'Total number of transactions')
total_amount_metric = Gauge('total_amount', 'Total transaction amount')
ecocash_count_metric = Counter('ecocash_count', 'Ecocash transactions')
zesa_count_metric = Counter('zesa_count', 'ZESA transactions')
onemoney_count_metric = Counter('onemoney_count', 'OneMoney transactions')


@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# Expose Prometheus metrics
@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')

# API to update stats from any client
@app.route("/update", methods=["POST"])
def update_stats_api():
    data = request.json  # property, not a method

    # Update Prometheus metrics
    total_transactions_metric.inc(data.get("total_transactions", 0))
    total_amount_metric.inc(data.get("total_amount", 0.0))  # <-- increment, not set
    ecocash_count_metric.inc(data.get("total_ecocash", 0))
    zesa_count_metric.inc(data.get("total_zesa", 0))
    onemoney_count_metric.inc(data.get("total_onemoney", 0))

    # Emit to Socket.IO clients
    send_stats(
        total_transactions=data.get("total_transactions", 0),
        total_amount=data.get("total_amount", 0.0),
        total_ecocash=data.get("total_ecocash", 0),
        total_onemoney=data.get("total_onemoney", 0),
        total_zesa=data.get("total_zesa", 0)
    )

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001)
