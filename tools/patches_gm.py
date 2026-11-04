# -*- coding: utf-8 -*-
"""Apply human-approved Google Maps findings (gm/approved.json) to the shop list.
Only hours, the 'verified' line, the menu link and coordinates are touched;
prices are never changed automatically (platform prices differ from in-store)."""
import json, os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gm", "approved.json")


def apply(S):
    if not os.path.exists(P):
        return S
    A = json.load(open(P, encoding="utf-8"))
    for s in S:
        a = A.get(s["id"])
        if not a:
            continue
        if "hours" in a:
            s["slots"] = a["hours"]["slots"]
            s["hours"] = a["hours"]["text"]
        if "verified" in a:
            s["verified"] = a["verified"]
        if "menu_link" in a:
            s["menu_link"] = a["menu_link"]["url"]
            s["menu_link_label"] = a["menu_link"]["label"]
        if "ll" in a:
            s["ll"] = a["ll"]
    return S
