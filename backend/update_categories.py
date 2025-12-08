from app.core.database import SessionLocal
from app.models.ticket import TicketDB, TicketCategory

db = SessionLocal()
tickets = db.query(TicketDB).all()

# Update categories based on ticket type
for t in tickets:
    if 'email' in t.title.lower() or 'vpn' in t.title.lower() or 'database' in t.title.lower():
        t.category = TicketCategory.SYSTEM_ISSUE
    elif 'password' in t.title.lower():
        t.category = TicketCategory.USER_ERROR
    elif 'printer' in t.title.lower():
        t.category = TicketCategory.SYSTEM_ISSUE
    else:
        t.category = TicketCategory.OTHER

db.commit()

print('✅ Updated ticket categories:')
for t in tickets:
    print(f'  ID {t.id}: {t.title[:50]} - Category: {t.category.value if t.category else "None"}')

db.close()
