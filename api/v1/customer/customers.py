from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from services.customer.customer_service import CustomerService
from schemas.customer.customer import Customer, CustomerCreate, CustomerUpdate

router = APIRouter()

@router.post("/customers/", response_model=Customer)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    service = CustomerService(db)
    return service.create_customer(customer)

@router.get("/customers/", response_model=list[Customer])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = CustomerService(db)
    return service.get_customers(skip=skip, limit=limit)

@router.get("/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    service = CustomerService(db)
    db_customer = service.get_customer(customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@router.put("/customers/{customer_id}", response_model=Customer)
def update_customer(customer_id: str, customer: CustomerUpdate, db: Session = Depends(get_db)):
    service = CustomerService(db)
    db_customer = service.update_customer(customer_id, customer)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@router.delete("/customers/{customer_id}")
def delete_customer(customer_id: str, db: Session = Depends(get_db)):
    service = CustomerService(db)
    db_customer = service.delete_customer(customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"detail": "Deleted"}
