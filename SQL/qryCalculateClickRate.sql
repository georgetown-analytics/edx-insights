SELECT student,
       tbl_videos.course,
       count(*) as numclicks,
       youtube_id,
       video_seconds,
       video_order,
       video_seconds/count(*) as rate,
       tbl_videos.week
FROM tbl_clicks, tbl_videos
WHERE student = '0466005eeb50ea5f1880f5a9bdea7078' and
      tbl_clicks.youtube_id = tbl_videos.youtubeid
GROUP BY student, tbl_videos.course, youtube_id, video_seconds, video_order, tbl_videos.week
ORDER BY tbl_videos.course, video_order