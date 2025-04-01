# Telegram Persian Calendar Picker

A Telegram bot component for Persian (Jalali) calendar date selection, featuring holiday indicators and month navigation.

<img src="assets/demo.gif?raw=true" alt="Demo GIF" width="500" />


## Overview

This component provides an inline keyboard calendar for Telegram bots with:
- Persian calendar system (Jalali)
- Holiday indicators (🔴)
- Month navigation
- Today's date display

## Installation

1. Required packages:

```bash
pip install python-telegram-bot>=20.0 persiantools
```

2. Project files:
```
your_project/
├── persian_date_picker.py    # Main component
└── persian_holidays.json     # Holiday definitions
```

## Quick Start

```python
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from persian_date_picker import PersianDatePicker

# Initialize the date picker
date_picker = PersianDatePicker(callback_pattern="mycalendar")

# Command handler
async def calendar_command(update, context):
    await date_picker.show_calendar(update.message)

# Callback handler
async def button_handler(update, context):
    selected_date = await date_picker.process_selection(update.callback_query)
    if selected_date:
        await update.callback_query.message.reply_text(
            f"تاریخ انتخاب شده: {selected_date}"
        )

# Add to your bot
app = Application.builder().token("YOUR_BOT_TOKEN").build()
app.add_handler(CommandHandler("date", calendar_command))
app.add_handler(CallbackQueryHandler(button_handler))
```

## Holiday Configuration

Define holidays in `persian_holidays.json`:
```json
{
    "1404/1/1": "نوروز",
    "1404/1/2": "نوروز",
    "1404/1/13": "روز طبیعت"
}
```

## Features

- 📅 Full Persian calendar implementation
- 🔴 Holiday indicators (Fridays and special dates)
- ⬅️ Month navigation buttons
- 📍 Today's date display
- 🎯 Customizable callback pattern
- 🔄 Automatic holiday handling

## Component API

### Initialization
```python
date_picker = PersianDatePicker(callback_pattern="your_pattern")
```

### Methods
- `show_calendar(message, year=None, month=None)`: Display the calendar
- `process_selection(query)`: Handle user interactions
- `create_calendar(year=None, month=None)`: Generate calendar markup

### Return Format
Selected dates are returned as strings: `"YYYY/MM/DD"`

## Notes

- Requires Python 3.7+
- Built for python-telegram-bot version 20.0 or higher
- Automatically marks Fridays as holidays
- Uses RTL text formatting for Persian language
- Includes built-in error handling

## License

MIT License
