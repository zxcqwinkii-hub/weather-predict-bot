from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    telegram_id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(nullable=True)
    style: Mapped[str] = mapped_column(nullable=True)
    is_onboarded: Mapped[bool] = mapped_column(default=False)
    
    def __repr__(self):
        return f"<User {self.telegram_id}: {self.city}>"