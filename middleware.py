from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class LogsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Capturando o request
        body = await request.body()
        print("Request:")
        print(f"URL: {request.url}")
        print(f"Headers: {dict(request.headers)}")
        print(f"Body: {body.decode('utf-8')}")

        # Passando para o próximo middleware ou endpoint
        response: Response = await call_next(request)

        # Capturando o response
        print("Response:")
        print(f"Status Code: {response.status_code}")
        response_body = [section async for section in response.body_iterator]
        response.body_iterator = iter(response_body)
        print(f"Body: {b''.join(response_body).decode('utf-8')}")

        return response