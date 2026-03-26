import random
import time
from sqlalchemy.orm import Session
from models.email_verification import EmailVerification
from modules.auth.dto.mobile_dto import RegisterRequest
from utils.email_util import send_email
from modules.auth.services.mobile_service import MobileService, ServiceError
from utils.security import hash_password
from utils.i18n import t

OTP_TTL_SECONDS = 10 * 60  # 10 minutes
MAX_ATTEMPTS = 5


class VerificationError(Exception):
    """Raised with an error code (e.g. 'email_exists', 'invalid_otp')."""
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class VerificationService:
    def __init__(self, db: Session):
        self.db = db
        self.mobile_service = MobileService(db)

    def _generate_otp(self) -> str:
        return f"{random.randint(0, 999999):06d}"

    def create_verification(self, register_request: RegisterRequest, locale: str | None = None):
        # Check email / username availability
        if self.mobile_service.find_by_email(register_request.email):
            raise VerificationError('email_exists')
        if register_request.username and self.mobile_service.find_by_username(register_request.username):
            raise VerificationError('username_exists')

        otp = self._generate_otp()
        now = int(time.time())
        expires = now + OTP_TTL_SECONDS

        verification = EmailVerification(
            email=register_request.email,
            username=register_request.username,
            password_hash=hash_password(register_request.password),
            full_name=register_request.full_name,
            otp_code=otp,
            expires_at=expires,
            verified=False,
            attempts=0,
            created_at=now,
        )
        self.db.add(verification)
        self.db.commit()
        self.db.refresh(verification)

        # Send email (may raise RuntimeError if SMTP not configured)
        subject = t('otp_subject', locale)
        body = t('otp_body', locale, otp=otp, minutes=OTP_TTL_SECONDS // 60)
        send_email(subject, register_request.email, body)

        return verification

    def verify_and_create(self, email: str, otp: str):
        v = self.db.query(EmailVerification).filter(EmailVerification.email == email, EmailVerification.verified == False).order_by(EmailVerification.created_at.desc()).first()
        if not v:
            raise VerificationError('no_pending')
        if v.attempts >= MAX_ATTEMPTS:
            raise VerificationError('too_many_attempts')
        now = int(time.time())
        if now > v.expires_at:
            raise VerificationError('otp_expired')
        v.attempts += 1
        if v.otp_code != otp:
            self.db.commit()
            raise VerificationError('invalid_otp')

        # mark verified
        v.verified = True
        self.db.commit()

        # Create user and customer using the stored hashed password
        # We add a method in MobileService to create with pre-hashed password
        try:
            user, customer = self.mobile_service.create_customer_with_hashed_password(
                username=v.username,
                email=v.email,
                password_hash=v.password_hash,
                full_name=v.full_name,
            )
            return user, customer
        except ServiceError as e:
            # Map to verification error codes so controller can localize
            raise VerificationError(e.code)
