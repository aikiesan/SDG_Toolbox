from datetime import datetime

# Remove Babel dependency for now to simplify
babel_loaded = False  # Assume not using Babel for simplicity

def format_datetime(value, format='medium'):
    """Format a datetime object for display using strftime."""
    if value is None:
        return ""
    if isinstance(value, str):
        # Basic ISO format handling
        try:
            if value.endswith('Z'):
                value = value[:-1] + '+00:00'
            value = datetime.fromisoformat(value)
        except ValueError:
            try:  # Common DB format
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return value  # Return original if parsing fails
    elif not isinstance(value, datetime):
        return value

    # Define format strings directly
    if format == 'full':
        format_string = "%A, %d %B %Y at %I:%M:%S %p"  # Removed %Z as it can be problematic
    elif format == 'medium':
        format_string = "%b %d, %Y, %I:%M %p"
    elif format == 'short_date':
        format_string = "%m/%d/%y"  # Correct format codes for month/day/2-digit-year
    elif format == 'medium_date':
        format_string = "%b %d, %Y"
    else:  # Default to medium
        format_string = "%b %d, %Y, %I:%M %p"

        try:
            # Use locale-aware formatting if Babel is present
            return babel.dates.format_datetime(value, format_string)
        except Exception as e:
            # Fallback to strftime on Babel error
            print(f"Babel formatting failed ({e}), falling back to strftime.")
            pass # Fallthrough to strftime

    # Fallback to strftime
    try:
        return value.strftime(format_string)
    except ValueError:
        # Handle potential issues with format specifiers like %Z on some systems
        # Fallback to a very basic format if specific one fails
        return value.strftime('%Y-%m-%d %H:%M')


def format_date_filter(value):
    # Ensure this calls the main function correctly
    return format_datetime(value, format='medium_date')

def register_filters(app):
    app.jinja_env.filters['format_date'] = format_date_filter
    app.jinja_env.filters['format_datetime'] = format_datetime
