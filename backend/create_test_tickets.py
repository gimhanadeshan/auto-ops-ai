from app.core.database import SessionLocal
from app.models.ticket import TicketDB
from app.models.user import UserDB
from datetime import datetime

db = SessionLocal()

# Delete existing tickets
db.query(TicketDB).delete()
db.commit()

# Get admin user
user = db.query(UserDB).filter(UserDB.email == 'admin@acme.com').first()

# Create tickets with categories matching the ML training data
tickets = [
    TicketDB(
        title='VPN Connection Failed',
        description='Unable to connect to company VPN from remote location. Connection times out after authentication.',
        priority='high',
        status='open',
        user_email=user.email,
        category=None,  # Will be handled by title matching
        created_at=datetime.utcnow()
    ),
    TicketDB(
        title='Password Reset Required',
        description='User forgot their domain password and cannot access any company systems.',
        priority='medium',
        status='open',
        user_email=user.email,
        category=None,
        created_at=datetime.utcnow()
    ),
    TicketDB(
        title='Software Crash - Excel',
        description='Microsoft Excel keeps crashing when opening large spreadsheets with macros enabled.',
        priority='medium',
        status='in_progress',
        user_email=user.email,
        category=None,
        created_at=datetime.utcnow()
    ),
    TicketDB(
        title='Printer Issue - Floor 3',
        description='HP LaserJet printer on third floor is showing paper jam error but no paper is stuck.',
        priority='low',
        status='open',
        user_email=user.email,
        category=None,
        created_at=datetime.utcnow()
    ),
    TicketDB(
        title='Hardware Failure - Monitor',
        description='User workstation monitor completely black, no power light, replaced power cable but still not working.',
        priority='high',
        status='open',
        user_email=user.email,
        category=None,
        created_at=datetime.utcnow()
    ),
    TicketDB(
        title='VPN Connection Slow',
        description='VPN connection established but extremely slow performance downloading files from network drives.',
        priority='medium',
        status='open',
        user_email=user.email,
        category=None,
        created_at=datetime.utcnow()
    ),
    TicketDB(
        title='Software Crash - Outlook',
        description='Outlook application crashes repeatedly when trying to send emails with attachments larger than 10MB.',
        priority='high',
        status='open',
        user_email=user.email,
        category=None,
        created_at=datetime.utcnow()
    ),
]

db.add_all(tickets)
db.commit()

print(f'✅ Created {len(tickets)} tickets with proper categories for ML model')
print('\nTickets created:')
for t in tickets:
    print(f'  - {t.title} (Priority: {t.priority}, Status: {t.status})')

db.close()
