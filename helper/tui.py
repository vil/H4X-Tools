"""
Copyright (c) 2023-2026. Vili and contributors.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from colorama import Back, Fore, Style

from helper import proxymanager
from tools.base import BaseTool


def run_menu(tools: tuple[BaseTool, ...], banner: str) -> str | None:
    """
    Display a full-screen interactive menu with arrow-key navigation.

    Only tools with ``menu_visible = True`` should be passed here; the
    Proxy Manager is accessed separately via the ``P`` shortcut.

    Controls
    --------
    ↑ / ↓      Navigate the tool list.
    Enter      Run the currently highlighted tool.
    0–9        Accumulate digits for a direct jump; the selection tracks
               live as you type.
    Backspace  Remove the last typed digit.
    Esc        Clear typed digits, or quit when nothing is typed.
    P          Open the Proxy Manager.
    ?          Open the help screen.
    q          Quit (only when no digits have been typed).
    Ctrl-C     Quit immediately.

    Parameters
    ----------
    tools:
        Ordered tuple of menu-visible tools.
    banner:
        Pre-rendered ANSI banner string shown at the top of the screen.

    Returns
    -------
    str | None
        ``"<n>"``   — 1-based index string of the chosen tool.
        ``"proxy"`` — user pressed P.
        ``"help"``  — user pressed ?.
        ``"quit"``  — user pressed q, Esc, or Ctrl-C.
        ``None``    — application exited unexpectedly.
    """
    from prompt_toolkit import Application
    from prompt_toolkit.formatted_text import ANSI as PT_ANSI
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import Layout
    from prompt_toolkit.layout.containers import HSplit, Window
    from prompt_toolkit.layout.controls import FormattedTextControl

    n = len(tools)
    sel: list[int] = [0]
    result: list[str | None] = [None]
    typed: list[str] = [""]  # digit accumulator for quick-jump

    # ── Content renderers ─────────────────────────────────────────────────

    def _banner() -> PT_ANSI:
        return PT_ANSI(banner + "\n")

    def _menu() -> PT_ANSI:
        COL_NAME = 22  # fixed name column width for the two-column layout

        lines = ""
        for row_start in range(0, n, 2):
            # Left column
            t1 = tools[row_start]
            lbl1 = str(row_start + 1).zfill(2)
            active1 = row_start == sel[0]
            arrow1 = ">" if active1 else " "
            if active1:
                left = (
                    f"  {Fore.BLACK}{Back.LIGHTGREEN_EX}"
                    f"{arrow1} [{lbl1}] {t1.name:<{COL_NAME}}"
                    f"{Style.RESET_ALL}"
                )
            else:
                left = (
                    f"  {arrow1} {Fore.LIGHTGREEN_EX}[{lbl1}]{Style.RESET_ALL}"
                    f" {t1.name:<{COL_NAME}}"
                )

            # Right column (absent when n is odd and this is the last row)
            right = ""
            if row_start + 1 < n:
                t2 = tools[row_start + 1]
                lbl2 = str(row_start + 2).zfill(2)
                active2 = (row_start + 1) == sel[0]
                arrow2 = ">" if active2 else " "
                if active2:
                    right = (
                        f"  {Fore.BLACK}{Back.LIGHTGREEN_EX}"
                        f"{arrow2} [{lbl2}] {t2.name:<{COL_NAME}}"
                        f"{Style.RESET_ALL}"
                    )
                else:
                    right = (
                        f"  {arrow2} {Fore.LIGHTGREEN_EX}[{lbl2}]{Style.RESET_ALL}"
                        f" {t2.name}"
                    )

            lines += left + right + "\n"

        # Description of the currently highlighted tool
        desc = tools[sel[0]].description
        if len(desc) > 74:
            desc = desc[:73] + "…"
        lines += f"\n  {Fore.LIGHTBLACK_EX}{desc}{Style.RESET_ALL}\n"

        # Proxy status indicator (compact, since full management is via P)
        if proxymanager.is_enabled():
            proxy_list = proxymanager.list_proxies()
            count = len(proxy_list)
            mode = "rotating" if proxymanager.is_rotating() else "fixed"
            if count:
                lines += (
                    f"  {Fore.LIGHTGREEN_EX}* Proxy{Style.RESET_ALL} "
                    f"{count} {'proxy' if count == 1 else 'proxies'} active ({mode})\n"
                )
            else:
                lines += (
                    f"  {Fore.LIGHTYELLOW_EX}● Proxy{Style.RESET_ALL}"
                    " routing enabled but no proxies configured\n"
                )

        # Live quick-jump echo
        if typed[0]:
            lines += (
                f"\n  {Fore.LIGHTYELLOW_EX}Jump to: "
                f"{typed[0]}\u2581{Style.RESET_ALL}"  # ▁ acts as a block cursor
            )

        return PT_ANSI(lines)

    def _status() -> PT_ANSI:
        return PT_ANSI(
            f"\n  {Fore.LIGHTBLACK_EX}"
            "↑↓ Navigate   Enter Select   0–9 Jump   "
            "P Proxy Manager   ? Help   q Quit"
            f"{Style.RESET_ALL}\n"
        )

    # ── Key bindings ──────────────────────────────────────────────────────

    kb = KeyBindings()

    @kb.add("up")
    def _up(event):
        typed[0] = ""
        sel[0] = (sel[0] - 1) % n

    @kb.add("down")
    def _down(event):
        typed[0] = ""
        sel[0] = (sel[0] + 1) % n

    @kb.add("enter")
    def _enter(event):
        if typed[0]:
            idx = int(typed[0]) - 1
            if 0 <= idx < n:
                result[0] = typed[0]
                event.app.exit()
                return
            # Out of range — clear and stay
            typed[0] = ""
        else:
            result[0] = str(sel[0] + 1)
            event.app.exit()

    @kb.add("q")
    def _quit_key(event):
        if typed[0]:
            # 'q' cancels the digit accumulation
            typed[0] = ""
        else:
            result[0] = "quit"
            event.app.exit()

    @kb.add("escape")
    def _escape(event):
        if typed[0]:
            typed[0] = ""
        else:
            result[0] = "quit"
            event.app.exit()

    @kb.add("c-c")
    def _ctrl_c(event):
        result[0] = "quit"
        event.app.exit()

    @kb.add("?")
    def _help_key(event):
        if not typed[0]:
            result[0] = "help"
            event.app.exit()

    @kb.add("p")
    @kb.add("P")
    def _proxy_key(event):
        # Only fire when not mid-way through a number sequence
        if not typed[0]:
            result[0] = "proxy"
            event.app.exit()

    @kb.add("backspace")
    def _backspace(event):
        if typed[0]:
            typed[0] = typed[0][:-1]
            if typed[0]:
                idx = int(typed[0]) - 1
                if 0 <= idx < n:
                    sel[0] = idx

    # Digit keys — accumulate and update the selection live
    for _d in "0123456789":

        @kb.add(_d)
        def _digit(event, d=_d):
            candidate = typed[0] + d
            try:
                idx = int(candidate) - 1
            except ValueError:
                return

            if 0 <= idx < n:
                typed[0] = candidate
                sel[0] = idx
            elif candidate == "0":
                pass  # ignore bare zero
            else:
                # Combined number out of range — restart with this digit alone
                try:
                    idx2 = int(d) - 1
                    if 0 <= idx2 < n:
                        typed[0] = d
                        sel[0] = idx2
                    else:
                        typed[0] = ""
                except ValueError:
                    typed[0] = ""

    # ── Layout ────────────────────────────────────────────────────────────

    layout = Layout(
        HSplit(
            [
                Window(
                    content=FormattedTextControl(_banner),
                    dont_extend_height=True,
                    always_hide_cursor=True,
                ),
                Window(
                    content=FormattedTextControl(_menu),
                    always_hide_cursor=True,
                ),
                Window(
                    content=FormattedTextControl(_status),
                    dont_extend_height=True,
                    always_hide_cursor=True,
                ),
            ]
        )
    )

    app = Application(
        layout=layout,
        key_bindings=kb,
        full_screen=True,
        mouse_support=False,
    )
    app.run()

    return result[0]
