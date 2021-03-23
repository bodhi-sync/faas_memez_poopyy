from datetime import datetime
from typing import Any, Dict, Optional

from addict import Addict as DDict
from fastapi import FastAPI, HTTPException
from inflection import tableize
from loguru import logger
from mangostar import commands as comms
from mangostar.circular import DBResponse
# from mangostar.mangostar import commands as comm
from pydantic import BaseModel, root_validator

FUNCTION_NAME = 'insert_record'
FUNCTION_VERSION = '0.0.1'
FUNCTION_SUMMARY = "Gets the entity and schema of the model we send in and converts into a graph representation that we can manipulate later."
FUNCTION_RESPONSE_DESC = "Relfecting what was sent to us."


class RequestModel(BaseModel):
    data: Dict


class InsertableRecord(BaseModel):
    data: Dict[str, Any]
    event_at: datetime = datetime.now()
    bucket: Optional[str]
    tags: Dict[str, Any] = {}

    @root_validator
    def check_bucket(cls, values: dict):
        doti = DDict(**values)
        buck = doti.bucket
        if buck:
            doti.bucket = tableize(buck)
            return doti.to_dict()

        if "bucket" not in doti.data.keys():
            raise ValueError("Bucket not added.")

        nested_bucket = doti.data.bucket
        if not isinstance(nested_bucket, str):
            raise TypeError(
                "A bucket was found in 'data' but it wasn't the right type.")
        doti.data.pop("bucket", None)

        doti.bucket = str(nested_bucket)
        return doti.to_dict()


class ResponseModel(BaseModel):
    data: Dict


def logic(req: InsertableRecord) -> ResponseModel:
    try:
        db_response = comms.insert_dict(**req.dict())
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"An API Error occurred: Detail: {str(e)}")
    return ResponseModel(data=db_response.dict())


async def logic_async(req: RequestModel) -> ResponseModel:
    try:
        res = ResponseModel(data=req.data)
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"An API Error occurred. Further Detail")
    return res


def handle(req: RequestModel) -> ResponseModel:
    """Handle the incoming request .

    Args:
        req (RequestModel): data inputs

    Returns:
        ResponseModel: [description]
    """
    print("Eating shit")
    return logic(InsertableRecord(**req.data))


async def handle_async(req):
    """handle a request to the function
    Args:
        req (dict): request body
    """
    return await logic_async(req)


async def handle_async_stream(req):
    """handle a request to the function asynchronously and with a stream.
    
    We assume to use async for this for all other IO.
    Args:
        req (dict): request body
    """
    yield await logic_async(req)
