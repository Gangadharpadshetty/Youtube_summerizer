import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://youtube_summerizer_user:nafpLGb0TXS3Ck4OFcA02Cu104sYfQ1I@dpg-d6fhbp6a2pns73dk91f0-a.oregon-postgres.render.com/youtube_summerizer")
FERNET_KEY = os.getenv("FERNET_KEY", "w7s9KxR2q8L0p3Vt6Yz4nB1mQ2hS9dF0uW5vA3yZ6k")