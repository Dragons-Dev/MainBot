import asyncio
import logging

import discord
from discord.ext import commands
import wavelink

import config
from utils import utility


log = logging.getLogger("mainLog")


class Music(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        log.debug("Started Music Cog")

    music = discord.SlashCommandGroup("music", "music commands", config.GUILDS)

    @music.command()
    async def play(
        self,
        ctx: discord.ApplicationContext,
        search: discord.Option(str, description="Song title to search"),
    ):
        def _check(reaction, user):
            if not user == ctx.author:
                return False
            match reaction.emoji:
                case "1️⃣":
                    return True
                case "2️⃣":
                    return True
                case "3️⃣":
                    return True
                case "4️⃣":
                    return True
                case "5️⃣":
                    return True

        await ctx.defer()

        vc = ctx.guild.voice_client  # define our voice client

        if not vc:  # check if the bot is not in a voice channel
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)  # connect to the voice channel

        if ctx.author.voice.channel.id != vc.channel.id:  # check if the bot is not in the voice channel
            return await ctx.response.send_message("You must be in the same voice channel as the bot.")

        await vc.self_deaf()

        songs = await wavelink.YouTubeTrack.search(query=search, return_first=False)
        tracks = []
        key = 0

        for song in songs:
            tracks.append(song)
            key += 1
            if key >= 5:
                break
        music_selection = discord.Embed(
            title="Select your title",
            description=(
                "\n".join(f"**{i + 1}.** {t.title}\n{utility.sec_to_min(t.length)}" for i, t in enumerate(tracks[:5]))
            ),
            color=discord.Color.blurple(),
        )
        music_selection.set_author(name="Query Results")

        try:
            msg = await ctx.channel.send(embed=music_selection)
            await msg.add_reaction("1️⃣")
            await msg.add_reaction("2️⃣")
            await msg.add_reaction("3️⃣")
            await msg.add_reaction("4️⃣")
            await msg.add_reaction("5️⃣")
            reaction, user = await self.client.wait_for("reaction_add", timeout=20.0, check=_check)
            match reaction.emoji:
                case "1️⃣":
                    track = 0
                case "2️⃣":
                    track = 1
                case "3️⃣":
                    track = 2
                case "4️⃣":
                    track = 3
                case "5️⃣":
                    track = 4
                case _:
                    track = 0
            song = await wavelink.YouTubeTrack.search(tracks[track].uri, return_first=True)
            await msg.delete(delay=3, reason="Song chosen")
        except asyncio.TimeoutError:
            return await ctx.response.send_message(
                embed=discord.Embed(title="Search cancelled timed out", color=discord.Color.brand_red())
            )

        await vc.set_volume(config.VOLUME)
        await vc.play(song)
        em = discord.Embed(
            title=f"Now playing {song.title}",
            url=song.uri,
            description=f"""
By: {song.author}
Duration: {utility.sec_to_min(song.duration)}
""",
            color=discord.Color.blurple(),
        )
        em.set_image(url=song.thumbnail)

        await ctx.followup.send(embed=em)

    @music.command(name="stop", description="stops the music backplay")
    async def stop(self, ctx: discord.ApplicationContext):
        vc = ctx.guild.voice_client
        if not vc:  # check if the bot is not in a voice channel
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)  # connect to the voice channel

        if ctx.author.voice.channel.id != vc.channel.id:  # check if the bot is not in the voice channel
            return await ctx.response.send_message("You must be in the same voice channel as the bot.")

        await vc.stop()
        await vc.disconnect(force=True)

    @music.command(name="volume", description="set the volume")
    async def set_volume(
        self,
        ctx: discord.ApplicationContext,
        volume: discord.Option(int, description="volume to set"),
    ):
        vc = ctx.guild.voice_client
        if not vc:  # check if the bot is not in a voice channel
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)  # connect to the voice channel

        if ctx.author.voice.channel.id != vc.channel.id:  # check if the bot is not in the voice channel
            return await ctx.response.send_message("You must be in the same voice channel as the bot.")

        await vc.set_volume(volume)


def setup(bot):
    bot.add_cog(Music(bot))
