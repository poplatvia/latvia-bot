import nextcord
from nextcord.ext import commands
from utils.DFA import DFA
from checks import bot_channel_only
import os

class Automata(commands.Cog):
    def __init__(self, context):
        self.bot = context.client
        self.db = context.csdb
        self.config = context.config

    @nextcord.slash_command(name="dfa", description="Various dfa commands.")
    @bot_channel_only()
    async def dfa(self, ctx):
        pass

    @dfa.subcommand(name="init", description="Initialize the DFA.")
    async def init(self, ctx, alphabet: str):
        await ctx.response.defer()
        # convert to hashset then back to string to remove duplicates
        alphabet = "".join(set(alphabet))
        await self.db.add_dfa(ctx.user.id, alphabet)
        await ctx.followup.send(f"DFA initialized with alphabet: {alphabet}")

    @dfa.subcommand(name="add", description="Add states and transitions to the DFA.")
    async def add(self, ctx):
        pass

    @dfa.subcommand(name="get", description="Get the current DFA configuration.")
    async def get(self, ctx):
        pass

    @get.subcommand(name="alphabet", description="Get the DFA's alphabet.")
    async def get_alphabet(self, ctx):
        await ctx.response.defer()
        alphabet = await self.db.get_dfa_alphabet(ctx.user.id)
        if not alphabet:
            await ctx.followup.send("DFA not initialized. Please initialize the DFA using /dfa init <alphabet>.")
            return
        await ctx.followup.send(f"DFA Alphabet: {alphabet}")
    
    @get.subcommand(name="states", description="Get the DFA's states.")
    async def get_states(self, ctx):
        await ctx.response.defer()
        states = await self.db.get_dfa_states(ctx.user.id)
        if not states:
            await ctx.followup.send("No states found. Please add states using /dfa add state <state_id> <is_accepting>.")
            return
        states_str = "\n".join([f"State ID: {state['state_id']}, Accepting: {state['is_accepting']}" for state in states])
        await ctx.followup.send(f"DFA States:\n{states_str}")

    @get.subcommand(name="transitions", description="Get the DFA's transitions.")
    async def get_transitions(self, ctx):
        await ctx.response.defer()
        transitions = await self.db.get_dfa_transitions(ctx.user.id)
        if not transitions:
            await ctx.followup.send("No transitions found. Please add transitions using /dfa add transition <from_state> <input_symbol> <to_state>.")
            return
        transitions_str = "\n".join([f"{transition['from_state']} --{transition['input_symbol']}--> {transition['to_state']}" for transition in transitions])
        await ctx.followup.send(f"DFA Transitions:\n{transitions_str}")

    @add.subcommand(name="state", description="Add a state to the DFA.")
    async def add_state(self, ctx, state_id: int, is_accepting: bool=False):
        await ctx.response.defer()
        await self.db.add_state(ctx.user.id, state_id, is_accepting)
        await ctx.followup.send(f"State {state_id} added. Accepting: {is_accepting}")
    
    @add.subcommand(name="start", description="Set the start state of the DFA.")
    async def set_start(self, ctx, state_id: int):
        await ctx.response.defer()
        await self.db.set_start_state(ctx.user.id, state_id)
        await ctx.followup.send(f"Start state set to: {state_id}")

    @add.subcommand(name="transition", description="Add a transition to the DFA.")
    async def add_transition(self, ctx, from_state: int, input_symbol: str, to_state: int):
        await ctx.response.defer()
        await self.db.add_transition(ctx.user.id, from_state, input_symbol, to_state)
        await ctx.followup.send(f"Transition added: {from_state} --{input_symbol}--> {to_state}")
    
    async def __build_dfa_from_db(self, user_id) -> DFA:
        dfa: DFA = DFA()
        alphabet = await self.db.get_dfa_alphabet(user_id)
        if not alphabet:
            raise ValueError("Alphabet not set. Please initialize the DFA using /dfa init <alphabet>.")
        dfa.set_alphabet(alphabet)
        states = await self.db.get_dfa_states(user_id)
        if not states:
            raise ValueError("No states found. Please add states using /dfa add state <state_id> <is_accepting>.")
        for state in states:
            dfa.add_state(state['state_id'], state['is_accepting'])
        transitions = await self.db.get_dfa_transitions(user_id)
        for transition in transitions:
            dfa.add_transition(transition['from_state'], transition['input_symbol'], transition['to_state'])
        start_state = await self.db.get_dfa_start_state(user_id)
        dfa.set_start_state(start_state)
        if dfa.q0 is None:
            raise ValueError("Start state not set. Please set a start state using /dfa add start <state_id>.")
        return dfa


    @dfa.subcommand(name="accepts", description="Test if a string is accepted by the DFA.")
    async def accepts(self, ctx, string: str):
        await ctx.response.defer()
        # build dfa from db then check acceptance
        try:
            dfa: DFA = await self.__build_dfa_from_db(ctx.user.id)
        except ValueError as e:
            await ctx.followup.send(f"Error: {e}")
            return

        is_accepted = dfa.accepts(string)
        await ctx.followup.send(f"{'✅' if is_accepted else '❌'} String '{string}' is {'accepted' if is_accepted else 'not accepted'} by the DFA.")

    @dfa.subcommand(name="draw", description="Graphical representation of the DFA.")
    async def draw(self, ctx, title: str=""):
        await ctx.response.defer()
        # build dfa from db then draw
        try:
            dfa: DFA = await self.__build_dfa_from_db(ctx.user.id)
        except ValueError as e:
            await ctx.followup.send(f"Error: {e}")
            return

        dfa.draw(title=title, filename=f"dfa_{ctx.user.id}")
        await ctx.followup.send(file=nextcord.File(f"dfa_{ctx.user.id}.png"))
        # delete the file after sending
        os.remove(f"dfa_{ctx.user.id}.png")

    @dfa.subcommand(name="reset", description="Reset the DFA (delete all states and transitions).")
    async def reset(self, ctx):
        await ctx.response.defer()
        await self.db.reset_dfa(ctx.user.id)
        await ctx.followup.send("DFA reset.")

