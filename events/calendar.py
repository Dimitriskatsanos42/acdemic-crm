from calendar import HTMLCalendar
from datetime import date

class BootstrapHTMLCalendar(HTMLCalendar):
    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="bg-light p-1" style="width: 40px; height: 40px;"></td>'  # Empty cell with reduced size
        
        today = date.today()
        is_today = day == today.day and self.current_month == today.month and self.current_year == today.year

        # CSS classes for styling
        css_class = 'bg-primary text-white' if is_today else 'bg-light'
        text_colour = 'text-white' if is_today else 'text-dark'
        
        # Entire cell clickable
        return f'''
            <td class="{css_class} p-1" style="width: 40px; height: 40px;">
                <a href="/events/calendar/{self.current_year}/{self.current_month}/{day}/" 
                   class="text-decoration-none {text_colour} d-block w-100 h-100 text-center">
                    {day}
                </a>
            </td>
        '''

    def formatmonth(self, theyear, themonth, withyear=True):
        """Return a month's calendar table with Bootstrap classes."""
        # Track current year and month
        self.current_year = theyear
        self.current_month = themonth

        # Generate the default calendar table
        table = super().formatmonth(theyear, themonth, withyear)

        # Process the table for Bootstrap compatibility
        table_rows = table.split('\n')
        table_without_header = '\n'.join(row for i, row in enumerate(table_rows) if i != 1)  # Remove month/year header

        # Replace default table classes with Bootstrap classes
        table_without_header = table_without_header.replace(
            '<table border="0" cellpadding="0" cellspacing="0" class="month">',
            '<table class="table table-bordered table-hover text-center table-sm" style="table-layout: fixed; width: 100%;">'
        )
        
        # Adjust weekday headers for compactness
        table_without_header = table_without_header.replace(
            '<tr><th colspan="7" class="month">',
            '<tr class="bg-secondary text-white small">'
        )
        
        return table_without_header