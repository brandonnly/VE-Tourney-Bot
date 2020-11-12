import asyncio
import os
from message_generators import *
from discord.ext import commands
from embed_messages import *


intents = discord.Intents.default()
allowed_mentions = discord.AllowedMentions(everyone=False, users=True, roles=True)
bot = discord.ext.commands.Bot('ve!', intents=intents, description="Tournament Bot for Vaughan Esports",
                               case_insensitive=True, allowed_mentions=allowed_mentions)
BOT_TOKEN = os.getenv('BOT_TOKEN')


@bot.command()
async def veto(ctx, game, seriesLength, p2):
    """
    Starts a veto lobby with your opponent
    """
    if game == 'smash' and seriesLength == 'bo3':
        # player objects
        player1 = ctx.author
        player2 = await bot.fetch_user(p2[3:-1])

        # veto embed
        embed = discord.Embed(title="Smash Ultimate Best-of-3 Veto",
                              description=f"{player1.mention} vs {player2.mention}"
                                          f"\nThe rulebook can be found [here]({rulebook_url})",
                              color=discord.Color(0xffff00))

        # game 1 embed line
        embed.add_field(name="`                         Game 1                            `",
                        value="**Winner:** TBD", inline=False)
        embed.add_field(name="Starter Stages", value=starter_stages_message(), inline=True)
        embed.add_field(name="Counterpick Stages", value=counterpick_stages_message(), inline=True)

        # game 2 embed line
        embed.add_field(name="`                         Game 2                            `",
                        value="**Winner:** TBD", inline=False)
        embed.add_field(name="Starter Stages", value=starter_stages_message(), inline=True)
        embed.add_field(name="Counterpick Stages", value=counterpick_stages_message(), inline=True)

        # game 3 embed line
        embed.add_field(name="`                         Game 3                            `",
                        value="**Winner:** TBD", inline=False)
        embed.add_field(name="Starter Stages", value=starter_stages_message(), inline=True)
        embed.add_field(name="Counterpick Stages", value=counterpick_stages_message(), inline=True)
        embed.set_footer(icon_url=footer_icon, text=f"{tourney_name} | {footer_note}")

        main_msg = await ctx.send(embed=embed)

        try:

            # HIGHER SEED SELECTION
            await ctx.send("Player 1 (the higher seed) say `me`")

            # checks which user says me
            def playerCheck(message):
                return message.content.lower() == 'me' and message.channel == ctx.channel

            msg = await bot.wait_for('message', check=playerCheck, timeout=5)

            # changes player order if player 2 said they were first seed
            if msg.author == player2:
                player1 = player2
                player2 = ctx.author

            # notifies of veto starts
            await ctx.send(f"Starting veto with {player1.mention} as **Player 1** and {player2.mention} "
                           f"as **Player 2** in 5 seconds...")

            # delete all messages and begin veto after 5 seconds
            await asyncio.sleep(5)
            await ctx.channel.purge(after=main_msg)

            # setup removed stages
            removed_stages = []
            p1_dsr_stages = []
            p2_dsr_stages = []

            # stage check function
            def stageCheck(message):
                return message.content.title() in starter_stages and message.content.title() not in removed_stages \
                       and message.channel == ctx.channel

            # FIRST GAME VETO PROCESS
            # cross out all counterpick stages as they are not valid for first veto
            embed.set_field_at(2, name="Counterpick Stages",
                               value=counterpick_stages_message(counterpick_stages))
            await main_msg.edit(embed=embed)

            for x in range(4):
                # check which message to send
                if x == 0:
                    await ctx.send(f"{player1.mention} please veto a starter.")
                if x == 1:
                    await ctx.send(f"{player2.mention} please veto a starter.")
                if x == 2:
                    await ctx.send(f"{player2.mention} please veto another starter.")
                if x == 3:
                    await ctx.send(f"{player1.mention} please pick a map from the remaining starters.")

                # players message
                msg = await bot.wait_for('message', check=stageCheck, timeout=120)

                # remove messages sent after the embed
                await ctx.channel.purge(after=main_msg)

                # edit game 1 embed to remove the stage
                if x == 3:
                    embed.set_field_at(1, name="Starter Stages",
                                       value=starter_stages_message(removed_stages, msg.content.title()))
                else:
                    # add stage to removed list
                    removed_stages.append(msg.content.title())
                    embed.set_field_at(1, name="Starter Stages", value=starter_stages_message(removed_stages))

                # edit original message with new embed
                await main_msg.edit(embed=embed)

        # if the veto times out
        except asyncio.TimeoutError:
            # purge all messages after original message
            await ctx.channel.purge(after=main_msg)

            # create error embed and edit original message
            await timeout_error_message(main_msg)


bot.run(BOT_TOKEN)
