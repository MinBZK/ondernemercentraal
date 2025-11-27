from uuid import UUID

from pydantic import BaseModel

from .base import BaseSchema


class ProductUpdate(BaseModel):
    name: str
    code: str | None
    product_category_name: str


class ProductCreate(ProductUpdate):
    pass


class Product(BaseSchema, ProductCreate):
    product_category_id: UUID
    product_category_name: str
    pass


class ProductCategoryCreate(BaseModel):
    name: str


class ProductCategoryUpdate(ProductCategoryCreate):
    pass


class ProductCategory(BaseSchema, ProductCategoryUpdate):
    products: list[Product]
