import asyncpg


class Settings:
    def __init__(self, **kwargs):
        self.guild_id = kwargs.pop('guild_id')
        self.log_enabled = kwargs.pop('log_enabled')
        self.log_channel = kwargs.pop('log_channel')
        self.trigger_on_mute = kwargs.pop('trigger_on_mute')
        self.trigger_on_manual = kwargs.pop('trigger_on_manual')


class SQL:
    def __init__(self, pool: asyncpg.pool.Pool):
        self.db = pool

    async def fast_setup(self, settings: Settings):
        await self.db.execute("""
        INSERT INTO guild_settings (guild_id, log_enabled, log_channel, trigger_on_mute, trigger_on_manual)
                VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (guild_id)
        DO UPDATE SET log_enabled = $2, log_channel = $3, trigger_on_mute = $4, trigger_on_manual = $5;
        """,
            settings.guild_id, settings.log_enabled, settings.log_channel,
            settings.trigger_on_mute, settings.trigger_on_manual)

    async def audit_log(self, ctx, channel):
        if channel is None:
            enabled = False
        else:
            enabled = True
        await self.db.execute("""
                INSERT INTO guild_settings (guild_id, log_enabled, log_channel)
                        VALUES ($1, $2, $3)
                ON CONFLICT (guild_id)
                DO UPDATE SET log_enabled = $2, log_channel = $3;
                """, ctx.guild.id, enabled, channel)

    async def fetch_settings(self, guild):
        settings = await self.db.fetchrow("""
        SELECT * FROM guild_settings
        WHERE guild_id = $1
        """, guild.id)
        return dict(settings)

    async def force_reason(self, ctx, setting: bool):
        await self.db.execute("""
        INSERT INTO guild_settings (guild_id, force_reason)
                        VALUES ($1, $2)
                ON CONFLICT (guild_id)
                DO UPDATE SET force_reason = $2;
        """, ctx.guild.id, setting)

    async def toggle_force_reason(self, guild):
        query = """
        UPDATE guild_settings
        SET trigger_on_manual = NOT trigger_on_manual
        WHERE guild_id = $1
        RETURNING trigger_on_manual;
        """
        return await self.db.fetchval(query, guild.id)

    async def log_avatar(self, ctx, setting: bool):
        await self.db.execute("""
                INSERT INTO guild_settings (guild_id, log_avatar)
                    VALUES ($1, $2)
                ON CONFLICT (guild_id)
                DO UPDATE SET log_avatar = $2;
                """, ctx.guild.id, setting)

    async def new_record(self, guild):
        await self.db.execute("""
           INSERT INTO guild_settings (guild_id)
                   VALUES ($1)
           ON CONFLICT DO NOTHING;
           """, guild.id)

    async def fetch_prefix(self, guild):
        return await self.db.fetchval("""
        SELECT prefix FROM guild_settings
        WHERE guild_id = $1;
        """, guild.id)

    async def update_prefix(self, guild, prefix: list= None):
        await self.db.execute("""
        INSERT INTO guild_settings (guild_id, prefix)
            VALUES ($1, $2)
        ON CONFLICT (guild_id)
        DO UPDATE SET prefix = $2
        """, guild.id, prefix)

    async def update_prefix_(self, guild_id, prefix: list= None):
        await self.db.execute("""
        INSERT INTO guild_settings (guild_id, prefix)
            VALUES ($1, $2)
        ON CONFLICT (guild_id)
        DO UPDATE SET prefix = $2
        """, guild_id, prefix)

    async def increment_kick(self):
        await self.db.execute("""
        UPDATE usage_stats
        SET kick_members = kick_members + 1
        WHERE guild_id = 0;
        """)

    async def increment_ban(self):
        await self.db.execute("""
        UPDATE usage_stats
        SET ban_members = ban_members + 1
        WHERE guild_id = 0;
        """)

    async def increment_soft(self):
        await self.db.execute("""
        UPDATE usage_stats
        SET soft_ban = soft_ban + 1
        WHERE guild_id = 0;
        """)

    async def delete_settings(self, ctx):
        await self.db.execute("""
        DELETE FROM guild_settings
        WHERE guild_id = $1;
        """, ctx.guild.id)

    async def reset_guild(self, id: int, prefix: list=None):
        await self.db.execute("""
        DELETE FROM guild_settings
        WHERE guild_id = $1;
        """, id)
        if prefix is None:
            await self.db.execute("""
            INSERT INTO guild_settings (guild_id)
            VALUES ($1)
            ON CONFLICT DO NOTHING;
            """, id)
        else:
            await self.db.execute("""
            INSERT INTO guild_settings (guild_id, prefix)
                VALUES ($1, $2)
            ON CONFLICT (guild_id)
            DO UPDATE SET prefix = $2
            """, id, prefix)

    async def toggle_manual_log(self, guild):
        return await self.db.fetchval("""
        UPDATE guild_settings
        SET trigger_on_manual = NOT trigger_on_manual
        WHERE guild_id = $1
        RETURNING trigger_on_manual;
        """, guild.id)

