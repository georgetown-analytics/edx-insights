SELECT tbl_clicks.course,
       student,
       sum(time_marker) as video_seconds,
       sum(tbl_videos.video_seconds) as seconds_of_video,
       sum(time_marker)/sum(tbl_videos.video_seconds) as Percent_Video_Watched,
       count (*) as click_count,
       sum(CASE
          WHEN event_type = 'seek_video' and split_part(extra,',',2)::numeric - split_part(extra,',',1)::numeric > 0 THEN 1
          ELSE 0
          END) AS Seek_RW_Count,
       sum(CASE
          WHEN event_type = 'seek_video' and split_part(extra,',',2)::numeric - split_part(extra,',',1)::numeric < 0 THEN 1
          ELSE 0
          END) AS Seek_FF_Count,
       sum(CASE
          WHEN event_type = 'seek_video' THEN split_part(extra,',',2)::numeric - split_part(extra,',',1)::numeric ELSE 0
          END) AS Seek_Time_Adjust,
       tbl_videos.week as module,
       CASE WHEN sum(tbl_videos.week) OVER(partition by tbl_clicks.course, student) = 45 AND tbl_clicks.course = 'terrorism' or
                 sum(tbl_videos.week) OVER(partition by tbl_clicks.course, student) = 36 AND tbl_clicks.course = 'genomics' or
                 sum(tbl_videos.week) OVER(partition by tbl_clicks.course, student) = 36 AND tbl_clicks.course = 'genomics2' or
                 sum(tbl_videos.week) OVER(partition by tbl_clicks.course, student) = 21 AND tbl_clicks.course = 'inferno'
                 THEN 1 ELSE 0
                 END AS course_complete
FROM tbl_clicks, tbl_videos
WHERE tbl_clicks.youtube_id = tbl_videos.youtubeid and
      tbl_clicks.youtube_id <> '' and
      tbl_clicks.student <> ''
GROUP BY tbl_clicks.course, student, week