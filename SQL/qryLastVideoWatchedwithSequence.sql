SELECT * 
FROM tbl_clicks WHERE (course,event_time) IN 
( SELECT course, MAX(event_time)
  FROM tbl_clicks
  WHERE student = '0201465580fb6ccae30f93ed67b028f1'
  GROUP BY course, student
)
