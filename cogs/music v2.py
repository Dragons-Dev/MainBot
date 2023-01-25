import asyncio
import logging
import datetime

import discord
from discord.ext import commands
import wavelink

import config
from utils import db, utility


log = logging.getLogger("mainLog")


async def play_or_queue(song, interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if not vc:
        vc = await interaction.user.voice.channel.connect(cls = wavelink.Player)
    em = discord.Embed(
        title = f"Now playing {song.title}",
        url = song.uri,
        description = f"""
    By: {song.author}
    Duration: {utility.sec_to_min(song.length)}
    """,
        color = discord.Color.blurple(),
    )
    em.set_image(url = song.thumbnail)
    if vc.is_playing():
        await vc.queue.put_wait(song)
    else:
        await vc.play(song)
    return em


async def edit_panel(song, vc: wavelink.Player):
    db_return = await db.get_setting(setting_name = "panel", guild_id = vc.guild.id)
    msg_id = db_return[0]
    panel_channel = vc.client.get_channel(1067457865746485288)
    panel = await panel_channel.fetch_message(msg_id)
    embed = discord.Embed(
        title = f"Now playing {song.title}",
        description = f"**By: {song.author}\nDuration: {utility.sec_to_min(song.length)}**",
        color = discord.Color.blurple(),
        timestamp = datetime.datetime.now(),
        url = song.uri
    )
    try:
        embed.set_image(url = song.thumbnail)
    except AttributeError:
        pass
    try:
        next_track = vc.queue.get()
        embed.add_field(name = "Next Track", value = f"[{next_track.title}]({next_track.uri})\n-> {next_track.author}\n-> {utility.sec_to_min(next_track.length)}")
        vc.queue.put_at_front(next_track)
    except wavelink.QueueEmpty:
        pass
    await panel.edit(content = None, embed = embed)


# noinspection PyTypeChecker
class SelectSongView(discord.ui.View):
    def __init__(self, songs: list[wavelink.abc.Playable]):
        self.songs = songs
        super().__init__(timeout = 300,
                         disable_on_timeout = True)

    @discord.ui.button(label = "Select first", style = discord.ButtonStyle.blurple, emoji = "1️⃣")
    async def first_song(self, button: discord.Button, interaction: discord.Interaction):
        song = self.songs[0]
        self.disable_all_items()
        button.style = discord.ButtonStyle.green
        await self.message.edit(view = self)
        await interaction.response.send_message(embed = await play_or_queue(song = song, interaction = interaction), delete_after = 5)
        self.stop()

    @discord.ui.button(label = "Select second", style = discord.ButtonStyle.blurple, emoji = "2️⃣")
    async def second_song(self, button: discord.Button, interaction: discord.Interaction):
        song = self.songs[1]
        self.disable_all_items()
        button.style = discord.ButtonStyle.green
        await self.message.edit(view = self)
        await interaction.response.send_message(embed = await play_or_queue(song = song, interaction = interaction), delete_after = 5)
        self.stop()

    @discord.ui.button(label = "Select third", style = discord.ButtonStyle.blurple, emoji = "3️⃣")
    async def third_song(self, button: discord.Button, interaction: discord.Interaction):
        song = self.songs[2]
        self.disable_all_items()
        button.style = discord.ButtonStyle.green
        await self.message.edit(view = self)
        await interaction.response.send_message(embed = await play_or_queue(song = song, interaction = interaction), delete_after = 5)
        self.stop()

    @discord.ui.button(label = "Select fourth", style = discord.ButtonStyle.blurple, emoji = "4️⃣")
    async def fourth_song(self, button: discord.Button, interaction: discord.Interaction):
        song = self.songs[3]
        self.disable_all_items()
        button.style = discord.ButtonStyle.green
        await self.message.edit(view = self)
        await interaction.response.send_message(embed = await play_or_queue(song = song, interaction = interaction), delete_after = 5)
        self.stop()

    @discord.ui.button(label = "Select fifth", style = discord.ButtonStyle.blurple, emoji = "5️⃣")
    async def fifth_song(self, button: discord.Button, interaction: discord.Interaction):
        song = self.songs[4]
        self.disable_all_items()
        button.style = discord.ButtonStyle.green
        await self.message.edit(view = self)
        await interaction.response.send_message(embed = await play_or_queue(song = song, interaction = interaction), delete_after = 5)
        self.stop()

class Music(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        log.debug("Started Music Cog")

    @commands.Cog.listener("on_wavelink_track_start")
    async def on_track_start(self, player: wavelink.Player, track: wavelink.Track):
        await edit_panel(song = track, vc = player)

    @commands.Cog.listener("on_wavelink_track_end")
    async def on_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        try:
            next_track = player.queue.get()
            await player.play(next_track)
        except wavelink.QueueEmpty:
            pass

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        if not message.channel.id == 1067457865746485288:
            return
        if message.author.bot:
            return
        vc = message.guild.voice_client  # define our voice client

        if not vc:  # check if the bot is not in a voice channel
            try:
                vc = await message.author.voice.channel.connect(cls = wavelink.Player)  # connect to the voice channel
            except AttributeError:
                await message.channel.send("You are not connected to any voice channel")
        if message.author.voice.channel.id != vc.channel.id:  # check if the bot is not in the voice channel
            return await message.channel.send("You must be in the same voice channel as the bot.")

        search = message.content.strip("<>")
        if search.startswith("https://open.spotify.com/track"):
            return await message.reply("Spotify is not supported for now.")
        elif search.startswith("https://open.spotify.com/playlist"):
            return await message.reply("Spotify is not supported for now.")
        elif search.startswith("https://www.youtube.com"):
            tracks = await wavelink.YouTubeTrack.search(search)
        elif search.startswith("https://soundcloud.com"):
            tracks = await wavelink.SoundCloudTrack.search(search)
        else:
            tracks = await wavelink.YouTubeTrack.search(search)

        music_selection = discord.Embed(
            title = "Select your title",
            description = (
                "\n".join(f"**{i + 1}.** [{t.title}]({t.uri})\n-> {t.author}\n-> {utility.sec_to_min(t.length)}" for i, t in enumerate(tracks[:5]))
            ),
            color = discord.Color.blurple(),
        )
        music_selection.set_author(name = "Query Results")
        await message.reply(embed = music_selection, view = SelectSongView(songs = tracks), delete_after = 20)
        await message.delete()

    @commands.command(name = "music_panel", description = "Summons the music panel")
    async def panel(self, ctx):
        msg = await ctx.send("this will be the music dashboard!")
        await db.insert_settings("panel", msg.id, guild = ctx.guild.id)


def setup(bot):
    bot.add_cog(Music(bot))
