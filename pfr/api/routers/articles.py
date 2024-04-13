from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/articles", tags=["articles"])


class GetArticlesInput(BaseModel):
    id: int


@router.get("/<token>")
async def get_summary_article(input_data: GetArticlesInput):
    pass
