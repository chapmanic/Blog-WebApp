from datetime import date, datetime


def calculate_time_difference(posted_time):
    current_time = datetime.now()
    time_difference = current_time - posted_time

    # Extract days, hours, and minutes
    days = time_difference.days

    # the divmod divide the time_difference.seconds by 3600 and then save the answer as a tuple, with the whole number and remainder,
    # as hours and remainder(minutes) respectively. the same as the second tuple, only that the remainder( _ ) which is the seconds is not needed.
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if days > 0:
        if days < 10:
            return f"{days} days ago"
        else:
            # This return Month, day and year if over 10days old
            time_posted = posted_time.strftime("%B %d, %Y")
            return f"{time_posted}"
    elif hours > 0:
        return f"{hours} hours ago"
    elif minutes > 0:
        return f"{minutes} minutes ago"
    else:
        return "just now"
