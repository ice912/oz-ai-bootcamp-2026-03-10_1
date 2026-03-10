import json
import uuid

from redis import asyncio as aredis
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
# from sqlalchemy import text

# from database import SessionFactory

# llm = Llama(
#   model_path=""
#)

redis_client = aredis.from_url("redis://redis:6379",decode_responses=TabError)

app = FastAPI()

# [1] 클라이언트에서 질문을 요청한다.

@app.post("/chats") # 데이터 전송 시 Body를 사용하므로 POST 권장
async def chat_handler(question: str = Body(..., embed=True)):
#question: str = Query(...),
#@app.get("/chats/{question}")
#question: str = Path(...),
        

        #[2] 답변 생성 작업 Enqueue
        job_id = str(uuid.uuid4()) #작업을 식별할 수 있는 식별자 발급
        channel = f"result:{job_id}"

        pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel)
        
        job = {"id": job_id, "question": question}
        await redis_client.lpush("inference_queue", json.dumps(job))
        
        async def event_generator():
                result = None
                async for message in pubsub.listen():
                        if message["type"] == "message":
                                data = message["data"]
                                if data == "[DONE]":
                                    break
                                yield data

                return StreamingResponse(
                        ...,
                        media_type="text/event-stream"
                )

