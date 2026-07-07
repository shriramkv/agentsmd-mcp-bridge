"""Render the architecture diagram (navy/teal house style)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

NAVY="#1F3864"; TEAL="#2A9D8F"; LIGHT="#EAF3F1"; SAND="#F4EFE6"; GREY="#5B6B7B"
plt.rcParams.update({"font.family":"DejaVu Sans"})

fig, ax = plt.subplots(figsize=(9.2, 4.6)); ax.axis("off")
ax.set_xlim(0,10); ax.set_ylim(0,5)

def box(x,y,w,h,t,fc,ec=NAVY,tc=NAVY,fs=10,sub=None):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.03",fc=fc,ec=ec,lw=1.6))
    ax.text(x+w/2,y+h/2+(0.12 if sub else 0),t,ha="center",va="center",color=tc,fontsize=fs,fontweight="bold")
    if sub: ax.text(x+w/2,y+h/2-0.26,sub,ha="center",va="center",color=GREY,fontsize=8)
def arr(p1,p2,c=TEAL,lw=2):
    ax.add_patch(FancyArrowPatch(p1,p2,arrowstyle="-|>",mutation_scale=14,color=c,lw=lw,shrinkA=3,shrinkB=3))

ax.text(5,4.7,"agentsmd-mcp-bridge",ha="center",color=NAVY,fontsize=15,fontweight="bold")

box(0.3,2.9,2.2,1.1,"AGENTS.md",SAND,tc=NAVY,fs=12,sub="documented commands")
box(3.9,2.9,2.2,1.1,"Bridge",TEAL,ec=NAVY,tc="white",fs=13,sub="parse + extract + gen")
box(7.5,2.9,2.2,1.1,"MCP server",LIGHT,tc=NAVY,fs=12,sub="tools an agent calls")

arr((2.5,3.45),(3.9,3.45)); ax.text(3.2,3.68,"generate-mcp",ha="center",color=NAVY,fontsize=8)
arr((6.1,3.45),(7.5,3.45))

# reverse path
box(3.9,0.9,2.2,1.0,"Bridge (reverse)",LIGHT,ec=TEAL,tc=NAVY,fs=10,sub="manifest -> section")
arr((8.6,2.9),(6.1,1.7),c=GREY,lw=1.6); ax.text(7.7,2.15,"tools/list",color=GREY,fontsize=8)
arr((3.9,1.4),(1.4,2.9),c=GREY,lw=1.6); ax.text(2.2,2.05,"generate-agentsmd",color=GREY,fontsize=8)

ax.text(5,0.3,"Two AAIF standards, one bridge: AGENTS.md  \u2194  Model Context Protocol",
        ha="center",color=GREY,fontsize=9,style="italic")
plt.tight_layout(); plt.savefig("/home/claude/agentsmd-mcp-bridge/docs/architecture.png",dpi=160,bbox_inches="tight")
print("diagram written")
