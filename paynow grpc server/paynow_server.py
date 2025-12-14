import grpc
from concurrent import futures
import paynow_pb2
import paynow_pb2_grpc
import requests


class PayNowServicer(paynow_pb2_grpc.PayNowServicer):
    def push_stats(
        self,
        amount,
        service,
        server_url="http://localhost:5001/update"
    ):
        payload = {
            "amount": amount,
            "service": service,
        }

        response = requests.post(server_url, json=payload)
        if response.status_code == 200:
            print("Stats sent successfully!")
        else:
            print("Failed to send stats:", response.status_code, response.text)

    def StreamPayments(self, request_iterator, context):
        for payment in request_iterator:
            print(
                f"Received #{payment.service} : {payment.amount}"
            )
            # Example usage
            self.push_stats(
                amount=payment.amount,
                service=payment.service

            )


        return paynow_pb2.Ack(received=True)

# Create gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
paynow_pb2_grpc.add_PayNowServicer_to_server(PayNowServicer(), server)
server.add_insecure_port("[::]:50051")
server.start()
print("Server running on port 50051...")
server.wait_for_termination()
