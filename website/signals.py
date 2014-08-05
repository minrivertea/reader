import django.dispatch

word_searched = django.dispatch.Signal(providing_args=["word", "time", "user_id"])
word_viewed = django.dispatch.Signal(providing_args=["word", "time", "user_id"])






