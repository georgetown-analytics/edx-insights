SELECT student,
       tbl_clicks.course,
       sum(tbl_videos.week) over(partition by tbl_clicks.course, student) as total_course_modules,
       count(tbl_clicks.youtube_id) OVER(partition by tbl_clicks.course, student) as video_count_for_course,
       count(tbl_clicks.clickid) as click_count_for_video,
       sum(tbl_videos.video_seconds) OVER(PARTITION by tbl_clicks.youtube_id, student) as seconds_for_video,
   CASE WHEN sum(tbl_videos.week) OVER(partition by tbl_clicks.course, student) = 45 AND tbl_clicks.course = 'terrorism' or
             sum(tbl_videos.week) OVER(partition by tbl_clicks.course, student) = 36 AND tbl_clicks.course = 'genomics' or
             sum(tbl_videos.week) OVER(partition by tbl_clicks.course, student) = 36 AND tbl_clicks.course = 'genomics2' or
             sum(tbl_videos.week) OVER(partition by tbl_clicks.course, student) = 21 AND tbl_clicks.course = 'inferno'
        THEN 1 ELSE 0     
   END as is_complete,
   CASE WHEN tbl_clicks.course = 'terrorism' THEN 141
        WHEN tbl_clicks.course = 'genomics' THEN 89
        WHEN tbl_clicks.course = 'genomics2' THEN 87
        WHEN tbl_clicks.course = 'inferno' THEN 6
        ELSE 0
   END as course_videos
   FROM tbl_clicks, tbl_videos
   WHERE tbl_clicks.youtube_id = tbl_videos.youtubeid and
         student = '0201465580fb6ccae30f93ed67b028f1'
   GROUP BY student, tbl_clicks.course, tbl_videos.week, tbl_clicks.youtube_id, tbl_videos.video_seconds
   ORDER BY student, course
