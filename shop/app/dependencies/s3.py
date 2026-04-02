from fastapi import Request

from shop.app.services.s3_service import S3Service


async def get_s3_service(request: Request) -> S3Service:
    return request.app.state.s3_service
