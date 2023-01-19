import logging

import discord
from discord.ext import commands

import config
from utils import autocompletes, db


log = logging.getLogger("mainLog")


class SettingsSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = 300,
                         disable_on_timeout = True)

    @discord.ui.string_select(options = autocompletes.settings)
    async def select_option(self, select: discord.ui.Select, interaction: discord.Interaction) -> None:
        select.disabled = True
        select.placeholder = str(select.values[0])
        await interaction.message.edit(view = self)
        match select.values[0]:
            case "statistics":

                em = None
                view = None

                return await interaction.response.send_message(embed = em, view = view)
            case "volume":
                return await interaction.response.send_modal(VolumeModal())

            case _:
                return None


class VolumeModal(discord.ui.Modal):
    def __init__(self, title: str = "Volume"):
        self.title = title
        super().__init__(title = self.title)
        self.add_item(discord.ui.InputText(
            label = "Set the Volume",
            min_length = 1,
            max_length = 4,
            value = "25"
        ))

    async def callback(self, interaction: discord.Interaction):
        try:
            number = int(self.children[0].value)
        except ValueError:
            return await interaction.response.send_message("Please enter a valid number betweeen 1 and 1000")

        db_return = await db.insert_settings(setting_name = "volume", setting = number, guild = interaction.guild_id)
        if db_return is None:
            await interaction.response.send_message(f"Set the volume to {number}%")
        else:
            await interaction.response.send_message(f"Changed the volume from {db_return[0]}% to {number}%")


class Settings(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        log.debug("Started Settings Cog")

    @commands.slash_command(name="settings", description="set configs for the bot")
    async def settings(self, ctx: discord.ApplicationContext):
        em = discord.Embed(title = "Select what you want to edit", color = discord.Color.dark_gold())
        await ctx.response.send_message(embed = em, view = SettingsSelectView())


def setup(client):
    client.add_cog(Settings(client))
