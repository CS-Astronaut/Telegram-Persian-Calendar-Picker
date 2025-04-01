from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from persiantools.jdatetime import JalaliDate
from typing import Dict, Callable
import json
import os

class PersianDatePicker:
    """
    A Persian (Jalali) date picker component for Telegram bots.
    
    This class provides a calendar-style date picker that:
    - Shows Persian calendar months
    - Marks holidays and Fridays
    - Supports navigation between months
    - Returns selected dates in YYYY/MM/DD format
    
    Example Usage:
    -------------
    # In your bot's initialization:
    date_picker = PersianDatePicker(callback_pattern="my_calendar")
    
    # In your command handler:
    async def calendar_command(update, context):
        await date_picker.show_calendar(update.message)
    
    # In your callback query handler:
    async def callback_handler(update, context):
        result = await date_picker.process_selection(update.callback_query)
        if result:
            # result will be a string in format: YYYY/MM/DD
            await update.callback_query.message.reply_text(f"Selected date: {result}")
    
    Attributes:
    ----------
    callback_pattern : str
        Prefix for callback data to identify this component's callbacks
    holidays : dict
        Dictionary of holiday dates and their descriptions
    weekdays : list
        List of Persian weekday names
    """
    
    def __init__(self, callback_pattern: str = "calendar"):
        """
        Initialize the date picker.
        
        Args:
            callback_pattern (str): Prefix for callback data to identify this component's callbacks
        """
        self.callback_pattern = callback_pattern
        self.weekdays = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج']
        self.holidays = self._load_holidays()
        
    def _load_holidays(self) -> Dict[str, str]:
        """Load holidays from JSON file or return empty dict if file not found."""
        try:
            json_path = os.path.join(os.path.dirname(__file__), 'persian_holidays.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load holidays file: {e}")
            return {}

    def _get_persian_month_name(self, month: int) -> str:
        """Get Persian month name."""
        months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
        return months[month - 1]

    def _is_holiday(self, date: JalaliDate) -> bool:
        """Check if given date is a holiday."""
        date_str = f"{date.year}/{date.month}/{date.day}"
        return date_str in self.holidays or (date.to_gregorian().weekday() == 4)

    def create_calendar(self, year: int = None, month: int = None) -> InlineKeyboardMarkup:
        """
        Create a calendar keyboard for the specified year and month.
        
        Args:
            year (int, optional): Year in Jalali calendar
            month (int, optional): Month number (1-12)
            
        Returns:
            InlineKeyboardMarkup: Telegram keyboard markup for the calendar
        """
        if not year or not month:
            today = JalaliDate.today()
            year = today.year
            month = today.month

        keyboard = []
        
        # Add header row (month/year and navigation buttons)
        month_year = f"{self._get_persian_month_name(month)} {year}"
        keyboard.append([
            InlineKeyboardButton("←", callback_data=f"{self.callback_pattern}_prev_{year}_{month}"),
            InlineKeyboardButton(month_year, callback_data="ignore"),
            InlineKeyboardButton("→", callback_data=f"{self.callback_pattern}_next_{year}_{month}")
        ])
        
        # Add weekday headers
        keyboard.append([InlineKeyboardButton(x, callback_data="ignore") for x in self.weekdays])
        
        # Calculate calendar days
        first_day = JalaliDate(year, month, 1)
        start_weekday = (first_day.to_gregorian().weekday() + 2) % 7
        
        if month <= 6:
            days_in_month = 31
        elif month <= 11:
            days_in_month = 30
        else:
            days_in_month = 29 if not JalaliDate.is_leap(year) else 30

        # Add blank cells for first row
        current_row = []
        for _ in range(start_weekday):
            current_row.append(InlineKeyboardButton(" ", callback_data="ignore"))
        
        # Add days
        for day in range(1, days_in_month + 1):
            date = JalaliDate(year, month, day)
            is_holiday = self._is_holiday(date)
            display_text = f"🔴{day}" if is_holiday else str(day)
            
            current_row.append(InlineKeyboardButton(
                display_text,
                callback_data=f"{self.callback_pattern}_day_{year}_{month}_{day}"
            ))
            
            if len(current_row) == 7:
                keyboard.append(current_row)
                current_row = []
        
        # Add remaining blank cells
        if current_row:
            while len(current_row) < 7:
                current_row.append(InlineKeyboardButton(" ", callback_data="ignore"))
            keyboard.append(current_row)
        
        return InlineKeyboardMarkup(keyboard)

    async def show_calendar(self, message, year=None, month=None):
        """
        Show the calendar in response to a message.
        
        Args:
            message: Telegram message object
            year (int, optional): Year to display
            month (int, optional): Month to display
        """
        today = JalaliDate.today()
        today_str = f"امروز: {today.day} {self._get_persian_month_name(today.month)} {today.year}"
        await message.reply_text(
            f"لطفاً تاریخ مورد نظر را انتخاب کنید:\n{today_str}",
            reply_markup=self.create_calendar(year, month)
        )

    async def process_selection(self, query) -> str:
        """
        Process calendar callback queries.
        
        Args:
            query: Telegram callback query object
            
        Returns:
            str: Selected date in format 'YYYY/MM/DD' or None if no date was selected
        """
        await query.answer()
        callback_data = query.data
        
        if not callback_data.startswith(self.callback_pattern):
            return None
            
        action = callback_data.split('_')[1]
        
        if action == "ignore" or not action:
            return None
            
        elif action in ["prev", "next"]:
            year, month = map(int, callback_data.split('_')[2:])
            if action == "prev":
                month -= 1
                if month < 1:
                    month = 12
                    year -= 1
            else:
                month += 1
                if month > 12:
                    month = 1
                    year += 1
                    
            await query.edit_message_reply_markup(
                reply_markup=self.create_calendar(year, month)
            )
            return None
            
        elif action == "day":
            year, month, day = map(int, callback_data.split('_')[2:])
            return f"{year}/{month}/{day}" 