from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated, List
from sqlmodel import Session, select
from fastapi import APIRouter, Depends, UploadFile, File
from typing import List
from fastapi.responses import FileResponse
import os

from database import get_session
from core.security import get_current_user
from model.user import User
from model.product import ProductCreate, ProductResponse, ProductImage, Product
from core.local_common import upload_images, upload_image, remove_image
from model.product_publish import ProductPublishCreate, ProductPublish, ProductPublishResponse, ProductPublishUpdate, PublishType

router = APIRouter(prefix="/products", tags=["products"])

SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/add/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def add_product(
    session: SessionDep,
    prduct_data: ProductCreate = Depends(ProductCreate.as_form),
    images: List[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):

    product = Product(
        title=prduct_data.title,
        description=prduct_data.description,
        category=prduct_data.category,
        quantity=prduct_data.quantity,
        quantity_name=prduct_data.quantity_name,
        quality=prduct_data.quality,
        pickup_address=prduct_data.pickup_address,
        latitude=prduct_data.latitude,
        longitude=prduct_data.longitude,
        user_id=current_user.id,
        publish=False,
        status="draft"
    )

    session.add(product)
    session.commit()
    session.refresh(product)

    if images:
        image_urls = upload_images(images, "products")

        for url in image_urls:
            product_image = ProductImage(
                product_id=product.id,
                image_url=url
            )
            session.add(product_image)

        session.commit()

    session.refresh(product)

    return product

@router.post("/{product_id}/upload-images", status_code=status.HTTP_201_CREATED)
def upload_product_images(product_id: str, session: SessionDep, images: List[UploadFile] = File(...), current_user: User = Depends(get_current_user)):
    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    image_urls = upload_images(images, "products")
    product_images = []

    for url in image_urls:
        product_image = ProductImage(
            product_id=product.id,
            image_url=url
        )
        session.add(product_image)
        product_images.append(product_image)

    session.commit()

    for img in product_images:
        session.refresh(img)

    return product_images

@router.get("/details/", response_model=List[ProductResponse],status_code=status.HTTP_200_OK)
def read_productions(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    try:
        statement = select(Product).offset(offset).limit(limit)
        products = session.exec(statement).all()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/detail/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def read_prduction(product_id: str, session: SessionDep, current_user: User = Depends(get_current_user)):
    try:
        statement = select(Product).where(Product.id == product_id)
        user = session.exec(statement).first()
        if not user:
            raise HTTPException(status_code=404, detail="Product not found")
            
        return user
    
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.put("/update/{product_id}", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def update_product_detail(product_id:str, session:SessionDep, product_data: ProductCreate = Depends(ProductCreate.as_form), current_user: User = Depends(get_current_user)):
    try:
        product = session.get(Product, product_id)

        if not product:
            raise HTTPException(
                status_code=400,
                detail=f"prduct with {product_id} not found"
            )
        
        if product.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to update this product"
            )
        update_data = product_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(product, key, value)

        session.add(product)
        session.commit()
        session.refresh(product)

        return product
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error updating product: {str(e)}"
        )
    
@router.delete("/delete/{product_id}", status_code=status.HTTP_200_OK)
def delete_production(product_id:str, session:SessionDep,current_user: User = Depends(get_current_user)):
    try:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(
                status_code=400,
                detail=f"prduct with {product_id} not found"
            )
        
        if product.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to update this product"
            )
        
        session.delete(product)
        session.commit()
        return {
            "message": f"Production with id {product_id} deleted successfully",
            "deleted_user": {
                "id": product.id,
                "name":product.title
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error updating product: {str(e)}"
        )

@router.delete("/bulk_delete/", status_code=status.HTTP_200_OK)
def bulk_deletion(product_ids: List[str], session: SessionDep, current_user: User = Depends(get_current_user)):
    try:
        deleted_products = []
        not_found = []

        for product_id in product_ids:
            product = session.get(Product, product_id)
            if product:
                session.delete(product)
                deleted_products.append({"id":product.id, "title":product.title})
            else:
                not_found.append(product_id)

        return {
            "message": f"Successfully deleted {len(deleted_products)} users",
            "deleted_products": deleted_products,
            "not_found": not_found
        } 
        

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error updating product: {str(e)}"
        )

@router.patch("/update_image/{image_id}", status_code=status.HTTP_200_OK)
def update_product_image(
    image_id: str,
    session: SessionDep,
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    product_image = session.get(ProductImage, image_id)

    if not product_image:
        raise HTTPException(status_code=404, detail="Image not found")

    product = session.get(Product, product_image.product_id)

    if product.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        old_file_path = product_image.image_url.lstrip("/")
        if old_file_path:
            remove_image(old_file_path)

        new_url = upload_image(image, "products")

        product_image.image_url = new_url
        session.add(product_image)
        session.commit()
        session.refresh(product_image)

        return product_image
    
    except HTTPException:
        raise

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/delete_image/{image_id}", status_code=status.HTTP_200_OK)
def delete_product_image(
    image_id: str,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    product_image = session.get(ProductImage, image_id)

    if not product_image:
        raise HTTPException(status_code=404, detail="Image not found")

    product = session.get(Product, product_image.product_id)

    if product.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        file_path = product_image.image_url.lstrip("/")

        if file_path:
            remove_image(file_path)

        session.delete(product_image)
        session.commit()

        return {"message": "Product image deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/see_production_image/{image_id}", status_code=status.HTTP_200_OK)
def get_product_image(
    image_id: str,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):

    product_image = session.get(ProductImage, image_id)

    if not product_image:
        raise HTTPException(
            status_code=404,
            detail="Image not found"
        )
    file_path = product_image.image_url.lstrip("/")

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="Image file not found"
        )
    return FileResponse(file_path)

@router.post("/publish", response_model=ProductPublishResponse)
def publish_product(
    data: ProductPublishCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    product = session.exec(
        select(Product).where(Product.id == data.product_id)
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    publish = session.exec(
        select(ProductPublish).where(ProductPublish.product_id == data.product_id)
    ).first()

    if publish:
        publish.publish_type = data.publish_type
        publish.amount = data.amount
    else:
        publish = ProductPublish(
            product_id=data.product_id,
            publish_type=data.publish_type,
            amount=data.amount
        )
        session.add(publish)

    product.publish = True
    product.status = "published"

    session.add(product)
    session.commit()
    session.refresh(publish)

    return publish

@router.put("/publish/{product_id}")
def update_publish(
    product_id: str,
    data: ProductPublishUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    publish = session.exec(
        select(ProductPublish).where(ProductPublish.product_id == product_id)
    ).first()

    if not publish:
        raise HTTPException(status_code=404, detail="Publish record not found")

    if data.publish_type is not None:
        publish.publish_type = data.publish_type

    if data.amount is not None:
        publish.amount = data.amount

    if data.publish_type == PublishType.FREE:
        publish.amount = None

    if data.publish_type == PublishType.EXCHANGE:
        publish.amount = None

    product = session.exec(
        select(Product).where(Product.id == product_id)
    ).first()

    if product:
        product.publish = True
        product.status = "published"
        session.add(product)

    session.add(publish)
    session.commit()
    session.refresh(publish)

    return publish