import razorpay
from app.config import settings

class PaymentService:
    """
    Service responsible for interacting with Razorpay.
    This abstracts away the payment gateway logic so the rest of the application
    doesn't need to know how Razorpay works internally.
    """
    
    def __init__(self):
        # Initialize the Razorpay client using our secure keys from .env
        self.client = razorpay.Client(
            auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
        )

    def create_order(self, amount_in_rupees: int, receipt_id: str) -> dict:
        """
        Creates a new order in Razorpay.
        Razorpay requires the amount to be in subunits (paise for INR).
        """
        amount_in_paise = amount_in_rupees * 100
        data = {
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": receipt_id,
            "payment_capture": 1 # Auto capture payment
        }
        
        # Call Razorpay API to generate the secure order
        razorpay_order = self.client.order.create(data=data)
        return razorpay_order

    def verify_signature(self, order_id: str, payment_id: str, signature: str) -> bool:
        """
        Verifies the cryptographic signature sent by Razorpay to ensure
        the payment is legitimate and hasn't been tampered with.
        """
        try:
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            # This will throw a SignatureVerificationError if invalid
            self.client.utility.verify_payment_signature(params_dict)
            return True
        except Exception as e:
            print(f"Payment verification failed: {str(e)}")
            return False

    def fetch_order(self, razorpay_order_id: str) -> dict:
        """
        Fetches the current status of an order from Razorpay.
        Useful for reconciliation if webhooks fail.
        """
        return self.client.order.fetch(razorpay_order_id)

    def refund_payment(self, payment_id: str, amount_in_rupees: int = None) -> dict:
        """
        Initiates a refund for a captured payment.
        If amount is None, full refund is issued.
        """
        data = {}
        if amount_in_rupees:
            data['amount'] = amount_in_rupees * 100
        
        return self.client.payment.refund(payment_id, data)

# Create a singleton instance to use throughout the app
payment_service = PaymentService()
