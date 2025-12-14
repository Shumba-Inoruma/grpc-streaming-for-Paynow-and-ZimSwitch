import grpc
from concurrent import futures
import paynow_pb2
import paynow_pb2_grpc
import requests


class PayNowServicer(paynow_pb2_grpc.PayNowServicer):
    def __init__(self):
        # Initialize counters as instance attributes
        self.total_transactions = 0
        self.total_amount = 0
        self.total_ecocash = 0
        self.total_zesa = 0
        self.total_onemoney = 0

    def push_stats(
        self,
        total_transactions,
        total_amount,
        total_ecocash,
        total_onemoney,
        total_zesa,
        server_url="http://localhost:5001/update"
    ):
        payload = {
            "total_transactions": total_transactions,
            "total_amount": total_amount,
            "total_ecocash": total_ecocash,
            "total_onemoney": total_onemoney,
            "total_zesa": total_zesa
        }

        response = requests.post(server_url, json=payload)
        if response.status_code == 200:
            print("Stats sent successfully!")
        else:
            print("Failed to send stats:", response.status_code, response.text)

    def StreamPayments(self, request_iterator, context):
        for payment in request_iterator:
            self.total_transactions += 1
            self.total_amount += payment.amount

            # Fixed typos: should be 'payment.service', not 'payment.server'
            if payment.service == "Ecocash":
                self.total_ecocash += 1
            elif payment.service == "OneMoney":
                self.total_onemoney += 1
            elif payment.service == "ZESA":
                self.total_zesa += 1

            # Print running totals
            print(
                f"Received #{self.total_transactions} → {payment.service} : {payment.amount}"
            )
            print(
                f"Totals → Ecocash: {self.total_ecocash}, OneMoney: {self.total_onemoney}, ZESA: {self.total_zesa}, Amount: {self.total_amount}"
            )
            # Example usage
            self.push_stats(
                total_transactions=self.total_transactions,
                total_amount=self.total_amount,
                total_ecocash=self.total_ecocash,
                total_onemoney=self.total_onemoney,
                total_zesa=self.total_zesa
            )


        return paynow_pb2.Ack(received=True)

# Create gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
paynow_pb2_grpc.add_PayNowServicer_to_server(PayNowServicer(), server)
server.add_insecure_port("[::]:50051")
server.start()
print("Server running on port 50051...")
server.wait_for_termination()
