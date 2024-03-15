import os
import openai
import discord
from discord import app_commands

openai_client = openai.Client(api_key=os.environ['OPENAI_API_KEY'])
discord_client = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(discord_client)

global last_message
last_message = ""


async def send_voice(interaction, text):
    if not interaction.guild.voice_client:
        voice_channel = interaction.user.voice.channel
        if not voice_channel:
            await interaction.response.send_message("You need to be in a voice channel to use this command.", ephemeral=True)
            return

        await voice_channel.connect()

    await interaction.response.send_message(f"{text}", ephemeral=True)

    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text)

    response.write_to_file("speech.mp3")
    interaction.guild.voice_client.play(discord.FFmpegPCMAudio("speech.mp3"))


async def send_sound_effect(interaction, name):
    if not interaction.guild.voice_client:
        voice_channel = interaction.user.voice.channel
        if not voice_channel:
            await interaction.response.send_message("You need to be in a voice channel to use this command.", ephemeral=True)
            return

        await voice_channel.connect()

    sound_file = f"./soundboard/{name}.mp3"
    if not os.path.exists(sound_file):
        await interaction.response.send_message("Sound file not found.", ephemeral=True)
        return

    await interaction.response.send_message(f"Playing {name}", ephemeral=True)
    interaction.guild.voice_client.play(discord.FFmpegPCMAudio(sound_file))


@tree.command(name="say", description="Synthesizes speech directly to a voice channel.")
async def say(interaction, text: str):
    global last_message
    last_message = text
    await send_voice(interaction, text)


@tree.command(name="repeat", description="Repeats last spoken message.")
async def repeat(interaction):
    if last_message == "":
        await interaction.response.send_message("There is no message to repeat.", ephemeral=True)
        return

    await send_voice(interaction, last_message)


@tree.command(name="play", description="Plays a sound effect from the soundboard.")
async def bruh(interaction, name: str):
    await send_sound_effect(interaction, name)


@discord_client.event
async def on_ready():
    await tree.sync()

discord_client.run(os.environ['NATIVE_SPEAKER_BOT_TOKEN'])
