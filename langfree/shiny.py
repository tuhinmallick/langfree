# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_shiny.ipynb.

# %% auto 0
__all__ = ['render_input_chat', 'render_funcs', 'render_llm_output', 'invoke_later']

# %% ../nbs/04_shiny.ipynb 3
import os, json
from pprint import pformat
from .transform import RunData
from shiny import module, ui, render, reactive
import shiny.experimental as x
import asyncio

# %% ../nbs/04_shiny.ipynb 5
def _get_role(m):
    role = m['role'].upper()
    if 'function_call' in m: return f"{role} - Function Call"
    return 'FUNCTION RESULTS' if role == 'FUNCTION' else role

def _get_content(m):
    if 'function_call' not in m:
        return m['content']
    func = m['function_call']
    return f"{func['name']}({func['arguments']})"

def render_input_chat(run:RunData, markdown=True):
    "Render the chat history, except for the last output as a group of cards."
    cards = []
    num_inputs = len(run.inputs)
    for i,m in enumerate(run.inputs):
        content = str(_get_content(m))
        if _get_role(m) == 'FUNCTION RESULTS':
            try: content = '```json\n' + pformat(json.loads(content)) + '\n```'
            except: pass
        cards.append(
            x.ui.card(
                x.ui.card_header(ui.div({"style": "display: flex; justify-content: space-between;"},
                                    ui.span(
                                        {"style": "font-weight: bold;"}, 
                                        _get_role(m),
                                    ),
                                    ui.span(f'({i+1}/{num_inputs})'),
                                )       
                ),
                x.ui.card_body(ui.markdown(content) if markdown else content),
                class_= "card border-dark mb-3"
            )
        )
    return ui.div(*cards)

# %% ../nbs/04_shiny.ipynb 17
def render_funcs(run:RunData, markdown=True):
    "Render functions as a group of cards."
    cards = []
    if run.funcs:
        num_inputs = len(run.funcs)
        for i,m in enumerate(run.funcs):
            nm = m.get('name', '')
            desc = m.get('description', '')
            content = json.dumps(m.get('parameters', ''), indent=4)
            cards.append(
                x.ui.card(
                    x.ui.card_header(ui.div({"style": "display: flex; justify-content: space-between;"},
                                        ui.span(
                                            {"style": "font-weight: bold;"}, 
                                            nm,
                                        ),
                                        ui.span(f'({i+1}/{num_inputs})'),
                                    )       
                    ),
                    x.ui.card_body(
                        ui.strong(f'Description: {desc}'),
                        ui.markdown(content) if markdown else content
                    ),
                    class_= "card border-dark mb-3"
                )
            )
    return ui.div(*cards)

# %% ../nbs/04_shiny.ipynb 24
def render_llm_output(run, width="100%", height="250px"):
    "Render the LLM output as an editable text box."
    o = run.output
    return ui.input_text_area('llm_output', label=ui.h3('LLM Output (Editable)'), 
                              value=o['content'], width=width, height=height)

# %% ../nbs/04_shiny.ipynb 28
def invoke_later(delaySecs:int, callback:callable):
    "Execute code in a shiny app with a time delay of `delaySecs` asynchronously."
    async def delay_task():
        await asyncio.sleep(delaySecs)
        async with reactive.lock():
            callback()
            await reactive.flush()
    asyncio.create_task(delay_task())
