from pydantic import BaseModel

class ProductBase(BaseModel):
    pass

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductOut(ProductBase):
    pass