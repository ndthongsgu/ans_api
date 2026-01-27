from sqlalchemy.orm import Session
from models.customer import Customer
from schemas.customer.customer import CustomerCreate, CustomerUpdate

class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_customer(self, customer_id: str):
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def get_customers(self, skip: int = 0, limit: int = 100):
        return self.db.query(Customer).offset(skip).limit(limit).all()

    def create_customer(self, customer: CustomerCreate):
        db_customer = Customer(user_id=customer.user_id, full_name=customer.full_name, phone=customer.phone)
        self.db.add(db_customer)
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer

    def update_customer(self, customer_id: str, customer: CustomerUpdate):
        db_customer = self.get_customer(customer_id)
        if db_customer:
            db_customer.user_id = customer.user_id
            db_customer.full_name = customer.full_name
            db_customer.phone = customer.phone
            self.db.commit()
            self.db.refresh(db_customer)
        return db_customer

    def delete_customer(self, customer_id: str):
        db_customer = self.get_customer(customer_id)
        if db_customer:
            self.db.delete(db_customer)
            self.db.commit()
        return db_customer
