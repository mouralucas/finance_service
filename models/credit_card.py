import datetime
import uuid

from rolf_common.models import SQLModel
from sqlalchemy import String, ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CreditCardModel(SQLModel):
    __tablename__ = 'credit_card'

    owner_id: Mapped[uuid.UUID] = mapped_column('owner_id')
    nickname: Mapped[str] = mapped_column('nickname', String(50))
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('account.id'), nullable=True)
    account: Mapped["AccountModel"] = relationship(foreign_keys=[account_id], lazy='subquery')
    issue_date: Mapped[datetime.date] = mapped_column('issue_date', nullable=True)
    cancel_date: Mapped[datetime.date] = mapped_column('cancel_date', nullable=True)
    due_date: Mapped[int] = mapped_column('due_date', SmallInteger, nullable=True)
    close_date: Mapped[int] = mapped_column('close_date', SmallInteger, nullable=True)

