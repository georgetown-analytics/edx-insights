#!/usr/bin/python2.7

import psycopg2
import sys
import pprint
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import pylab
import csv
import pandas as pd
from collections import Counter
import csv

def main():
	# define connection string
	conn_string = "host='localhost' dbname = 'dbname' user='postgres' password='password'"

	# print connection string we will use to connect
	print "Connecting to database\n ->%s" % (conn_string)

	# get a connection, if a connection cannot be made an exception will be made here
	conn = psycopg2.connect(conn_string)

	# conn.cursor will return a cursor object, you can use this cursor to perform queries
	cursor = conn.cursor()
	print "Connected!\n"

	# execute our Query
	#cursor.execute("SELECT * FROM students LIMIT 100")
	
	### works when SELECT * FROM db
	#for row in records:
	#	print row[3]

	# returns each row as a separate list
	#pprint.pprint(records)



	### DETERMINE THE NUMBER OF SEEKS PER SECOND OF VIDEO WATCHED PER STUDENT ###
	
	cursor.execute("SELECT count(studentid)	from students")
	num = cursor.fetchone()[0]
	# num = 7675 -- the total number of students in the student db table

	
	length_query = (
		"SELECT clicks.studentid, max(clicks.video_order), video_stats.video_len"
		"	FROM clicks, video_stats"
		"	WHERE clicks.video_order = video_stats.video_order"
		"	GROUP BY clicks.studentid, video_stats.video_len"
		)
	
	cursor.execute(length_query)
	vid_lengths = cursor.fetchall()
	

	v_sum = []
	n = 1
	query = ("select * from lengths where studentid=%s")
	
	while n < num:
		cursor.execute(query, (n,))
		length = cursor.fetchall()
		v_len = np.sum([x[2] for x in length]) 
		v_sum.append([n, v_len])
		n += 1
				
	# export max_course to a .csv
	with open("length_sums.csv", "wb") as f:
		writer = csv.writer(f, delimiter=',') 
		writer.writerow(['studentid', 'len_sum'])
		writer.writerows(v_sum)



	
	### RETURN THE TIMESTAMPS FOR EVERY EVENT_TYPE BY STUDENT ###
	
	times_query = "SELECT count(event_time) from clicks"
	cursor.execute(times_query)
	times = cursor.fetchone()[0]
	# times now equals 1565319

	clicks_query = (
		"SELECT studentid, event_time, video_order, max_video"
		"	FROM clicks"
		"	WHERE studentid <%s"
		"	ORDER BY studentid, event_time, video_order"
		)

	with open("time_of_clicks3.csv", "w") as f:
		writer = csv.writer(f)
		cursor.execute(clicks_query, (times,))
		for row in cursor.fetchall():
			writer.writerow(row)
	

	### BREAK DOWN THE SEEKS BY TYPE (REWIND, FAST FORWARD) AND BY STUDENT ###
	
	seek_query = (
		"SELECT studentid, extra"
		"	FROM clicks"
		"	WHERE event_type='seek_video'"
		"	AND extra is not null"
		)
	cursor.execute(seek_query)
	seeks = cursor.fetchall()
	
	seek_list = []
	count = 0
	for i in seeks:
		time = i[1]
		start = time.split(',')[0]	
		end = time.split(',')[-1]
		delta = float(start) - float(end)
		if delta < 0:
			direction = 'rewind'
		elif delta > 0:
			direction = 'fast forward'
		else:
			direction = 'neutral'
		seek_list.append([i[0], start, end, delta, direction])
		count += 1
	print count

	# export max_course to a .csv
	with open("seek_classification.csv", "wb") as f:
		writer = csv.writer(f, delimiter=',') 
		writer.writerow(['studentid', 'seek_initiated', 'seek_stop', 'seek_delta', 'seek_direction'])
		writer.writerows(seek_list)
	


	### SUM SEEK TYPES BY STUDENT ###
	
	seek_query_neutral = (
		"SELECT studentid, count(seek_direction)"
		"	FROM seek_classification"
		"	WHERE seek_direction='neutral'"
		"	group by studentid"
		"	order by studentid"
		)
	cursor.execute(seek_query_neutral)
	seeks_neutral = cursor.fetchall()

	seek_query_fastforward = (
		"SELECT studentid, count(seek_direction)"
		"	FROM seek_classification"
		"	WHERE seek_direction='fast forward'"
		"	group by studentid"
		"	order by studentid"
		)
	cursor.execute(seek_query_fastforward)
	seeks_fastforward = cursor.fetchall()

	seek_query_rewind = (
		"SELECT studentid, count(seek_direction)"
		"	FROM seek_classification"
		"	WHERE seek_direction='rewind'"
		"	group by studentid"
		"	order by studentid"
		)
	cursor.execute(seek_query_rewind)
	seeks_rewind = cursor.fetchall()


	with open("seek_query_neutral.csv", "wb") as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(['studentid', 'seeks_neutral'])
		writer.writerows(seeks_neutral)

	with open("seek_query_fastforward.csv", "wb") as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(['studentid', 'seeks_fastforward'])
		writer.writerows(seeks_fastforward)

	with open("seek_query_rewind.csv", "wb") as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(['studentid', 'seeks_rewind'])
		writer.writerows(seeks_rewind)
	



	### CALCULATE THE TIME BETWEEN EVENTS FOR EACH STUDENT ... NOT COMPLETED ###
	"""
	t=5
	tm = []


	while t < 7:
		#tm = []
		cursor.execute("SELECT studentid, event_time, event_type FROM clicks \
	 		WHERE studentid=%d ORDER BY studentid, event_time" % (t))
		times = cursor.fetchall()
		
		for tim in times:
			tm.append(tim[1])
		
		print tm
		t+=1
	
	print tm
	#stimes(tm)
	


	conn.commit()
	cursor.close()
	conn.close()

def stimes(tm): 
	length = len(tm)
	print length
	t = 0
	time_lists = []
	while t < length:
		if t == 0:
			t += 1
		elif t == length:
			pass
		else:
			a = tm[t]
			b = tm[t-1]
			a = a.strip('+00:00')	
			b = b.strip('+00:00')
		
			DT_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
			dta = datetime.strptime(a, DT_FORMAT)
			dtb = datetime.strptime(b, DT_FORMAT)
			difference = dta-dtb
			time_lists.append(difference.total_seconds())
			#print difference.total_seconds()
			t += 1
	print time_lists
	"""


	### SQL STATEMENTS TO RETRIEVE VARIOUS RECORDS ###
	
	# length of VIDEOS
	cursor.execute("SELECT video_len FROM video_stats \
		ORDER BY video_order")

	video_len = cursor.fetchall()

	# execute our Query for the number of clicks PER VIDEO
	cursor.execute("SELECT count(event_type), video_order FROM clicks \
		GROUP BY video_order ORDER BY video_order")
	records = cursor.fetchall()

	
	# execute our Query for the number of "pause_video" click events PER VIDEO
	cursor.execute("SELECT count(event_type), video_order FROM clicks \
		WHERE event_type='pause_video' \
		GROUP BY video_order ORDER BY video_order")
	
	# retrieve the pauses from the database
	pauses = cursor.fetchall()

	# execute our Query for the number of clicks PER STUDENT
	cursor.execute("SELECT count(event_type), studentid FROM clicks \
		GROUP BY studentid ORDER BY studentid")

	clicks = cursor.fetchall()
	
	

	# execute our Query to return a single row for student and a video watched 
	# regardless of video completion
	cursor.execute("SELECT studentid, max(video_order) FROM clicks \
		GROUP BY studentid, video_order")

	stud_completion = cursor.fetchall()
	#print stud_completion
	# prints one element for each student and the course: [... (5932,3), (5932,4), (5932,5), ...]
	# so it takes all the multiple records for each student and each course and just has 1 record


	
	### DETERMINE THE MAX VIDEO A STUDENT WATCHED ###
	### takes 42 minutes to crank through ###
	
	# return the total number of students who have watched any part of any video
	cursor.execute("SELECT count(studentid)	from students")
	num_students = cursor.fetchall()
	# returns [(7675,)]
	
	num = num_students[0][0]
	print num
	# prints 7675 -- the total number of students who have one record in the db for clicks
	
	n = 0

	# create an empty list in order to create a new list
	max_video = []
	
	# iterate through each student to find the max course taken
	# does not consider courses that were skipped; only the max
	while n < num:
		
		cursor.execute("SELECT studentid, max(video_order) FROM clicks \
			WHERE studentid=%d GROUP BY studentid, video_order" % (n))
		student_video = cursor.fetchall()
		
		#print student_list
		# prints row by row the studentid and all the videos watched as a list of lists
		# [(56,2), (56,7), (56,1)] 
		# []
		# [(58,1), (58,8), ...] 
		
		# check for empty lists
		if not student_video:
			n += 1
		else: 
			# find max video taken by each student
			max_v = np.max([x[1] for x in student_video]) 
			
			# append the list with student and max video
			max_video.append([student_video[0][0],max_v])
			n += 1
	
	#print max_course

	# export max_course to a .csv
	with open("max_video_completed.csv", "wb") as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerows(max_video)
	
	

	### DETERMINE THE NUMBER OF VIDEOS EACH STUDENT WATCHED ###
	### takes 42 minutes to crank through ###
	
	# return the total number of students who have watched any part of any video
	cursor.execute("SELECT count(studentid)	from students")
	num_students = cursor.fetchall()
	# returns [(7275,)]
	num = num_students[0][0]
	print num
	# prints 7275 -- the total number of students who have one record in the db for clicks
	
	n = 0

	# create an empty list in order to create a new list
	total_videos = []
	
	# iterate through each student 
	while n < num:
		
		cursor.execute("SELECT studentid, max(video_order) FROM clicks \
			WHERE studentid=%d GROUP BY studentid, video_order" % (n))
		student_video = cursor.fetchall()
		# prints row by row the studentid and all the videos with at least one click event as a list of lists
		# [(56,2), (56,7), (56,1)] 
		# []
		# [(58,1), (58,8), ...] 
		
		# check for empty lists
		if not student_video:
			n += 1
		else: 
			# find total videos with at least one click event for each student
			tot_v = np.count_nonzero([x[1] for x in student_video]) 
			
			# append the list with student and total videos
			total_videos.append([student_video[0][0],tot_v, float(tot_v)/89*100])
			n += 1
	
	# export max_course to a .csv
	COLUMNS = [
		'studentid',
		'videos_clicked',
		'percent_clicked',
		]
	with open("videos_by_student.csv", "wb") as f:
		writer = csv.writer(f, delimiter=',') 
		writer.writerows(total_videos)
	

	

	### GATHER BASIC DATA ###

	# total clicks per student
	cursor.execute("SELECT studentid, count(event_type) FROM clicks \
		GROUP BY studentid ORDER BY studentid")
	clicks_by_student = cursor.fetchall()

	with open("clicks_by_student.csv", "wb") as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerows(clicks_by_student)

	cursor.execute("CREATE TABLE clicks_by_student( 	\
		studentid INTEGER PRIMARY KEY, \
		clicks INTEGER \
		) \
		")

	# total play videos per student -- could inform watching shorter durations
	# versus sitting down and going through the videos in less sittings
	cursor.execute("SELECT studentid, count(event_type) FROM clicks \
		WHERE event_type = 'play_video' \
		GROUP BY studentid ORDER BY studentid")
	plays_by_student = cursor.fetchall()

	with open("plays_by_student.csv", "wb") as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerows(plays_by_student)

	cursor.execute("CREATE TABLE plays_by_student( 	\
		studentid INTEGER PRIMARY KEY, \
		plays INTEGER \
		) \
		")


	# total pauses per student -- student distracted?  multitasking?
	cursor.execute("SELECT studentid, count(event_type) FROM clicks \
		WHERE event_type = 'pause_video' \
		GROUP BY studentid ORDER BY studentid")
	pauses_by_student = cursor.fetchall()

	with open("pauses_by_student.csv", "wb") as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerows(pauses_by_student)

	cursor.execute("CREATE TABLE pauses_by_student( 	\
		studentid INTEGER PRIMARY KEY, \
		pauses INTEGER \
		) \
		")
	


	# total SEEKS per student -- student skipping material or rewinding video  
	cursor.execute("SELECT studentid, count(event_type) FROM clicks \
		WHERE event_type = 'seek_video' \
		GROUP BY studentid ORDER BY studentid")
	seeks_by_student = cursor.fetchall()

	with open("seeks_by_student.csv", "wb") as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerows(seeks_by_student)

	cursor.execute("CREATE TABLE seeks_by_student( 	\
		studentid INTEGER PRIMARY KEY, \
		seeks INTEGER \
		) \
		")

	# total SPEED CHANGES per student -- student skipping material?  
	cursor.execute("SELECT studentid, count(event_type) FROM clicks \
		WHERE event_type = 'speed_change_video' \
		GROUP BY studentid ORDER BY studentid")
	seeks_by_student = cursor.fetchall()

	with open("speed_change_by_student.csv", "wb") as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerows(seeks_by_student)

	cursor.execute("CREATE TABLE speed_change_by_student( 	\
		studentid INTEGER PRIMARY KEY, \
		seeks INTEGER \  # named this wrong, should have been speed_changes and not seeks
		) \
		")


	# total video loads per student -- similar to video plays
	cursor.execute("SELECT studentid, count(event_type) FROM clicks \
		WHERE event_type = 'load_video' \
		GROUP BY studentid ORDER BY studentid")
	loads_by_student = cursor.fetchall()

	with open("loads_by_student.csv", "wb") as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerows(loads_by_student)

	cursor.execute("CREATE TABLE loads_by_student( 	\
		studentid INTEGER PRIMARY KEY, \
		loads INTEGER \
		) \
		")

	# total times a student looks at transcript to see progress
	cursor.execute("SELECT studentid, count(event_type) FROM clicks \
		WHERE event_type = 'show_transcript' \
		GROUP BY studentid ORDER BY studentid")
	show_transcript_by_student = cursor.fetchall()

	with open("show_transcript_by_student.csv", "wb") as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerows(show_transcript_by_student)

	cursor.execute("CREATE TABLE show_transcript_by_student( 	\
		studentid INTEGER PRIMARY KEY, \
		transcript INTEGER \
		) \
		")

	
	### DETERMINE THE MODULE ATTAINED BY EACH STUDENT BASED ON THE LAST VIDEO WATCHED ###

	cursor.execute("SELECT max_video, module FROM ml")
	module = cursor.fetchall()

	max_vid = [x[0] for x in module]
	mod = [x[1] for x in module]
	new = []
	
	for i in xrange(len(module)):
		if max_vid[i] == 0:
			new.append([max_vid[i], 0])
		elif max_vid[i] >=1 and max_vid[i] <= 8:
			new.append([max_vid[i], 1])
		elif max_vid[i] >=9 and max_vid[i] <= 14:
			new.append([max_vid[i], 2])
		elif max_vid[i] >=15 and max_vid[i] <= 21:
			new.append([max_vid[i], 3])
		elif max_vid[i] >=22 and max_vid[i] <= 36:
			new.append([max_vid[i], 4])
		elif max_vid[i] >=37 and max_vid[i] <= 51:
			new.append([max_vid[i], 5])
		elif max_vid[i] >=52 and max_vid[i] <= 67:
			new.append([max_vid[i], 6])
		elif max_vid[i] >=68 and max_vid[i] <= 78:
			new.append([max_vid[i], 7])
		elif max_vid[i] >=79 and max_vid[i] <= 88:
			new.append([max_vid[i], 8])		
	print new	

	with open("module_by_student.csv", "wb") as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerows(new)


	conn.commit()
	cursor.close()
	conn.close()

	
	# returns each row as a separate list
	#pprint.pprint(records)
	
	
	### BASIC STATISTICS ###
	
	# calculate sum, min, max, mean, median for clicks PER VIDEO
	sum_value(records)
	min_value(records)
	max_value(records)
	mean_value(records)
	median_value(records)
	
	# and again, but now PER STUDENT
	sum_value(clicks)
	min_value(clicks)
	max_value(clicks)
	mean_value(clicks)
	median_value(clicks)


	### GENERATE VISUALIZATIONS ###
	graph_student_clicks(clicks)
	graph_pauses(pauses, video_len)
	graph_clicks(records, video_len)
	graph_max_video_completion(max_video)
	


def graph_max_video_completion(max_video):
	data =  max_video
	# x_val is the max video completed
	x_val = [x[1] for x in data]
	# y_val is the student
	y_val = [x[0] for x in data]

	plt.scatter(x_val, y_val)
	plt.show()

	
def graph_student_clicks(clicks):
	clicks_video, student = zip(*clicks)
	clicks_video = [x[0] for x in clicks]
	divisor = 93
	resize_clicks_video = [x/divisor for x in clicks_video]

	N = len(student) 

	x = np.random.rand(N)
	y = np.random.rand(N)
	colors = np.random.rand(N)
	#area = np.pi * (15 * ([x[0] for x in b]))**2
	#area = np.pi * (15 * np.random.rand(N))**2  # 0 to 15 point radiuses

	plt.scatter(x, y, s=resize_clicks_video, c=colors, alpha=0.5)
	plt.show()


def graph_pauses(pauses, video_len):
	count, video_order = zip(*pauses)
	#print count, video_order
	tick_positions = len(video_order) 
	count_pauses = [x[0] for x in pauses]
	videoid_labels = [x[1] for x in pauses]
	vid_len = [x[0] for x in video_len]
	
	#normalize: pauses per length of video
	normalize = [1.0*count_pauses[n]/vid_len[n] for n in xrange(len(vid_len))]

	N = tick_positions
	index = np.arange(N)
	bar_width = 0.35
	opacity = 0.4
	error_config = {'ecolor': '0.3'}
	axis_font = {'size':'10'}
	plt.bar(index, normalize, bar_width,
		alpha = opacity,
		color = 'b',
		error_kw = error_config,
		label = 'Event_Count'
		)

	plt.xlabel("Video")
	plt.ylabel("Number of Pauses/Sec of Video")
	plt.title("Number of Pauses/Second of Video for each Genomics Video")
	plt.xticks(index + bar_width, videoid_labels, rotation='vertical', **axis_font)
	plt.grid()
	plt.legend()
	plt.tight_layout()
	plt.show()


def graph_clicks(records, video_len):
	count, video = zip(*records)
	tick_positions = len(video) 
	count_events = [x[0] for x in records]
	video_labels = [x[1] for x in records]
	vid_len = [x[0] for x in video_len]

	# normalize: clicks per length of video
	normalize = [1.0*count_events[n]/vid_len[n] for n in xrange(len(vid_len))]
	
	N = tick_positions
	index = np.arange(N)
	bar_width = 0.35
	opacity = 0.4
	error_config = {'ecolor': '0.3'}
	axis_font = {'size':'10'}
	plt.bar(index, normalize, bar_width,
		alpha = opacity,
		color = 'b',
		error_kw = error_config,
		label = 'Event_Count'
		)

	plt.xlabel("Video")
	plt.ylabel("Number of Clicks/Sec of Video")
	plt.title("Number of Clicks/Second of Video for each Genomics Video")
	plt.xticks(index + bar_width, video_labels, rotation='vertical', **axis_font)
	plt.grid()
	plt.legend()
	plt.tight_layout()
	plt.show()


def sum_value(records):
	sum = np.sum([x[0] for x in records])
	"""
	sum = 0        
	for i in records:
		sum += i[0]
	"""
	print "sum is equal to: ", sum
	return sum 


def min_value(records):
	min = 10
	# loop through the list of tuple objects
	for i in records:
		# compare the 0th element in each row
		if i[0] < min:
			# min is updated only if i[0] is smaller than min
			min = i[0] 
	print "min is equal to: ", min
	return min


def max_value(records):
	max = 0
	# loop through the list of tuple objects
	for i in records:
		# compare the 0th element in each row
		if i[0] > max:
			# max is updated only if i[0] is larger than max
			max = i[0] 
	print "max is equal to: ", max
	return max


def mean_value(records):
	mean = np.mean([x[0] for x in records])
	print "mean is equal to: ", mean
	return mean


def median_value(records):
	median = np.median([x[0] for x in records])
	print "median is equal to: ", median
	return median
 
	


if __name__ == "__main__":
	main()
	
