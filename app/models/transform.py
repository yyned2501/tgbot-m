from sqlalchemy import (
    ForeignKey,
    String,
    Integer,
    BigInteger,
    func,
    select,
)
import pyrogram
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import TimeBase
from app.models import ASSession


class User(TimeBase):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    async def get_bonus_sum_for_site(self, site_name: str) -> int:
        """
        获取当前用户在指定站点的 bonus 总和。

        :param site_name: 站点名称
        :type site_name: str
        :return: 站点 bonus 的总和，如果不存在则返回 0
        :rtype: int
        """

        session = ASSession()
        bonus_sum_select = select(
            func.sum(Transform.bonus).filter(
                Transform.user_id == self.id, Transform.site == site_name
            )
        )
        bonus_sum = (await session.execute(bonus_sum_select)).scalar_one_or_none()
        return bonus_sum if bonus_sum is not None else 0

    async def get_bonus_get_sum_for_site(self, site_name: str) -> int:
        """
        获取当前用户在指定站点的 发送给我的 bonus 总和。

        :param site_name: 站点名称
        :type site_name: str
        :return: 站点 bonus 的总和，如果不存在则返回 0
        :rtype: int
        """

        session = ASSession()
        bonus_sum_select = select(
            func.sum(Transform.bonus).filter(
                Transform.user_id == self.id,
                Transform.site == site_name,
                Transform.bonus > 0,
            )
        )
        bonus_sum = (await session.execute(bonus_sum_select)).scalar_one_or_none()
        return bonus_sum if bonus_sum is not None else 0

    async def get_bonus_post_sum_for_site(self, site_name: str) -> int:
        """
        获取当前用户在指定站点的 我发送的 bonus 总和。

        :param site_name: 站点名称
        :type site_name: str
        :return: 站点 bonus 的总和，如果不存在则返回 0
        :rtype: int
        """

        session = ASSession()
        bonus_sum_select = select(
            func.sum(Transform.bonus).filter(
                Transform.user_id == self.id,
                Transform.site == site_name,
                Transform.bonus < 0,
            )
        )
        bonus_sum = (await session.execute(bonus_sum_select)).scalar_one_or_none()
        return -bonus_sum if bonus_sum is not None else 0

    @classmethod
    async def get(cls, tg_user: pyrogram.types.User):
        """
        获取或创建用户记录。

        :param tg_user: 用户对象
        :type tg_user: pyrogram.types.User
        :return: 用户记录
        :rtype: User
        """

        session = ASSession()
        username = " ".join(filter(None, [tg_user.first_name, tg_user.last_name]))
        user = await session.get(cls, tg_user.id)
        if user:
            if user.name != username:
                user.name = username
        else:
            user = cls(id=tg_user.id, name=username)
            session.add(user)
            await session.flush()
        return user

    async def add_transform_record(self, site: str, bonus: int):
        """
        添加转账记录。

        :param site: 站点名称
        :type site: str
        :param bonus: 转账金额
        :type bonus: int
        """
        session = ASSession()
        transform = Transform(site=site, user_id=self.id, bonus=bonus)
        session.add(transform)
        await session.flush()


class Transform(TimeBase):
    __tablename__ = "transform"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site: Mapped[str] = mapped_column(String(32))
    user_id: Mapped[int] = mapped_column(BigInteger)
    bonus: Mapped[int] = mapped_column(Integer)
