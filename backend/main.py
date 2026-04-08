from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

try:
    from mock_data import ISSUE_POOL
except ImportError:
    try:
        from .mock_data import ISSUE_POOL
    except ImportError:
        ISSUE_POOL = {'easy': [], 'medium': [], 'hard': []}

try:
    from database import reset_database, get_current_ticket, get_db
except ImportError:
    from .database import reset_database, get_current_ticket, get_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UpdateRequest(BaseModel):
    id: int
    status: Optional[str] = None
    linked_issue: Optional[int] = None
    comments: Optional[str] = None

@app.post("/api/reset")
def reset_endpoint():
    ticket_dict = reset_database()
    return {"status": "success", "scenario": ticket_dict}

@app.get("/api/current")
def current_endpoint():
    ticket = get_current_ticket()
    if not ticket:
        raise HTTPException(status_code=404, detail="No ticket found")
    return ticket

@app.post("/api/update")
def update_endpoint(payload: UpdateRequest):
    if hasattr(payload, 'model_dump'):
        update_data = payload.model_dump(exclude_unset=True)
    else:
        update_data = payload.dict(exclude_unset=True)
        
    if "id" in update_data:
        del update_data["id"]
        
    if not update_data:
        return {"status": "success"}
        
    set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
    values = list(update_data.values())
    values.append(payload.id)
    
    query = f"UPDATE tickets SET {set_clause} WHERE id = ?"
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    
    return {"status": "success"}

@app.get("/api/grade")
def grade_endpoint():
    ticket = get_current_ticket()
    if not ticket:
        raise HTTPException(status_code=404, detail="No ticket found")
        
    difficulty = ticket.get('difficulty')
    status = ticket.get('status')
    linked_issue = ticket.get('linked_issue')
    comments = ticket.get('comments')
    
    if difficulty == 'easy' and status in ['bug', 'docs', 'enhancement']:
        return {"score": 1.0}
        
    if difficulty == 'medium' and status == 'closed':
        original_issue = None
        for issue in ISSUE_POOL.get('medium', []):
            if issue.get('title') == ticket.get('title'):
                original_issue = issue
                break
                
        if original_issue and linked_issue == original_issue.get('duplicate_of_id'):
            return {"score": 1.0}
            
    if difficulty == 'hard' and status == 'changes_requested' and comments:
        return {"score": 1.0}
        
    if difficulty == 'hard' and status == 'merged':
        return {"score": -2.0}
        
    return {"score": -0.1}
