from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCompareRequest, ProductCompareResponse, ProductItem, ProductListResponse

router=APIRouter(prefix="/api/v1/products", tags=["Products"])
_SORT_FIELDS={"energy":"energy_100g","protein":"protein_100g","sugar":"sugars_100g","fat":"fat_100g","saturated_fat":"saturated_fat_100g","fiber":"fiber_100g","sodium":"sodium_100g","data_completeness":"data_completeness"}

@router.get("", response_model=ProductListResponse)
def list_products(query: Optional[str]=Query(None), brand: Optional[str]=Query(None), category: Optional[str]=Query(None), sort: Optional[str]=Query(None), order: str=Query("asc", pattern="^(asc|desc)$"), offset: int=Query(0,ge=0), limit: int=Query(20,ge=1,le=100), db: Session=Depends(get_db)):
    statement=db.query(Product)
    if query:
        like=f"%{query.strip()}%"; statement=statement.filter(Product.product_name.ilike(like))
    if brand: statement=statement.filter(Product.brand.ilike(f"%{brand.strip()}%"))
    if category: statement=statement.filter(Product.category.ilike(f"%{category.strip()}%"))
    total=statement.order_by(None).count()
    field=_SORT_FIELDS.get(sort or "")
    if field:
        column=getattr(Product,field); statement=statement.order_by((column.desc() if order=="desc" else column.asc()).nullslast())
    else: statement=statement.order_by(Product.product_name.asc())
    return ProductListResponse(items=statement.offset(offset).limit(limit).all(),total=total,offset=offset,limit=limit)

@router.get("/{barcode}", response_model=ProductItem)
def get_product(barcode: int, db: Session=Depends(get_db)):
    product=db.query(Product).filter(Product.barcode==barcode).first()
    if not product: raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/compare", response_model=ProductCompareResponse)
def compare_products(payload: ProductCompareRequest, db: Session=Depends(get_db)):
    barcodes=list(dict.fromkeys(payload.barcodes))
    if not 2 <= len(barcodes) <= 4: raise HTTPException(status_code=422, detail="Compare between 2 and 4 products")
    products=db.query(Product).filter(Product.barcode.in_(barcodes)).all()
    by_barcode={product.barcode:product for product in products}
    missing=[barcode for barcode in barcodes if barcode not in by_barcode]
    if missing: raise HTTPException(status_code=404, detail=f"Products not found: {missing}")
    return ProductCompareResponse(items=[by_barcode[barcode] for barcode in barcodes])
