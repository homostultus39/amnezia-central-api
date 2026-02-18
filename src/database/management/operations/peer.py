import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import PeerModel


async def get_peer_by_id(session: AsyncSession, peer_id: uuid.UUID) -> PeerModel | None:
    result = await session.execute(
        select(PeerModel).where(PeerModel.id == peer_id)
    )
    return result.scalar_one_or_none()


async def get_peer_by_public_key(session: AsyncSession, public_key: str) -> PeerModel | None:
    result = await session.execute(
        select(PeerModel).where(PeerModel.public_key == public_key)
    )
    return result.scalar_one_or_none()


async def get_all_peers(session: AsyncSession) -> list[PeerModel]:
    result = await session.execute(select(PeerModel))
    return result.scalars().all()


async def get_peers_by_client_id(session: AsyncSession, client_id: uuid.UUID) -> list[PeerModel]:
    result = await session.execute(
        select(PeerModel).where(PeerModel.client_id == client_id)
    )
    return result.scalars().all()


async def get_peer_by_client_cluster_apptype(
    session: AsyncSession,
    client_id: uuid.UUID,
    cluster_id: uuid.UUID,
    app_type: str,
) -> PeerModel | None:
    result = await session.execute(
        select(PeerModel).where(
            PeerModel.client_id == client_id,
            PeerModel.cluster_id == cluster_id,
            PeerModel.app_type == app_type,
        )
    )
    return result.scalar_one_or_none()


async def create_peer(
    session: AsyncSession,
    client_id: uuid.UUID,
    cluster_id: uuid.UUID,
    public_key: str,
    private_key_hash: str,
    allocated_ip: str,
    endpoint: str,
    app_type: str,
    protocol: str
) -> PeerModel:
    peer = PeerModel(
        client_id=client_id,
        cluster_id=cluster_id,
        public_key=public_key,
        private_key_hash=private_key_hash,
        allocated_ip=allocated_ip,
        endpoint=endpoint,
        app_type=app_type,
        protocol=protocol
    )
    session.add(peer)
    await session.commit()
    await session.refresh(peer)
    return peer



async def delete_peer(session: AsyncSession, peer_id: uuid.UUID) -> bool:
    peer = await get_peer_by_id(session, peer_id)
    if not peer:
        return False

    await session.delete(peer)
    await session.commit()
    return True


async def delete_peers_by_client_id(session: AsyncSession, client_id: uuid.UUID) -> int:
    peers = await get_peers_by_client_id(session, client_id)
    count = len(peers)

    for peer in peers:
        await session.delete(peer)

    await session.commit()
    return count
