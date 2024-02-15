from fastapi import APIRouter

router = APIRouter(prefix='/connection_test', tags=['Connection Test'])


@router.get('/')
def test():
    return {'success': True}

