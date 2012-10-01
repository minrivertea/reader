import django.dispatch

word_searched = django.dispatch.Signal(providing_args=["chars", "time", "user_id"])
article_saved = django.dispatch.Signal(providing_args=["article_id", "time", "user_id"])




