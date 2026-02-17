import uuid
from enum import Enum
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import func, String, DateTime, UUID, ForeignKey

from src.database.base import Base


class UUIDMixin:
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class UserStatus(Enum):
    ACTIVE = "active"
    REVOKED = "revoked"


class SubscriptionStatus(Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    EXPIRED = "expired"


class AdminModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "admins"

    username: Mapped[str] = mapped_column(String(255), index=True, unique=True, nullable=False)
    pwd_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    user_status: Mapped[UserStatus] = mapped_column(String(50), default=UserStatus.ACTIVE.value, nullable=False)


class ClusterModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "clusters"

    name: Mapped[str] = mapped_column(String(255), index=True, unique=True, nullable=False)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    last_handshake: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    container_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    container_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    protocol: Mapped[str | None] = mapped_column(String(50), nullable=True)
    peers_count: Mapped[int] = mapped_column(nullable=False, default=0)
    online_peers_count: Mapped[int] = mapped_column(nullable=False, default=0)

    peers: Mapped[list["PeerModel"]] = relationship("PeerModel", back_populates="cluster", cascade="all, delete-orphan", uselist=True)


class ClientModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "clients"

    username: Mapped[str] = mapped_column(String(255), index=True, unique=True, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    subscription_status: Mapped[SubscriptionStatus] = mapped_column(String(50), default=SubscriptionStatus.TRIAL.value, nullable=False)
    trial_used: Mapped[bool] = mapped_column(nullable=False, default=False)
    last_subscription_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    peers: Mapped[list["PeerModel"]] = relationship("PeerModel", back_populates="client", cascade="all, delete-orphan", uselist=True)


class AppType(Enum):
    AMNEZIA_VPN = "amnezia_vpn"
    AMNEZIA_WG = "amnezia_wg"


class PeerModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "peers"

    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    cluster_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clusters.id"), nullable=False, index=True)
    public_key: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    private_key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    allocated_ip: Mapped[str] = mapped_column(String(50), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    app_type: Mapped[AppType] = mapped_column(String(50), default=AppType.AMNEZIA_VPN.value, nullable=False, index=True)
    protocol: Mapped[str] = mapped_column(String(50), nullable=False)

    client: Mapped["ClientModel"] = relationship("ClientModel", back_populates="peers")
    cluster: Mapped["ClusterModel"] = relationship("ClusterModel", back_populates="peers")


class TariffModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tariffs"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    days: Mapped[int] = mapped_column(nullable=False)
    price_rub: Mapped[int] = mapped_column(nullable=False)
    price_stars: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0, index=True)
