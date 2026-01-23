from sqlalchemy.orm import Session
from repositories.customer_repository import CustomerRepository
from schemas.customer import CustomerCreate, CustomerUpdate

class CustomerService:
    def __init__(self, db: Session):
        self.repository = CustomerRepository(db)

    def get_customer(self, customer_id: str):
        return self.repository.get_customer(customer_id)

    def get_customers(self, skip: int = 0, limit: int = 100):
        return self.repository.get_customers(skip, limit)

    def create_customer(self, customer: CustomerCreate):
        return self.repository.create_customer(customer)

    def update_customer(self, customer_id: str, customer: CustomerUpdate):
        return self.repository.update_customer(customer_id, customer)

    def delete_customer(self, customer_id: str):
        return self.repository.delete_customer(customer_id)
