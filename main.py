import os
import discord
from discord.ext import commands
from groq import Groq
from github import Github
from flask import Flask
from threading import Thread

# ========== CONFIGURACIÓN ==========
GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'tu_groq_api_key_aqui')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', 'tu_github_token_aqui')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', 'tu_discord_token_aqui')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID', 'tu_channel_id_aqui')
REPO_NAME = os.getenv('REPO_NAME', 'RoyTheDog/code-assistant')

# ========== FLASK PARA MANTENER VIVO ==========
app = Flask(__name__)

@app.route('/')
def home():
    return " Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# ========== INICIALIZAR CLIENTES ==========
groq_client = Groq(api_key=GROQ_API_KEY)
github_client = Github(GITHUB_TOKEN)

# ========== BOT DE DISCORD ==========
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    try:
        channel = bot.get_channel(int(DISCORD_CHANNEL_ID))
        if channel:
            await channel.send("🚀 **Asistente de Código Online**\nEscribe `!ayuda` para ver comandos")
    except:
        print("️ No se pudo enviar mensaje de inicio")

@bot.command(name='ayuda')
async def ayuda(ctx):
    help_text = """
**📋 Comandos Disponibles:**
- `!analizar` - Analiza tu repositorio
- `!estado` - Verifica que todo funciona
- `!hola` - Prueba de conexión
    """
    await ctx.send(help_text)

@bot.command(name='hola')
async def hola(ctx):
    await ctx.send(f"¡Hola {ctx.author.name}! 👋 Todo funciona correctamente")

@bot.command(name='estado')
async def estado(ctx):
    status = "✅ Bot operativo\n"
    status += "✅ Conexión a Discord OK\n"
    status += "✅ Flask corriendo\n"
    status += f"✅ Groq: {'OK' if groq_client else 'ERROR'}\n"
    status += f"✅ GitHub: {'OK' if github_client else 'ERROR'}\n"
    await ctx.send(status)

@bot.command(name='analizar')
async def analizar(ctx):
    await ctx.send("🔍 Iniciando análisis del repositorio...")
    
    if not github_client or not groq_client:
        await ctx.send("❌ Error: Clientes no inicializados correctamente")
        return
    
    try:
        repo = github_client.get_repo(REPO_NAME)
        contents = repo.get_contents("")
        
        files_analyzed = 0
        
        for content in contents:
            if content.type == "file" and content.name.endswith(('.py', '.js', '.ts', '.java')):
                try:
                    file_content = content.decoded_content.decode('utf-8')
                    
                      prompt = f"Analiza este código en ESPAÑOL. Responde SOLO con: Score: X/10, Bugs: [lista], Mejoras: [lista]. Código: {file_content[:300]}"
                    
                    response = groq_client.chat.completions.create(
                        model="qwen/qwen3.6-27b",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2,
                        max_tokens=300
                    )
                    
                    analysis = response.choices[0].message.content
                    
                    if len(analysis) > 1900:
                        analysis = analysis[:1900] + "..."
                    
                    await ctx.send(f"**📄 {content.name}**\n{analysis}")
                    files_analyzed += 1
                    
                except Exception as e:
                    await ctx.send(f"⚠️ Error con {content.name}: {str(e)[:100]}")
        
        await ctx.send(f"✅ Análisis completo de {files_analyzed} archivos")
        
    except Exception as e:
        await ctx.send(f"❌ Error general: {str(e)[:200]}")

@bot.command(name='score')
async def score(ctx):
    """Muestra estadísticas del bot"""
    await ctx.send(f"📊 **Estadísticas:**\n- Servidores: {len(bot.guilds)}\n- Usuarios: {sum(g.member_count for g in bot.guilds)}")

@bot.command(name='ping')
async def ping(ctx):
    """Verifica la latencia del bot"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! {latency}ms")

# ========== INICIAR TODO ==========
if __name__ == "__main__":
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    print("✅ Flask iniciado en puerto 8080")
    
    print("🚀 Iniciando bot de Discord...")
    bot.run(DISCORD_TOKEN)
