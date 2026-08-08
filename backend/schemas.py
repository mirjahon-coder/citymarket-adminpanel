from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime


# ─── Auth ───────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CustomerRegister(BaseModel):
    phone: str
    password: str
    full_name: Optional[str] = None

class CustomerProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    birth_date: Optional[str] = None
    avatar_url: Optional[str] = None

class AddressCreate(BaseModel):
    label: str = "uy"
    address: str
    city: Optional[str] = None
    apartment: Optional[str] = None
    is_default: bool = False

class AddressOut(AddressCreate):
    id: int
    class Config: from_attributes = True

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


# ─── Category ───────────────────────────────────────────────────────────────
class CategoryCreate(BaseModel):
    name: str
    name_uz: Optional[str] = None
    name_ru: Optional[str] = None
    name_en: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    image_url: Optional[str] = None
    banner_url: Optional[str] = None
    cover_url: Optional[str] = None
    location: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int = 0
    is_active: bool = True
    show_on_home: bool = False
    show_in_menu: bool = True
    is_popular: bool = False
    is_new: bool = False
    is_recommended: bool = False
    filter_enabled: bool = False
    show_in_discount: bool = False

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    name_uz: Optional[str] = None
    name_ru: Optional[str] = None
    name_en: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    image_url: Optional[str] = None
    banner_url: Optional[str] = None
    cover_url: Optional[str] = None
    location: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    show_on_home: Optional[bool] = None
    show_in_menu: Optional[bool] = None
    is_popular: Optional[bool] = None
    is_new: Optional[bool] = None
    is_recommended: Optional[bool] = None
    filter_enabled: Optional[bool] = None
    show_in_discount: Optional[bool] = None

class CategoryOut(BaseModel):
    id: int
    name: str
    name_uz: Optional[str]
    name_ru: Optional[str]
    name_en: Optional[str]
    slug: Optional[str]
    description: Optional[str]
    icon_url: Optional[str]
    image_url: Optional[str]
    banner_url: Optional[str]
    cover_url: Optional[str]
    location: Optional[str]
    parent_id: Optional[int]
    sort_order: int
    is_active: bool
    show_on_home: bool
    show_in_menu: bool
    is_popular: bool
    is_new: bool
    is_recommended: bool
    filter_enabled: bool
    show_in_discount: bool
    created_at: datetime
    class Config:
        from_attributes = True


# ─── Product Image ───────────────────────────────────────────────────────────
class ProductImageOut(BaseModel):
    id: int
    image_url: str
    is_primary: bool
    order_index: int
    class Config:
        from_attributes = True


# ─── Product ─────────────────────────────────────────────────────────────────
class ProductCreate(BaseModel):
    # Nomlar
    name: str
    name_uz: Optional[str] = None
    name_ru: Optional[str] = None
    name_en: Optional[str] = None
    # Identifikatorlar
    sku: Optional[str] = None
    barcode: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    model_name: Optional[str] = None
    # Kategoriya
    category_id: Optional[int] = None
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = None
    # Tavsiflar
    short_description: Optional[str] = None
    description: Optional[str] = None
    full_description: Optional[str] = None
    # Rasmlar
    main_image_url: Optional[str] = None
    gallery_images: Optional[List[str]] = None
    image_360_url: Optional[str] = None
    video_url: Optional[str] = None
    # Narxlar
    price: float = 0
    sale_price: Optional[float] = None
    purchase_price: Optional[float] = None
    cashback_percent: Optional[float] = 0
    bonus_points: Optional[float] = 0
    vat_percent: Optional[float] = 0
    # Ombor
    warehouse_name: Optional[str] = None
    stock: int = 0
    min_quantity: int = 1
    max_order_qty: Optional[int] = None
    user_order_limit: Optional[int] = None
    # Yetkazib berish
    weight: Optional[float] = None
    length_cm: Optional[float] = None
    width_cm: Optional[float] = None
    height_cm: Optional[float] = None
    delivery_type: Optional[str] = None
    delivery_price: Optional[float] = 0
    free_delivery_from: Optional[float] = None
    # Variantlar va xususiyatlar
    variants: Optional[List[Dict[str, Any]]] = None
    specs: Optional[List[Dict[str, str]]] = None
    # SEO
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    canonical_url: Optional[str] = None
    # Holat flaglari
    is_active: bool = True
    is_in_stock: bool = True
    is_new: bool = False
    is_popular: bool = False
    is_recommended: bool = False
    is_premium: bool = False
    is_bestseller: bool = False
    is_flash_sale: bool = False
    is_day_product: bool = False
    is_week_product: bool = False
    is_month_product: bool = False
    is_trend: bool = False
    has_discount: bool = False
    discount_ending: bool = False
    is_free_delivery: bool = False
    has_cashback: bool = False
    has_warranty: bool = False
    is_original: bool = False
    is_certified: bool = False
    is_import: bool = False
    is_local: bool = False
    is_returnable: bool = False
    is_exchangeable: bool = False
    is_online_payment: bool = True
    is_installment: bool = False
    show_description: bool = True
    show_specs: bool = True
    allow_reviews: bool = True
    allow_qa: bool = True
    allow_rating: bool = True
    allow_wishlist: bool = True
    allow_compare: bool = True
    show_in_recommended: bool = False
    show_on_home: bool = False
    show_in_banner: bool = False
    show_in_carousel: bool = False
    is_secret: bool = False
    is_archived: bool = False
    is_moderated: bool = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    name_uz: Optional[str] = None
    name_ru: Optional[str] = None
    name_en: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    model_name: Optional[str] = None
    category_id: Optional[int] = None
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    full_description: Optional[str] = None
    main_image_url: Optional[str] = None
    gallery_images: Optional[List[str]] = None
    image_360_url: Optional[str] = None
    video_url: Optional[str] = None
    price: Optional[float] = None
    sale_price: Optional[float] = None
    purchase_price: Optional[float] = None
    cashback_percent: Optional[float] = None
    bonus_points: Optional[float] = None
    vat_percent: Optional[float] = None
    warehouse_name: Optional[str] = None
    stock: Optional[int] = None
    min_quantity: Optional[int] = None
    max_order_qty: Optional[int] = None
    user_order_limit: Optional[int] = None
    weight: Optional[float] = None
    length_cm: Optional[float] = None
    width_cm: Optional[float] = None
    height_cm: Optional[float] = None
    delivery_type: Optional[str] = None
    delivery_price: Optional[float] = None
    free_delivery_from: Optional[float] = None
    variants: Optional[List[Dict[str, Any]]] = None
    specs: Optional[List[Dict[str, str]]] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    canonical_url: Optional[str] = None
    is_active: Optional[bool] = None
    is_in_stock: Optional[bool] = None
    is_new: Optional[bool] = None
    is_popular: Optional[bool] = None
    is_recommended: Optional[bool] = None
    is_premium: Optional[bool] = None
    is_bestseller: Optional[bool] = None
    is_flash_sale: Optional[bool] = None
    is_day_product: Optional[bool] = None
    is_week_product: Optional[bool] = None
    is_month_product: Optional[bool] = None
    is_trend: Optional[bool] = None
    has_discount: Optional[bool] = None
    discount_ending: Optional[bool] = None
    is_free_delivery: Optional[bool] = None
    has_cashback: Optional[bool] = None
    has_warranty: Optional[bool] = None
    is_original: Optional[bool] = None
    is_certified: Optional[bool] = None
    is_import: Optional[bool] = None
    is_local: Optional[bool] = None
    is_returnable: Optional[bool] = None
    is_exchangeable: Optional[bool] = None
    is_online_payment: Optional[bool] = None
    is_installment: Optional[bool] = None
    show_description: Optional[bool] = None
    show_specs: Optional[bool] = None
    allow_reviews: Optional[bool] = None
    allow_qa: Optional[bool] = None
    allow_rating: Optional[bool] = None
    allow_wishlist: Optional[bool] = None
    allow_compare: Optional[bool] = None
    show_in_recommended: Optional[bool] = None
    show_on_home: Optional[bool] = None
    show_in_banner: Optional[bool] = None
    show_in_carousel: Optional[bool] = None
    is_secret: Optional[bool] = None
    is_archived: Optional[bool] = None
    is_moderated: Optional[bool] = None

class ProductVideoOut(BaseModel):
    id: int
    product_id: int
    video_url: str
    title: Optional[str]
    created_at: datetime
    class Config: from_attributes = True

class ProductOut(BaseModel):
    id: int
    name: str
    name_uz: Optional[str]
    name_ru: Optional[str]
    name_en: Optional[str]
    sku: Optional[str]
    barcode: Optional[str]
    brand: Optional[str]
    manufacturer: Optional[str]
    model_name: Optional[str]
    category_id: Optional[int]
    subcategory: Optional[str]
    tags: Optional[List[str]]
    short_description: Optional[str]
    description: Optional[str]
    full_description: Optional[str]
    main_image_url: Optional[str]
    gallery_images: Optional[List[str]]
    image_360_url: Optional[str]
    video_url: Optional[str]
    price: float
    sale_price: Optional[float]
    purchase_price: Optional[float]
    cashback_percent: Optional[float]
    bonus_points: Optional[float]
    vat_percent: Optional[float]
    warehouse_name: Optional[str]
    stock: int
    min_quantity: int
    max_order_qty: Optional[int]
    user_order_limit: Optional[int]
    weight: Optional[float]
    length_cm: Optional[float]
    width_cm: Optional[float]
    height_cm: Optional[float]
    delivery_type: Optional[str]
    delivery_price: Optional[float]
    free_delivery_from: Optional[float]
    variants: Optional[List[Dict[str, Any]]]
    specs: Optional[List[Dict[str, str]]]
    seo_title: Optional[str]
    seo_description: Optional[str]
    seo_keywords: Optional[str]
    canonical_url: Optional[str]
    views_count: int
    sold_count: int
    rating: float
    reviews_count: int
    is_active: bool
    is_in_stock: bool
    is_new: bool
    is_popular: bool
    is_recommended: bool
    is_premium: bool
    is_bestseller: bool
    is_flash_sale: bool
    is_day_product: bool
    is_week_product: bool
    is_month_product: bool
    is_trend: bool
    has_discount: bool
    discount_ending: bool
    is_free_delivery: bool
    has_cashback: bool
    has_warranty: bool
    is_original: bool
    is_certified: bool
    is_import: bool
    is_local: bool
    is_returnable: bool
    is_exchangeable: bool
    is_online_payment: bool
    is_installment: bool
    show_description: bool
    show_specs: bool
    allow_reviews: bool
    allow_qa: bool
    allow_rating: bool
    allow_wishlist: bool
    allow_compare: bool
    show_in_recommended: bool
    show_on_home: bool
    show_in_banner: bool
    show_in_carousel: bool
    is_secret: bool
    is_archived: bool
    is_moderated: bool
    created_at: datetime
    images: List[ProductImageOut] = []
    videos: List[ProductVideoOut] = []
    class Config:
        from_attributes = True


# ─── Customer ────────────────────────────────────────────────────────────────
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

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    product_name: str
    unit_price: float

class CartOut(BaseModel):
    id: int
    items: List[CartItemOut]
    total_price: float

class OrderCreate(BaseModel):
    address_id: Optional[int] = None
    payment_method: str = "cash"

class WinningOut(BaseModel):
    id: int
    baraban_type: str
    prize_name: str
    qr_token: str
    status: str
    expires_at: Optional[datetime]
    created_at: datetime
    class Config: from_attributes = True

class DeviceTokenCreate(BaseModel):
    device_token: str

class NotificationCreate(BaseModel):
    title: str
    body: str
    customer_id: Optional[int] = None

class NotificationOut(BaseModel):
    id: int
    customer_id: Optional[int]
    title: str
    body: str
    is_read: bool
    created_at: datetime
    class Config: from_attributes = True

class BannerCreate(BaseModel):
    title: str
    image_url: str
    link_url: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0

class PromotionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    discount_percent: float = 0
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    is_active: bool = True

class RoleCreate(BaseModel):
    name: str
    permissions: List[str] = []

class RoleAssignment(BaseModel):
    role_id: int

class VideoCreate(BaseModel):
    video_url: str
    title: Optional[str] = None

class CashierVerify(BaseModel):
    qr_token: str

class BlockUserRequest(BaseModel):
    reason: Optional[str] = None


# ─── Order ───────────────────────────────────────────────────────────────────
class OrderItemOut(BaseModel):
    id: int
    product_name: str
    quantity: int
    unit_price: float
    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    status: str
    total_price: float
    payment_status: str
    paid_at: Optional[datetime]
    click_trans_id: Optional[int]
    click_paydoc_id: Optional[int]
    created_at: datetime
    items: List[OrderItemOut] = []
    class Config:
        from_attributes = True


# ─── Baraban ─────────────────────────────────────────────────────────────────
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


# ─── Dashboard ───────────────────────────────────────────────────────────────
class DashboardStats(BaseModel):
    total_products: int
    total_categories: int
    total_customers: int
    total_orders: int
    total_revenue: float
    active_barabanlar: int
    blocked_customers: int
    low_stock_products: int
