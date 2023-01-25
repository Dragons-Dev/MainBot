def sec_to_min(time: float):
    time = round(time)
    hours, seconds = divmod(time, 60 * 60)
    minutes, seconds = divmod(seconds, 60)
    if not hours:
        return f"{minutes}m {str(seconds).zfill(2)}s"
    return f"{hours}h {minutes}m {str(seconds).zfill(2)}s"
