from fastapi import APIRouter
from .math_route import router as math
from .cs_route import router as cs

router = APIRouter()


# Include sub_routers
router.include_router(cs)
router.include_router(math)