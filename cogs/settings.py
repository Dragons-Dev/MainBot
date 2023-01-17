import logging

import discord
from discord.ext import commands

import config
from utils import autocompletes, db


log = logging.getLogger("mainLog")


volume_options = [discord.SelectOption(label = "10"),
                  discord.SelectOption(label = "20"),
                  discord.SelectOption(label = "30"),
                  discord.SelectOption(label = "40"),
                  discord.SelectOption(label = "50"),
                  discord.SelectOption(label = "60"),
                  discord.SelectOption(label = "70"),
                  discord.SelectOption(label = "80"),
                  discord.SelectOption(label = "90"),
                  discord.SelectOption(label = "100")]


class SettingsView(discord.ui.View):
    def __init__(self, setting):
        self.setting = setting
        super().__init__(timeout = 300,
                         disable_on_timeout = True)

    async def smart(self):
        match self.setting:
            case "statistics":
                @discord.ui.channel_select(channel_types = [discord.ChannelType.text])
                async def channel_select(self, select: discord.ui.Select, interaction: discord.Interaction) -> None:
                    old_value = await db.insert_settings(setting_name = "statistics", setting = select.values[0].id, guild = interaction.guild_id)
                    if old_value is None:
                        em = discord.Embed(title = "Success", description = f"Set channel to <#{select.values}>", color = discord.Color.brand_green())
                    else:
                        em = discord.Embed(title = "Success", description = f"Updated channel from <#{old_value}> to {select.values}", color = discord.Color.brand_green())
                    await interaction.response.send_message(embed = em)
                    return
            case "volume":
                @discord.ui.string_select(options = volume_options)
                async def channel_select(self, select: discord.ui.Select, interaction: discord.Interaction) -> None:
                    old_value = await db.insert_settings(setting_name = "volume", setting = select.values, guild = interaction.guild_id)
                    await interaction.response.send_message(embed = )
                return

class Settings(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        log.debug("Started Settings Cog")

    @commands.slash_command(name="settings", description="set configs for the bot")
    async def settings(
        self,
        ctx: discord.ApplicationContext,
        setting: discord.Option(
            input_type=discord.SlashCommandOptionType.string,
            name="setting",
            description="wich setting are you editing",
            autocomplete=autocompletes.settings,
            required=True,
        ),
    ):
        return await ctx.response.send_message("hi", view = SettingsView())


def setup(client):
    client.add_cog(Settings(client))
