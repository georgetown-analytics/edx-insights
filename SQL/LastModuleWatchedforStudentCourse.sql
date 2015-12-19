SELECT student,
       tbl_clicks.course,
       sum(tbl_videos.week) over(partition by tbl_clicks.course, student) as total_modules,
       tbl_videos.week as module,
       sum(tbl_videos.video_seconds) as seconds_watched,
   CASE WHEN sum(tbl_videos.week) OVER(partition by tbl_clicks.course, student) = 45 AND tbl_clicks.course = 'terrorism' or
             sum(tbl_videos.week) OVER(partition by tbl_clicks.course, student) = 36 AND tbl_clicks.course = 'genomics' or
             sum(tbl_videos.week) OVER(partition by tbl_clicks.course, student) = 36 AND tbl_clicks.course = 'genomics2' or
             sum(tbl_videos.week) OVER(partition by tbl_clicks.course, student) = 21 AND tbl_clicks.course = 'inferno'
        THEN 1 ELSE 0     
   END as is_complete,
   CASE WHEN tbl_clicks.course = 'terrorism' THEN 50427
        WHEN tbl_clicks.course = 'genomics' THEN 41928
        WHEN tbl_clicks.course = 'genomics2' THEN 34117
        WHEN tbl_clicks.course = 'inferno' THEN 1898
        ELSE 0
   END as course_seconds  
   FROM tbl_clicks, tbl_videos
   WHERE tbl_clicks.youtube_id = tbl_videos.youtubeid   
   GROUP BY student, tbl_clicks.course, tbl_videos.week
   ORDER BY student, course, module
