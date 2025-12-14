import grpc
import paynow_pb2
import paynow_pb2_grpc

# Connect to gRPC server
channel = grpc.insecure_channel("localhost:50051")
stub = paynow_pb2_grpc.PayNowStub(channel)

# Prepare a list of payments
payments = []
payments.append(paynow_pb2.Payment(client_id="Munyaradzi Chirove", service="ZESA", amount=10.0))

# Stream payments to the server
response = stub.StreamPayments(iter(payments))

# Print the server acknowledgment
print("Server ack:", response.received)
