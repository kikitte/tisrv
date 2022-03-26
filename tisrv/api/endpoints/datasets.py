from fastapi import APIRouter, Request
from tisrv.api.models import DatasetResource

router = APIRouter()


@router.get('/', response_model=list[DatasetResource])
def get_datasets(request: Request):
    app = request.app
    return [i.api_response() for i in app.state.geo.data['datasets']]
