import praw
import csv
import pandas as pd
from tqdm import tqdm
from praw.models import Submission
from datetime import datetime, timezone

def get_reddit_data(subreddits, keywords, limit, csv_file_path, start_date, end_date):
    REDDIT_ID ="doVr0Tzy7XzxNX49V6WEBA"
    REDDIT_SECRET = "meyYVEetTi32wnbgKs8FNiKwgjDA-Q"
    USER_AGENT = "visual_analytics_groupproject"
    USERNAME = "Great-Oil5596"
    PASSWORD = "G2QxAiqNTMq$84n"

    reddit = praw.Reddit(
        client_id=REDDIT_ID,
        client_secret=REDDIT_SECRET,
        user_agent=USER_AGENT,
        username=USERNAME,
        password=PASSWORD
    )

    all_results = []

    start_date = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end_date = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    for sub in tqdm(subreddits):
        subreddit = reddit.subreddit(sub)
        for keyword in keywords:
            results = []
            selected_threads = subreddit.search(keyword, limit=limit)

            for post in selected_threads:
                post_date = datetime.fromtimestamp(post.created_utc, timezone.utc)
                if start_date <= post_date <= end_date:
                    data = {
                        'author_name': post.author.name if post.author else 'No author',
                        'post_id': post.id,
                        'title': post.title,
                        'body': post.selftext,
                        'post_date': post_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'keyword': keyword,
                    }

                    post.comments.replace_more(limit=None)
                    comments = post.comments.list()

                    for comment in comments:
                        comment_created_utc = datetime.fromtimestamp(comment.created_utc, timezone.utc)
                        if start_date <= comment_created_utc <= end_date and keyword.lower() in comment.body.lower():
                            comment_data = {
                                'comment_author_name': comment.author.name if comment.author else 'No author',
                                'comment_id': comment.id,
                                'comment_parent_id': comment.parent_id,
                                'comment_body': comment.body,
                                'comment_score': comment.score,
                                'comment_created_utc': comment_created_utc.strftime('%Y-%m-%d %H:%M:%S'),
                                'comment_replies_count': len(comment.replies),
                                'comment_keyword': keyword,
                                'subreddit': sub,
                            }
                            results.append({**data, **comment_data})

            all_results.extend(results)

    with open(csv_file_path, "w", newline='', encoding='utf-8') as csvfile:
        fieldnames = ['author_name', 'post_id', 'title', 'body', 'post_date', 'keyword', 'comment_author_name', 'comment_id', 'comment_parent_id', 'comment_body', 'comment_score', 'comment_created_utc', 'comment_replies_count', 'comment_keyword', 'subreddit']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

#all subreddits
#get_reddit_data(["Austria", "europe", "Stmk", "wien", "Tirol", "Salzburg", "Vorarlberg", "kaernten", "burgenland", "Noesterreich", "Linz"], ["ÖVP", "SPÖ", "FPÖ", "Grüne", "Neos"], 100, "C:/Stefan/Uni Graz/Master/VU Visual Analytics/austria_politik_posts2.csv", "2019-09-29", "2024-04-29")

get_reddit_data(["Linz"], ["ÖVP", "SPÖ", "FPÖ", "Grüne", "Neos"], None, "subreddits_datafiles\Linz_politik_posts.csv", "2019-09-29", "2024-04-29")

