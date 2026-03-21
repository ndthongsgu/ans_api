import random
import time
from sqlalchemy.orm import Session
from models.password_reset import PasswordReset
from modules.auth.services.mobile_service import MobileService, ServiceError
from utils.email_util import send_email
from utils.i18n import t
from utils.security import hash_password

OTP_TTL_SECONDS = 10 * 60
MAX_ATTEMPTS = 5


class PasswordResetError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class PasswordResetService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = MobileService(db)

    def _generate_otp(self) -> str:
        return f"{random.randint(0, 999999):06d}"

    def create_reset(self, email: str, locale: str | None = None):
        # Ensure email exists
        user = self.user_service.find_by_email(email)
        if not user:
            raise PasswordResetError('user_not_found')

        otp = self._generate_otp()
        now = int(time.time())
        expires = now + OTP_TTL_SECONDS

        pr = PasswordReset(
            email=email,
            otp_code=otp,
            expires_at=expires,
            used=False,
            attempts=0,
            created_at=now,
        )
        self.db.add(pr)
        self.db.commit()
        self.db.refresh(pr)

        # send localized email
        subject = t('reset_subject', locale)
        body = t('reset_body', locale, otp=otp, minutes=OTP_TTL_SECONDS // 60)
        send_email(subject, email, body)

        return pr

    def verify_and_reset(self, email: str, otp: str, new_password: str):
        pr = self.db.query(PasswordReset).filter(PasswordReset.email == email, PasswordReset.used == False).order_by(PasswordReset.created_at.desc()).first()
        if not pr:
            raise PasswordResetError('no_pending')
        if pr.attempts >= MAX_ATTEMPTS:
            raise PasswordResetError('too_many_attempts')
        now = int(time.time())
        if now > pr.expires_at:
            raise PasswordResetError('reset_expired')
        pr.attempts += 1
        if pr.otp_code != otp:
            self.db.commit()
            raise PasswordResetError('invalid_otp')

        pr.used = True
        self.db.commit()

        # update password
        hashed = hash_password(new_password)
        try:
            # use existing method to change by email
            self.user_service.change_password_by_email(email, hashed)
        except ServiceError as e:
            raise PasswordResetError(e.code)

        return True
