from crontab import CronTab

schedule = CronTab(user='pi')
job = schedule.new(command='python /home/pi/server/server.uploader.py', comment='uploader')
job.minute.every(1)

schedule.write()
