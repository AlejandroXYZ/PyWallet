from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

class TimestampMixin:

    """Añade marcas de tiempo automáticas a cualquier modelo."""
    
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        default=lambda: datetime.now(timezone.utc)
    )
    
