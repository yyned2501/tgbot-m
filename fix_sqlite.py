import asyncio
import aiosqlite


async def add_column_to_table(
    db_path: str, table_name: str, column_name: str, column_type: str
):
    # 连接到SQLite数据库
    async with aiosqlite.connect(db_path) as conn:
        async with conn.cursor() as cursor:
            # 构建ALTER TABLE语句
            alter_table_sql = f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name} {column_type}
            """
            try:
                # 执行ALTER TABLE语句
                await cursor.execute(alter_table_sql)
                # 提交事务
                await conn.commit()
                print(
                    f"Column '{column_name}' added successfully to table '{table_name}'."
                )
            except aiosqlite.Error as e:
                print(f"An error occurred: {e}")


async def rename_column_in_table(
    db_path: str, table_name: str, old_column_name: str, new_column_name: str
):
    # 连接到SQLite数据库
    async with aiosqlite.connect(db_path) as conn:
        async with conn.cursor() as cursor:
            # 构建ALTER TABLE语句
            alter_table_sql = f"""
            ALTER TABLE {table_name}
            RENAME COLUMN {old_column_name} TO {new_column_name};
            """
            try:
                # 执行ALTER TABLE语句
                await cursor.execute(alter_table_sql)
                # 提交事务
                await conn.commit()
                print(
                    f"Column '{old_column_name}' in table '{table_name}' has been renamed to '{new_column_name}'."
                )
            except aiosqlite.Error as e:
                print(f"An error occurred: {e}")


# 使用示例
async def main():
    try:
        await rename_column_in_table("tgbot.db", "zqydx", "rel_betbonus", "betbonus")
    except:
        pass
    try:
        await add_column_to_table("tgbot.db", "zqydx", "user_bonus", "INT")
    except:
        pass
    try:
        await add_column_to_table("tgbot.db", "zqydx", "max_bet_bonus", "INT")
    except:
        pass

# 运行异步主函数
asyncio.run(main())
