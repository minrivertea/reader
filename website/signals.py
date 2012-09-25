import django.dispatch

word_searched = django.dispatch.Signal(providing_args=["chars", "time", "user_id"])




