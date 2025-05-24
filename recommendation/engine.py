from datetime import datetime
import pandas as pd

def recommend_post_times(logs_queryset):
    data = pd.DataFrame(list(logs_queryset.values('post_time', 'likes', 'comments')))
    if data.empty:
        return []
    data['hour'] = data['post_time'].dt.hour
    data['engagement'] = data['likes'] + data['comments']
    best_hours = (
        data.groupby('hour')['engagement']
        .mean()
        .sort_values(ascending=False)
        .head(3)
        .index.tolist()
    )
    return best_hours
