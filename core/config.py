import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost/dbname")

# Auth configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-256-bit-secret-here-change-in-production-12345678901234567890123456789012")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# VNPay sandbox payment configuration
VNPAY_TMN_CODE = os.getenv("VNPAY_TMN_CODE", "")
VNPAY_HASH_SECRET = os.getenv("VNPAY_HASH_SECRET", "")
VNPAY_ENDPOINT = os.getenv("VNPAY_ENDPOINT", "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html")
VNPAY_RETURN_URL = os.getenv("VNPAY_RETURN_URL", "http://localhost:5173/owner/subscription-packages/return")
VNPAY_IPN_URL = os.getenv("VNPAY_IPN_URL", "http://localhost:8000/owner/subscription-packages/vnpay/ipn")
VNPAY_LOCALE = os.getenv("VNPAY_LOCALE", "vn")
VNPAY_ORDER_TYPE = os.getenv("VNPAY_ORDER_TYPE", "other")

# Cloudinary configuration for media uploads
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
CLOUDINARY_UPLOAD_PRESET = os.getenv("CLOUDINARY_UPLOAD_PRESET", "")
CLOUDINARY_FOLDER = os.getenv("CLOUDINARY_FOLDER", "ans_api/stalls")
