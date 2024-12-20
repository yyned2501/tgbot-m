from sqlalchemy import desc, select
from app.models.ydx import ZqYdxMulti, YdxHistory

from app.models import ASSession
from app.scripts.zhuque.ex.bet_modes import test
from app import scheduler,logger

logger.info("加载定时撤回更新")
async def refresh_model_withdrawal():
    logger.info("开始更新撤回")
    session = ASSession()
    async with session.begin():
        history_result = await session.execute(
            select(YdxHistory).order_by(desc(YdxHistory.id)).limit(4041)
        )
        history = history_result.scalars().all()
        data = [ydx_history.dx for ydx_history in history]
        model_data = test(data)
        models = await session.execute(select(ZqYdxMulti))
        for model in models.scalars():
            model.max_withdrawal = model_data[model.name]["max_withdrawal"]
            model.current_withdrawal = model_data[model.name]["current_withdraw"]


scheduler.add_job(refresh_model_withdrawal, "interval", minutes=10)
