select student, youtube_id, count(student), video_seconds, video_seconds/count(student) as decimal
  from tbl_clicks, tbl_videos
  where student <> '' and 
        youtube_id <> '' and
        tbl_videos.youtubeid = tbl_clicks.youtube_id and
        student = '0201465580fb6ccae30f93ed67b028f1'
group by student, youtube_id, video_seconds
order by student