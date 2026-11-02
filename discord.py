import os
import discord
from discord.ext import commands, tasks
import requests
from datetime import datetime, timedelta

TOKEN = os.environ["DISCORD_TOKEN"]  # set DISCORD_TOKEN before running the bot
API_URL = "https://ent.cesi.fr/api/seance/all"
CODE_PERSONNE = "2513459"  # Remplacez par le code personne approprié

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

def fetch_courses(start_date, end_date):
    params = {
        "start": start_date,
        "end": end_date,
        "codePersonne": CODE_PERSONNE,
        "_": "1731076854207"
    }
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    return []

def format_course(course):
    title = course.get("title", "Sans titre")
    start_time = course.get("start", "")
    end_time = course.get("end", "")
    salle = course.get("salles", [{"nomSalle": "Non spécifié"}])[0]["nomSalle"]
    professeur = course["intervenants"][0]["nom"] + " " + course["intervenants"][0]["prenom"]
    
    return f"**{title}**\n🕒 {start_time} - {end_time}\n📍 Salle : {salle}\n👨‍🏫 Professeur : {professeur}"

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")
    daily_schedule.start()

@tasks.loop(hours=24)
async def daily_schedule():
    channel = bot.get_channel(YOUR_CHANNEL_ID)  # Remplacez par l'ID de votre canal Discord
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    courses = fetch_courses(today.isoformat(), tomorrow.isoformat())
    if courses:
        await channel.send(f"**Emploi du temps pour {today.strftime('%d/%m/%Y')} :**")
        for course in courses:
            course_info = format_course(course)
            await channel.send(course_info)
    else:
        await channel.send(f"**{today.strftime('%d/%m/%Y')} : C'est une journée entreprise.**")

@bot.command(name="emploi")
async def emploi_du_temps(ctx, day_offset: int = 0):
    target_date = datetime.now().date() + timedelta(days=day_offset)
    end_date = target_date + timedelta(days=1)
    courses = fetch_courses(target_date.isoformat(), end_date.isoformat())
    if courses:
        await ctx.send(f"**Emploi du temps pour {target_date.strftime('%d/%m/%Y')} :**")
        for course in courses:
            course_info = format_course(course)
            await ctx.send(course_info)
    else:
        await ctx.send(f"**{target_date.strftime('%d/%m/%Y')} : C'est une journée entreprise.**")

bot.run(TOKEN)
