from accounts.models import UserInfo
from django.db import models
from django.contrib.auth.decorators import login_required

@login_required
def save_to_log(request, results):
    """
    Instantiate UserInfo and save/update according to queries searched by user
    """
    queries = UserInfo.objects.get(user = request.user)
    if not queries.search_history:
        queries.search_history = [results]
        queries.save()
    else:
        #
        if results in queries.search_history:
            queries.search_history.remove(results)
        if results[::-1] in queries.search_history:
            queries.search_history.remove(results[::-1])
        #
        if len(queries.search_history) >= 5:
            queries.search_history = queries.search_history[:-1]
        
        queries.search_history = [results] + queries.search_history
        queries.save()