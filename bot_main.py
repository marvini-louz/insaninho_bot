import discord
from discord.ext import commands

# -------- CONFIGURAÇÃO BÁSICA --------
intents = discord.Intents.default()
intents.message_content = True  # Permite ler mensagens
intents.reactions = True  # Permite ler reações
intents.guilds = True  # Permite gerenciar servidores
intents.members = True  # Permite gerenciar cargos em membros

bot = commands.Bot(command_prefix="!", intents=intents)

# Dicionário para armazenar os reaction roles
# Estrutura: { message_id: { "emoji": role_id, "emoji2": role_id2, ... } }
reaction_roles = {}

# -------- EVENTO QUANDO O BOT LIGA --------
@bot.event
async def on_ready():
    print(f"Bot {bot.user} está online.")

    for message_id, mapa in reaction_roles.items():
        canal = bot.get_channel(1407066934759129128)  # substitua pelo canal correto
        message = await canal.fetch_message(message_id)
        for reaction in message.reactions:
            if str(reaction.emoji) in mapa:
                role_id = mapa[str(reaction.emoji)]
                role = message.guild.get_role(role_id)
                users = await reaction.users().flatten()
                for user in users:
                    if not user.bot:
                        member = message.guild.get_member(user.id)
                        if member:
                            await member.add_roles(role)

# -------- COMANDO PARA CRIAR REACTION ROLE --------
@bot.command()
@commands.has_permissions(administrator=True)
async def reactionrole(ctx, *, conteudo: str):

    # Quebra o conteúdo em linhas
    linhas = conteudo.split("\n")

    # Primeira linha = texto da mensagem
    mensagem_texto = linhas[0]

    # Cria a mensagem no canal
    msg = await ctx.send(mensagem_texto)

    # Cria um dicionário temporário para mapear emoji->cargo
    mapa = {}

    # Lê cada linha seguinte (emoji + cargo)
    for linha in linhas[1:]:
        partes = linha.strip().split()
        if len(partes) >= 2:
            emoji = partes[0]  # Exemplo: 🔴
            role = await commands.RoleConverter().convert(ctx, partes[1])  # Converte @Cargo
            mapa[emoji] = role.id
            await msg.add_reaction(emoji)  # Bot adiciona a reação na mensagem

    # Salva no dicionário global para que o bot saiba o que fazer
    reaction_roles[msg.id] = mapa


# -------- EVENTO QUANDO UM USUÁRIO REAGE --------
@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    if payload.message_id in reaction_roles:
        role_id = reaction_roles[payload.message_id].get(str(payload.emoji))
        if role_id:
            guild = bot.get_guild(payload.guild_id)
            role = guild.get_role(role_id)
            member = guild.get_member(payload.user_id)
            if role and member:
                await member.add_roles(role)


# -------- EVENTO QUANDO UM USUÁRIO REMOVE REAÇÃO --------
@bot.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == bot.user.id:
        return
    if payload.message_id in reaction_roles:
        role_id = reaction_roles[payload.message_id].get(str(payload.emoji))
        if role_id:
            guild = bot.get_guild(payload.guild_id)
            role = guild.get_role(role_id)
            member = guild.get_member(payload.user_id)
            if role and member:
                await member.remove_roles(role)


# -------- RODAR O BOT --------
bot.run("NDg2NjIxNjE4ODQ4OTIzNjY5.GEi3AY.1mHCjj5zYqIPVsXbmB3NbMDW1dN6fRskYYTIk8")
