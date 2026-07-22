from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# Auth
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class AdminUserCreate(BaseModel):
    username: str
    password: str


class AdminUserOut(BaseModel):
    id: int
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Category
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    image_url: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Product Image
class ProductImageOut(BaseModel):
    id: int
    image_url: str
    is_primary: bool
    order_index: int

    class Config:
        from_attributes = True


# Product
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    full_description: Optional[str] = None
    price: float
    discount_price: Optional[float] = None
    has_discount: bool = False
    stock: int = 0
    sku: Optional[str] = None
    brand: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    video_url: Optional[str] = None
    is_active: bool = True
    is_featured: bool = False
    category_id: Optional[int] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    full_description: Optional[str] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    has_discount: Optional[bool] = None
    stock: Optional[int] = None
    sku: Optional[str] = None
    brand: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    video_url: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    category_id: Optional[int] = None


class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    full_description: Optional[str]
    price: float
    discount_price: Optional[float]
    has_discount: bool
    stock: int
    sku: Optional[str]
    brand: Optional[str]
    weight: Optional[float]
    dimensions: Optional[str]
    video_url: Optional[str]
    is_active: bool
    is_featured: bool
    category_id: Optional[int]
    created_at: datetime
    images: List[ProductImageOut] = []

    class Config:
        from_attributes = True


# Customer User
class CustomerUserOut(BaseModel):
    id: int
    phone: Optional[str]
    full_name: Optional[str]
    email: Optional[str]
    is_active: bool
    is_blocked: bool
    block_reason: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class BlockUserRequest(BaseModel):
    reason: Optional[str] = None


# Order Item
class OrderItemOut(BaseModel):
    id: int
    product_name: str
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


# Order
class OrderOut(BaseModel):
    id: int
    status: str
    total_price: float
    created_at: datetime
    items: List[OrderItemOut] = []

    class Config:
        from_attributes = True


# Baraban Prize
class BarabanPrizeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_mega_prize: bool = False
    probability_type: str = "count"
    probability_value: float = 10.0
    total_count: int = 10
    order_index: int = 0
    is_active: bool = True


class BarabanPrizeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_mega_prize: Optional[bool] = None
    probability_type: Optional[str] = None
    probability_value: Optional[float] = None
    total_count: Optional[int] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None


class BarabanPrizeOut(BaseModel):
    id: int
    baraban_id: int
    name: str
    description: Optional[str]
    image_url: Optional[str]
    is_mega_prize: bool
    probability_type: str
    probability_value: float
    total_count: int
    order_index: int
    is_active: bool

    class Config:
        from_attributes = True


# Baraban
class BarabanCreate(BaseModel):
    name: str
    target_audience: str = "yoshlar"
    description: Optional[str] = None
    is_active: bool = True


class BarabanUpdate(BaseModel):
    name: Optional[str] = None
    target_audience: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class BarabanOut(BaseModel):
    id: int
    name: str
    target_audience: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    prizes: List[BarabanPrizeOut] = []

    class Config:
        from_attributes = True


# Dashboard
class DashboardStats(BaseModel):
    total_products: int
    total_categories: int
    total_customers: int
    total_orders: int
    total_revenue: float
    active_barabanlar: int
    blocked_customers: int
    low_stock_products: int
