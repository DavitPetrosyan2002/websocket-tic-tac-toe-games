from fastapi import WebSocket,WebSocketDisconnect,APIRouter

import json 


router = APIRouter(
    prefix="/game",
    tags=["games"]
)


def init_board():
    
    return [
        None, None, None,
        None, None, None,
        None, None, None,
    ]


board = init_board()

def is_draw():
    global board
    for cell in board:
        if not cell:
            return False
    board = init_board()
    return True

def if_won():
    global board
    if board[0] == board[1] == board[2] != None or \
            board[3] == board[4] == board[5] != None or \
            board[6] == board[7] == board[8] != None or \
            board[0] == board[3] == board[6] != None or \
            board[1] == board[4] == board[7] != None or \
            board[2] == board[5] == board[8] != None or \
            board[0] == board[4] == board[8] != None or \
            board[6] == board[4] == board[2] != None:
        board = init_board()
        return True
    return False

async def update_board(manager, data):
    ind = int(data['cell']) - 1
    data['init'] = False
    if not board[ind]:
        board[ind] = data['player']
        if if_won():
            data['message'] = "won"
        elif is_draw():
            data['message'] = "draw"
        else:
            data['message'] = "move"
    else:
        data['message'] = "choose another one"
    await manager.broadcast(data)
    if data['message'] in ['draw', 'won']:
        manager.active_connections = []



class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        if len(self.active_connections)>=2:
            await websocket.accept()
            await websocket.close(4000)
        else:    
            await websocket.accept()    
            self.active_connections.append(websocket)
            if  len(self.active_connections)==1:
                await websocket.send_json({
                    "init":True,
                    "player":"X",
                    "message":"waiting for another player"
                })  
            else:
                await websocket.send_json({
                    "init":True,
                    "player":"O",
                    "message":""
                })
                await self.active_connections[0].send_json({
                    "init":True,
                    "player":"X",
                    "message":"your turn "
                    }
                )  
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, data: str):
        for connection in self.active_connections:
            await connection.send_json(data)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data=json.loads(data)
            await update_board(manager,data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        