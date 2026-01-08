"""Reusable UI components like Cards."""
import customtkinter as ctk
from utils.constants import *

def create_info_card(parent, title: str, value: str, color: str, icon: str = "•") -> ctk.CTkFrame:
    """Creates a stylized info card for the dashboard."""
    frame = ctk.CTkFrame(parent, fg_color=COLOR_CARD_BG, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
    
    content_frame = ctk.CTkFrame(frame, fg_color="transparent")
    content_frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    header_frame.pack(fill="x")
    
    icon_label = ctk.CTkLabel(header_frame, text=icon, font=(FONT_FAMILY, 20), text_color=color)
    icon_label.pack(side="left", padx=(0, 10))
    
    title_label = ctk.CTkLabel(header_frame, text=title.upper(), font=(FONT_FAMILY, 12, "bold"), text_color="#555555")
    title_label.pack(side="left")
    
    value_label = ctk.CTkLabel(content_frame, text=value, font=FONT_VALUE_BIG, text_color=color)
    value_label.pack(anchor="w", pady=(15, 0))
    
    return frame
