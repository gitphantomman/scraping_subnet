from datetime import datetime
import storeWB
temp = [{'id': '16j7lrl', 'title': 'Cathy Freeman honoured with stand at Stadium Australia in Sydney Olympic Park', 'content': '', 'url': 'https://www.abc.net.au/news/2023-09-15/cathy-freeman-stand-at-sydney-olympic-park/102861452', 'created_utc': '2023-09-15T01:30:20', 'type': 'reddit'}, {'id': '16j7lri', 'title': 'a Community lets you own your Distribution, but more importantly it lets you build with your consumer.', 'content': '', 'url': 'https://www.reddit.com/r/salescommunity/comments/16j7lri/a_community_lets_you_own_your_distribution_but/', 'created_utc': '2023-09-15T01:30:19', 'type': 'reddit'}, {'id': '16j7lrb', 'title': 'Who has more rizz?', 'content': '', 'url': 'https://www.reddit.com/gallery/16j7lrb', 'created_utc': '2023-09-15T01:30:19', 'type': 'reddit'}, {'id': '16j7lra', 'title': 'Iron-clad friendship with Cambodia set to strengthen / Forging ahead into future with glory', 'content': '', 'url': 'https://www.chinadaily.com.cn/a/202309/15/WS6503fd8ea310d2dce4bb5f2d.html', 'created_utc': '2023-09-15T01:30:19', 'type': 'reddit'}, {'id': '16j7lr9', 'title': 'trading my sis for nl mega', 'content': '', 'url': 'https://www.reddit.com/r/jerkbuds12778/comments/16j7lr9/trading_my_sis_for_nl_mega/', 'created_utc': '2023-09-15T01:30:19', 'type': 'reddit'}]



def redditScore(response = temp):
    timeScore = 1
    total_time_diff = 0
    unique_score = 1
    exist_count = 0
    history = storeWB.returnLog()
    history_ids = []
    for item in history:
        history_ids.append(item['id'])
    if(response is not None):
        for post in response:
            given_time = datetime.fromisoformat(post['created_utc'])
            current_time = datetime.now()
            time_diff = (current_time - given_time).total_seconds()
            total_time_diff += time_diff
            if post['id'] in history_ids:
                exist_count += 1
        unique_score = exist_count / len(response)
        avg_time_diff = total_time_diff / len(response)
        if avg_time_diff < 864000 :
            timeScore = avg_time_diff / 864000
        else:
            timeScore = 1.0
        return 1 - 0.15 * timeScore - 0.5 * unique_score
    else:
        return 0